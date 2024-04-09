import os
from pydantic import BaseModel, ValidationError, model_validator, root_validator
from functools import cached_property
from typing import Union


class Table(BaseModel):
    type: str
    rows: list[list[str]]


class Text(BaseModel):
    type: str
    value: str
    md: str


class Heading(BaseModel):
    type: str
    lvl: int
    value: str
    md: str


class Image(BaseModel):
    name: str
    height: int
    width: int
    x: int
    y: int


class Page(BaseModel):
    page: int
    text: str
    md: str
    items: list[Union[Table, Heading, Text]]


class PDFJson(BaseModel):
    pages: list[Page]
    job_id: str
    file_path: str

    @cached_property
    def full_md(self) -> str:
        return "\n\n".join([page.md for page in self.pages])

    @cached_property
    def basename(self) -> str:
        return os.path.basename(self.file_path)

    @classmethod
    def from_json_file(cls, file_path: str):
        import json

        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                return cls(**data)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}.")
            return None


if __name__ == "__main__":
    pdf_json = PDFJson.from_json_file("./parse-output/2302.01381.json")
    print(pdf_json.model_dump_json(indent=4))
