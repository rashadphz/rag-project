import asyncio
import glob
import os
from typing import AsyncIterator, Iterator, List

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index_client import ChatMessage
from qdrant_client import QdrantClient
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.postprocessor.voyageai_rerank import VoyageAIRerank
from llama_index.llms.openai import OpenAI
from llama_index.core.schema import BaseNode
import voyageai
from schemas import RelatedSchema, Source, SourceResponse, TextChunk, FollowUpQuestions
from llama_index.core.prompts import PromptTemplate

OPENAI_EMBEDDINGS_MODEL = "text-embedding-3-small"
GPT3_MODEL = "gpt-3.5-turbo"
GPT4_MODEL = "gpt-4-turbo-preview"

from dotenv import load_dotenv

load_dotenv()

USE_CITATIONS = """
MAKE SURE to Cite relevant statements INLINE using the format [1], [2], [3], etc to reference the document number, \
DO NOT provide any links following the citations. DO NOT add a reference section at the end.
""".rstrip()

CHAT_PROMPT = """\
You are a professional research assistant. For each user question, use the context to their fullest potential to answer the question. Directly answer the question, and augment the response with insights from the context. If LaTeX is needed in the answer, make sure to render it correctly within a LaTeX block with either inline or block formatting ($content$ or $$content$$).

{use_citations}
---------------------
{my_context}
---------------------
Query: {my_query}
Answer: \
"""

HISTORY_QUERY_REPHRASE = f"""
Given the following conversation and a follow up input, rephrase the follow up into a SHORT, \
standalone query (which captures any relevant context from previous messages) for a vectorstore.
IMPORTANT: EDIT THE QUERY TO BE AS CONCISE AS POSSIBLE. Respond with a short, compressed phrase \
with mainly keywords instead of a complete sentence.
If there is a clear change in topic, disregard the previous messages.
Strip out any information that is not relevant for the retrieval task.
If the follow up message is an error or code snippet, repeat the same input back EXACTLY.

Chat History:
{{chat_history}}

Follow Up Input: {{question}}
Standalone question (Respond with only the short combined query):
""".strip()


client = QdrantClient(
    url="https://86913b95-6060-4686-8047-7bae2fbd8541.us-east4-0.gcp.cloud.qdrant.io",
    api_key=os.getenv("QDRANT_API_KEY"),
)
vector_store = QdrantVectorStore(
    client=client, collection_name="big-collection", batch_size=30
)

embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_MODEL)
vo = voyageai.Client(api_key=os.getenv("VOYAGEAI_API_KEY"))


def source_from_node(node: BaseNode) -> Source:
    for header in ["Header_3", "Header_2", "Header_1"]:
        if heading := node.metadata.get(header):
            break
    else:
        heading = ""
    return Source(filename=node.metadata.get("filename", ""), heading=heading)


def rephrase_query_with_history(
    question: str, history: List[ChatMessage], llm: OpenAI
) -> str:
    if history:
        history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in history])
        return llm.complete(
            HISTORY_QUERY_REPHRASE.format(chat_history=history_str, question=question)
        ).text
    return question


async def stream_chat_message_objects(
    question: str, history: List[ChatMessage]
) -> AsyncIterator[SourceResponse | TextChunk | FollowUpQuestions]:

    llm = OpenAI(model=GPT4_MODEL)

    question = rephrase_query_with_history(question, history, llm)
    related_queries_task = asyncio.create_task(generate_related_queries(question))

    embedding = embeddings.embed_query(question)

    query = VectorStoreQuery(
        query_embedding=embedding,
        similarity_top_k=30,
    )

    # Sources
    top_nodes = vector_store.query(query).nodes or []

    node_texts = [node.get_content(metadata_mode="all") for node in top_nodes]

    rerank_result = vo.rerank(question, node_texts, model="rerank-lite-1", top_k=8)
    reranked_nodes: List[BaseNode] = [
        top_nodes[item.index] for item in rerank_result.results
    ]

    top_sources = [source_from_node(node) for node in reranked_nodes]
    yield SourceResponse(top_sources=top_sources)

    # Chat
    context_str = "\n\n".join(
        [
            f"{index + 1}. {node.get_content(metadata_mode='all')}"
            for index, node in enumerate(reranked_nodes)
        ]
    )
    fmt_qa_prompt = CHAT_PROMPT.format(
        use_citations=USE_CITATIONS, my_context=context_str, my_query=question
    )
    for completion in llm.stream_complete(fmt_qa_prompt):
        yield TextChunk(text=completion.delta or "")

    related_queries = await related_queries_task
    questions = [item.query for item in related_queries.queries]
    yield FollowUpQuestions(questions=questions)


async def generate_related_queries(question: str) -> RelatedSchema:
    llm = OpenAI(model=GPT3_MODEL)
    prompt = PromptTemplate(
        """
        You are a professional researcher. Your task is to generate three related queries that explore a subject matter more deeply, building on the original query and information discovered in its search results.

        For example, if the original query is "How do local balanced samplers in generative models compare in terms of sample quality and diversity?" your queries could be:

        What are some examples of local balanced samplers in generative models?
        How do local balanced samplers compare to other types of samplers in generative models?
        What are some advantages and disadvantages of using local balanced samplers in generative models?

        Try to make queries that dive deeper into the subject matter, implications or similar topics related to the initial query. The goal is to predice the user's potential information needs. Keep the queries short and concise.

        The user's original query is: {original_query}
        """
    )
    return await llm.astructured_predict(
        output_cls=RelatedSchema, prompt=prompt, original_query=question
    )


async def main():
    res = await generate_related_queries(
        "How does the performance of GSL algorithms change when random feature noise is injected into the graph structures of Cora and Citeseer?"
    )
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
