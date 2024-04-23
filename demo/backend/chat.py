import asyncio
import datetime
import glob
import os
from typing import AsyncIterator, Iterator, List
import wandb

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index_client import ChatMessage
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.postprocessor.voyageai_rerank import VoyageAIRerank
from llama_index.llms.openai import OpenAI
from llama_index.core.schema import BaseNode
import voyageai
from schemas import (
    RelatedSchema,
    SQLEvent,
    Source,
    SourceResponse,
    TextChunk,
    FollowUpQuestions,
)
from llama_index.core.prompts import PromptTemplate
from prompts import USE_CITATIONS, CHAT_PROMPT, HISTORY_QUERY_REPHRASE
from llama_index.core.tools import FunctionTool, ToolMetadata
from llama_index.core.selectors import LLMSingleSelector
from sql import ask_sql_query
from prompts import SQL_RESPONSE_SYNTHESIS_PROMPT
from wandb.sdk.data_types.trace_tree import Trace


import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

wandb.init(project="ifml-rag")


OPENAI_EMBEDDINGS_MODEL = "text-embedding-3-small"
GPT3_MODEL = "gpt-3.5-turbo"
GPT4_MODEL = "gpt-4-turbo"

from dotenv import load_dotenv

load_dotenv()
print(os.environ.get("DATABASE_URL"))


client = QdrantClient(
    url="https://86913b95-6060-4686-8047-7bae2fbd8541.us-east4-0.gcp.cloud.qdrant.io",
    api_key=os.getenv("QDRANT_API_KEY"),
)
vector_store = QdrantVectorStore(
    client=client, collection_name="big-collection-fixed", batch_size=30
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


async def stream_qa_objects(
    question: str, trace_parent: Trace = None
) -> AsyncIterator[SourceResponse | TextChunk]:
    llm = OpenAI(model=GPT4_MODEL)
    embedding = embeddings.embed_query(question)

    query = VectorStoreQuery(
        query_embedding=embedding,
        similarity_top_k=30,
    )

    retrieval_start_ms = now_ms()
    top_nodes = vector_store.query(query).nodes or []

    retrieval_span = Trace(
        name="retrieval",
        start_time_ms=retrieval_start_ms,
        end_time_ms=now_ms(),
        inputs={"question": question},
        outputs={
            "nodes": [node.get_content(metadata_mode="all") for node in top_nodes]
        },
    )
    trace_parent.add_child(retrieval_span)

    node_texts = [node.get_content(metadata_mode="all") for node in top_nodes]

    rerank_result = vo.rerank(question, node_texts, model="rerank-lite-1", top_k=8)

    reranked_nodes: List[BaseNode] = [
        top_nodes[item.index] for item in rerank_result.results
    ]

    rerank_span = Trace(
        name="rerank",
        start_time_ms=retrieval_span.end_time_ms,
        end_time_ms=now_ms(),
        inputs={"nodes": node_texts},
        outputs={
            "reranked_nodes": [
                node.get_content(metadata_mode="all") for node in reranked_nodes
            ]
        },
    )
    trace_parent.add_child(rerank_span)

    top_sources = [source_from_node(node) for node in reranked_nodes]
    yield SourceResponse(top_sources=top_sources)
    logging.info("Finished Reranking Sources")

    # Chat
    context_str = "\n\n".join(
        [
            f"Citation {index + 1}. {node.get_content(metadata_mode='all')}"
            for index, node in enumerate(reranked_nodes)
        ]
    )
    fmt_qa_prompt = CHAT_PROMPT.format(
        use_citations=USE_CITATIONS, my_context=context_str, my_query=question
    )
    logging.info(f"Beginning Text Stream: {fmt_qa_prompt}")
    final_answer = ""
    for completion in llm.stream_complete(fmt_qa_prompt):
        final_answer += completion.delta or ""
        yield TextChunk(text=completion.delta or "")

    answer_span = Trace(
        name="answer",
        start_time_ms=rerank_span.end_time_ms,
        end_time_ms=now_ms(),
        outputs={"answer": final_answer},
    )
    trace_parent.add_child(answer_span)

    logging.info(f"Final Answer: {final_answer}")


async def stream_sql_query(
    question: str, trace_parent: Trace = None
) -> AsyncIterator[TextChunk | SQLEvent]:
    yield SQLEvent(event_type="start")

    llm = OpenAI(model=GPT4_MODEL)

    start_sql_ms = now_ms()
    sql_result = ask_sql_query(question)
    sql_span = Trace(
        name="sql",
        start_time_ms=start_sql_ms,
        end_time_ms=now_ms(),
        inputs={"question": question},
        outputs={
            "sql_query": sql_result.sql_query,
            "sql_response_str": sql_result.sql_response_str,
        },
    )
    trace_parent.add_child(sql_span)

    fmt_sql_response_prompt = SQL_RESPONSE_SYNTHESIS_PROMPT.format(
        query_str=question,
        sql_query=sql_result.sql_query,
        context_str=sql_result.sql_response_str,
    )
    yield SQLEvent(event_type="end")
    final_answer = ""
    for completion in llm.stream_complete(fmt_sql_response_prompt):
        final_answer += completion.delta or ""
        yield TextChunk(text=completion.delta or "")

    answer_span = Trace(
        name="answer",
        start_time_ms=sql_span.end_time_ms,
        end_time_ms=now_ms(),
        outputs={"answer": final_answer},
    )
    trace_parent.add_child(answer_span)


sql_tool_metadata = ToolMetadata(
    name="sql",
    description="Useful for translating natural language into a SQL query over a table containing the following information about research papers: title, keywords / topics / categories, authors, author affiliations. These questions often involve known entities, direct database-related questions, or aggregation-related questions.",
)

retrieval_tool_metadata = ToolMetadata(
    name="retrieval",
    description="Useful for answering questions about research paper content that involves broader information gathering or when the question is more exploratory.",
)


def select_tool(question: str) -> ToolMetadata:
    llm = OpenAI(model=GPT4_MODEL)
    choices = [sql_tool_metadata, retrieval_tool_metadata]
    selector = LLMSingleSelector.from_defaults(llm=llm)
    selections = selector.select(
        choices=choices,
        query=question,
    )

    index = selections.ind
    tool = choices[index]
    return tool


def now_ms() -> int:
    return round(datetime.datetime.now().timestamp() * 1000)


async def stream_chat_message_objects(
    orig_question: str, history: List[ChatMessage]
) -> AsyncIterator[SourceResponse | TextChunk | FollowUpQuestions]:
    root_span = Trace(
        name="chat",
        kind="agent",
        start_time_ms=now_ms(),
        inputs={
            "original_question": orig_question,
            "history": [msg.json() for msg in history],
        },
    )

    logging.info(f"Original Question: {orig_question}")
    llm = OpenAI(model=GPT4_MODEL)

    question = rephrase_query_with_history(orig_question, history, llm)
    rephrase_span = Trace(
        name="rephrase",
        start_time_ms=root_span.start_time_ms,
        end_time_ms=now_ms(),
        inputs={"original_question": orig_question},
        outputs={"rephrased_question": question},
    )
    root_span.add_child(rephrase_span)

    logging.info(f"Rephrase Question: {question}")
    related_queries_task = asyncio.create_task(generate_related_queries(question))

    tool = select_tool(question)
    tool_span = Trace(
        name="select-tool",
        start_time_ms=rephrase_span.end_time_ms,
        end_time_ms=now_ms(),
        inputs={"question": question},
        outputs={"tool": tool.name},
    )
    root_span.add_child(tool_span)

    logging.info(f"Selected tool: {tool.name}")
    final_answer = ""
    if tool == sql_tool_metadata:
        async for step in stream_sql_query(question, trace_parent=root_span):
            final_answer += step.text if isinstance(step, TextChunk) else ""
            yield step
    elif tool == retrieval_tool_metadata:
        async for step in stream_qa_objects(question, trace_parent=root_span):
            final_answer += step.text if isinstance(step, TextChunk) else ""
            yield step

    related_queries = await related_queries_task
    questions = [item.query for item in related_queries.queries]
    yield FollowUpQuestions(questions=questions)

    root_span.end_time_ms = now_ms()
    root_span.add_inputs_and_outputs(
        inputs={},
        outputs={
            "final_answer": final_answer,
            "tool": tool.name,
            "rephrased_question": question,
            "related_queries": [item.query for item in related_queries.queries],
        },
    )
    root_span.log(name="chat-trace")


async def generate_related_queries(question: str) -> RelatedSchema:
    llm = OpenAI(model=GPT4_MODEL)
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
    q1 = "Which papers did dimakis write?"
    tool = select_tool(q1)
    assert tool.name == "sql"

    q2 = "Conditional Generative Model in Total Variation Details"
    tool = select_tool(q2)
    assert tool.name == "retrieval"

    q3 = "Dimakis publications"
    tool = select_tool(q3)
    assert tool.name == "sql"

    q4 = "Dimakis oldest publication"
    tool = select_tool(q4)
    assert tool.name == "sql"


if __name__ == "__main__":
    asyncio.run(main())
