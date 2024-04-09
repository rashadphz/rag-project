import asyncio
import glob
import os
from typing import Iterator, List

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.postprocessor.voyageai_rerank import VoyageAIRerank
from llama_index.llms.openai import OpenAI
from llama_index.core.schema import BaseNode
import voyageai
from schemas import Source, SourceResponse, TextChunk, FollowUpQuestions

OPENAI_EMBEDDINGS_MODEL = "text-embedding-3-small"
# GPT4_MODEL = "gpt-4-turbo-preview"
GPT4_MODEL = "gpt-3.5-turbo"

from dotenv import load_dotenv

load_dotenv()

qa_prompt = """\
You are an expert at answering questions about research papers.
---------------------
{my_context}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {my_query}
Answer: \
"""

client = QdrantClient(
    url="https://86913b95-6060-4686-8047-7bae2fbd8541.us-east4-0.gcp.cloud.qdrant.io",
    api_key=os.getenv("QDRANT_API_KEY"),
)
vector_store = QdrantVectorStore(
    client=client, collection_name="test-collection", batch_size=30
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


def stream_chat_message_objects(
    question: str,
) -> Iterator[SourceResponse | TextChunk | FollowUpQuestions]:
    embedding = embeddings.embed_query(question)

    query = VectorStoreQuery(
        query_embedding=embedding,
        similarity_top_k=15,
    )

    # Sources
    top_nodes = vector_store.query(query).nodes or []

    node_texts = [node.get_content(metadata_mode="all") for node in top_nodes]

    rerank_result = vo.rerank(question, node_texts, model="rerank-lite-1", top_k=5)
    reranked_nodes: List[BaseNode] = [
        top_nodes[item.index] for item in rerank_result.results
    ]

    top_sources = [source_from_node(node) for node in reranked_nodes]
    yield SourceResponse(top_sources=top_sources)

    # Chat
    llm = OpenAI(model=GPT4_MODEL)
    context_str = "\n\n".join(
        [node.get_content(metadata_mode="all") for node in reranked_nodes]
    )
    fmt_qa_prompt = qa_prompt.format(my_context=context_str, my_query=question)
    for completion in llm.stream_complete(fmt_qa_prompt):
        yield TextChunk(text=completion.delta or "")

    yield FollowUpQuestions(
        questions=[
            "this is a test?",
            "this is another test?",
            "and this is a third test?",
        ]
    )
