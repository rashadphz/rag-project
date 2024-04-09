import asyncio
import glob
import os
from typing import List

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from llama_index.core import Document, StorageContext
from llama_index.core.node_parser import MarkdownElementNodeParser, MarkdownNodeParser
from llama_index.vector_stores.qdrant import QdrantVectorStore
from parse_json import PDFJson
from qdrant_client import QdrantClient
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.postprocessor.voyageai_rerank import VoyageAIRerank
from llama_index.llms.openai import OpenAI
from llama_index.core.schema import BaseNode


import voyageai


from constants import GPT4_MODEL, OPENAI_EMBEDDINGS_MODEL


qa_prompt = """\
You are an expert at answering questions about research papers.
---------------------
{my_context}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {my_query}
Answer: \
"""


load_dotenv()
client = QdrantClient(
    url="https://86913b95-6060-4686-8047-7bae2fbd8541.us-east4-0.gcp.cloud.qdrant.io",
    api_key=os.getenv("QDRANT_API_KEY"),
)
vector_store = QdrantVectorStore(
    client=client, collection_name="test-collection", batch_size=30
)

embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_MODEL)
vo = voyageai.Client(api_key=os.getenv("VOYAGEAI_API_KEY"))


if __name__ == "__main__":
    # question = "What does the assumption of single-policy concentrability for \(\pi^*_\alpha\) entail in the context of reinforcement learning or decision-making models?"
    # question = "How does the performance of GSL algorithms change when random feature noise is injected into the graph structures of Cora and Citeseer?	"

    question = "How do local balanced samplers in generative models compare in terms of sample quality and diversity, specifically in the context of RBM training results and a text filling task on BERT?"
    embedding = embeddings.embed_query(question)

    query = VectorStoreQuery(
        query_embedding=embedding,
        similarity_top_k=15,
    )
    top_nodes = vector_store.query(query).nodes or []

    node_texts = [node.get_content(metadata_mode="all") for node in top_nodes]
    rerank_result = vo.rerank(question, node_texts, model="rerank-lite-1", top_k=5)

    reranked_nodes: List[BaseNode] = [
        top_nodes[item.index] for item in rerank_result.results
    ]

    llm = OpenAI(model=GPT4_MODEL)
    context_str = "\n\n".join(
        [node.get_content(metadata_mode="all") for node in reranked_nodes]
    )

    fmt_qa_prompt = qa_prompt.format(my_context=context_str, my_query=question)
    response = llm.complete(fmt_qa_prompt)
    print(response)
