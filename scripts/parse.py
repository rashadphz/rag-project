import asyncio
import nest_asyncio
from llama_parse import LlamaParse
import os
from dotenv import load_dotenv
import json
import glob

load_dotenv()

nest_asyncio.apply()


os.environ["LLAMA_CLOUD_API_KEY"] = os.getenv("LLAMA_CLOUD_API_KEY")

parsing_instruction = """The provided document includes both text and math equations.
Output any math equation in LATEX markdown, using $$ at the start and end of the LATEX.
Any table in the document needs to preserve markdown structure."""

parser = LlamaParse(verbose=True, parsing_instruction=parsing_instruction)


async def parse_pdf_and_save(file_path: str, output_path: str):
    print(f"Parsing {file_path}, saving to {output_path}")
    try:
        json_objs = await parser.aget_json(file_path)
        with open(output_path, "w") as f:
            json.dump(json_objs[0], f)
        print(f"Saved {output_path}")
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")


def get_unparsed_files(input_dir: str, parsed_dir: str):
    input_files = glob.glob(f"{input_dir}/*.pdf")
    parsed_files = glob.glob(f"{parsed_dir}/*.json")
    parsed_basenames = [os.path.basename(f).replace(".json", "") for f in parsed_files]
    return [
        file
        for file in input_files
        if os.path.basename(file).replace(".pdf", "") not in parsed_basenames
    ]


async def main():
    files_to_parse = get_unparsed_files(
        input_dir="./corpus", parsed_dir="./parse-output"
    )

    tasks = []
    for file in files_to_parse:
        basename = os.path.basename(file).replace(".pdf", "")
        output_path = f"./parse-output/{basename}.json"
        tasks.append(parse_pdf_and_save(file, output_path))

    if tasks:
        await asyncio.gather(*tasks)
    else:
        print("No new files to parse.")


if __name__ == "__main__":
    asyncio.run(main())
