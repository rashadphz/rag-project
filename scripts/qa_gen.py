import nest_asyncio
from datasets import Dataset, load_from_disk
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.testset.evolutions import multi_context, reasoning, simple
from ragas.testset.generator import TestsetGenerator

from constants import GPT3_MODEL, GPT4_MODEL, OPENAI_EMBEDDINGS_MODEL
from parse_json import PDFJson
from llama_index.core import Document


load_dotenv()

nest_asyncio.apply()

generator_llm = ChatOpenAI(model=GPT3_MODEL)
critic_llm = ChatOpenAI(model=GPT4_MODEL)
embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_MODEL)


generator = TestsetGenerator.from_langchain(
    generator_llm,
    critic_llm,
    embeddings,
)

distributions = {simple: 0.5, multi_context: 0.4, reasoning: 0.1}


if __name__ == "__main__":
    pdf_json = PDFJson.from_json_file("./parse-output/2302.01381.json")
    pdf_md = pdf_json.full_md

    index_docs = [
        Document(
            metadata={"pdf_path": pdf_json.file_path, "pdf_id": pdf_json.job_id},
            text=pdf_md,
        )
    ]

    testset = generator.generate_with_llamaindex_docs(
        index_docs,
        test_size=3,
        distributions=distributions,
        with_debugging_logs=True,
    )

    testset.to_dataset().save_to_disk("questions")
    test_df = testset.to_pandas()
    test_df.head()

    # dataset = load_from_disk("../questions")
    # test_df = dataset.to_pandas()
    # test_df.to_csv("generated_questions.csv", index=False)
    # print("Questions saved to generated_questions.csv")
