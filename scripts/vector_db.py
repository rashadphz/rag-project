import nest_asyncio
from constants import GPT3_MODEL, GPT4_MODEL, OPENAI_EMBEDDINGS_MODEL
from datasets import Dataset, load_from_disk
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from llama_index.core import Document
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from parse_json import PDFJson
from qdrant_client import QdrantClient
from ragas.testset.evolutions import multi_context, reasoning, simple
from ragas.testset.generator import TestsetGenerator
from llama_index.core import StorageContext
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.llms.openai import OpenAI


load_dotenv()

nest_asyncio.apply()

embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_MODEL)


client = QdrantClient(path="../qdrant-vector-store")
vector_store = QdrantVectorStore(client=client, collection_name="test-collection")
storage_context = StorageContext.from_defaults(vector_store=vector_store)


if __name__ == "__main__":

    node_parser = MarkdownElementNodeParser(llm=OpenAI(model=GPT3_MODEL), num_workers=8)

    pdf_json = PDFJson.from_json_file("./parse-output/2302.01381.json")
    pdf_md = pdf_json.full_md
    documents = [
        Document(
            metadata={"pdf_path": pdf_json.file_path, "pdf_id": pdf_json.job_id},
            text=pdf_md,
        )
    ]
    nodes = node_parser.get_nodes_from_documents([documents])
    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)

    index = VectorStoreIndex.build_index_from_nodes(
        nodes=base_nodes + objects, storage_context=storage_context
    )

    print(index)
