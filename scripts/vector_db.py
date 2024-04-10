import asyncio
import glob
import os
from typing import List

from constants import OPENAI_EMBEDDINGS_MODEL
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from llama_index.core import Document, StorageContext
from llama_index.core.node_parser import MarkdownElementNodeParser, MarkdownNodeParser
from llama_index.vector_stores.qdrant import QdrantVectorStore
from parse_json import PDFJson
from qdrant_client import QdrantClient

load_dotenv()


client = QdrantClient(
    url="https://86913b95-6060-4686-8047-7bae2fbd8541.us-east4-0.gcp.cloud.qdrant.io",
    api_key=os.getenv("QDRANT_API_KEY"),
)
vector_store = QdrantVectorStore(
    client=client, collection_name="big-collection", batch_size=30
)


def clear_vector_store(vector_store: QdrantVectorStore):
    client: QdrantClient = vector_store.client
    client.delete_collection(collection_name=vector_store.collection_name)


def get_documents(folder_path: str) -> List[Document]:
    parsed_files = glob.glob(f"{folder_path}/*.json")
    pdf_jsons = [PDFJson.from_json_file(f) for f in parsed_files]


    return [
        Document(
            metadata={"filename": pdf_json.basename, "title": pdf_json.title},
            text=pdf_json.full_md,
        )
        for pdf_json in pdf_jsons
    ]


from langchain_openai import OpenAIEmbeddings

embedder = OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_MODEL)


async def main():
    node_parser = MarkdownNodeParser()
    nodes = node_parser.get_nodes_from_documents(get_documents("./parse-output"))

    print(f"Embedding {len(nodes)} nodes...")
    embeddings = await embedder.aembed_documents(
        [node.get_content(metadata_mode="all") for node in nodes]
    )
    print(f"Embedded {len(nodes)} nodes...")

    for node, embedding in zip(nodes, embeddings):
        node.embedding = embedding

    res = vector_store.add(nodes)
    # print(res)


if __name__ == "__main__":
    asyncio.run(main())

    # TODO: This one parses tables an their summaries (probably better)
    # node_parser = MarkdownElementNodeParser(llm=OpenAI(model=GPT3_MODEL), num_workers=8)
