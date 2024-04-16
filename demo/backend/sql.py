from dataclasses import dataclass
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from llama_index.llms.openai import OpenAI
from llama_index.core.prompts import PromptTemplate

from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core import SQLDatabase


import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

TEXT_TO_SQL_TMPL = """
    You are an expert at writing SQL queries for a database schema of research papers.

    Given an input question, first create a syntactically correct {dialect}
    query to run, then look at the results of the query and return the answer.

    You can order the results by a relevant column to return the most interesting examples in the database.

    Never query for all the columns from a specific table, only ask for a few relevant columns given the question.

    Pay attention to use only the column names that you can see in the schema
    description.
    Be careful to not query for columns that do not exist.
    Pay attention to which column is in which table.
    Also, qualify column names with the table name when needed.

    Avoid being too specific with your queries. Instead of using direct match queries for strings, consider using a ILIKE query.

    For example if a query is "find the author named Dimakis", instead of writing "SELECT * FROM authors WHERE first_name = 'Dimakis'", write "SELECT * FROM authors WHERE first_name ILIKE '%dimakis%' OR last_name ILIKE '%dimakis%'".

    Only return the abstract column if necessary.

    Make sure the query does NOT return duplicate rows.

    For questions about paper topics or categories, use the categories tables BUT ALSO the abstracts of the papers.

    Output only the raw SQL query, no markdown block, or anything else.

    Only use tables listed below.
    {schema}

    Question: {query_str}
    SQLQuery:
    """

TEXT_TO_SQL_PROMPT = PromptTemplate(
    TEXT_TO_SQL_TMPL,
)

# Retrieving the table context is VERY slow, just storing it here for convenience
TABLE_CONTEXT = """
Table 'affiliations' has columns: id (INTEGER), name (TEXT), and foreign keys: .

Table 'author_affiliations' has columns: author_id (INTEGER), affiliation_id (INTEGER), and foreign keys: ['affiliation_id'] -> affiliations.['id'], ['author_id'] -> authors.['id'].

Table 'authors' has columns: id (INTEGER), first_name (VARCHAR(255)), last_name (VARCHAR(255)), and foreign keys: .

Table 'categories' has columns: id (INTEGER), name (VARCHAR(255)), and foreign keys: .

Table 'paper_authors' has columns: paper_id (INTEGER), author_id (INTEGER), and foreign keys: ['author_id'] -> authors.['id'], ['paper_id'] -> papers.['id'].

Table 'paper_categories' has columns: paper_id (INTEGER), category_id (INTEGER), and foreign keys: ['category_id'] -> categories.['id'], ['paper_id'] -> papers.['id'].

Table 'papers' has columns: id (INTEGER), filename (VARCHAR(255)), title (TEXT), publication_date (DATE), abstract (TEXT), and foreign keys: .
> Table desc str: Table 'affiliations' has columns: id (INTEGER), name (TEXT), and foreign keys: .

Table 'author_affiliations' has columns: author_id (INTEGER), affiliation_id (INTEGER), and foreign keys: ['affiliation_id'] -> affiliations.['id'], ['author_id'] -> authors.['id'].

Table 'authors' has columns: id (INTEGER), first_name (VARCHAR(255)), last_name (VARCHAR(255)), and foreign keys: .

Table 'categories' has columns: id (INTEGER), name (VARCHAR(255)), and foreign keys: .

Table 'paper_authors' has columns: paper_id (INTEGER), author_id (INTEGER), and foreign keys: ['author_id'] -> authors.['id'], ['paper_id'] -> papers.['id'].

Table 'paper_categories' has columns: paper_id (INTEGER), category_id (INTEGER), and foreign keys: ['category_id'] -> categories.['id'], ['paper_id'] -> papers.['id'].

Table 'papers' has columns: id (INTEGER), filename (VARCHAR(255)), title (TEXT), publication_date (DATE), abstract (TEXT), and foreign keys: .
"""


def _parse_response_to_sql(response: str) -> str:
    sql_result_start = response.find("SQLResult:")
    if sql_result_start != -1:
        response = response[:sql_result_start]
    return response.strip()


@dataclass
class SQLResult:
    sql_query: str
    sql_response_str: str


def ask_sql_query(query_str: str) -> SQLResult:
    database = SQLDatabase.from_uri(DATABASE_URL)
    llm = OpenAI(model="gpt-4-turbo")
    response = llm.predict(
        prompt=TEXT_TO_SQL_PROMPT,
        query_str=query_str,
        schema=TABLE_CONTEXT,
        dialect="postgresql",
    )
    sql = _parse_response_to_sql(response)
    logging.info(f"SQL query: {sql}")
    raw_response, metadata = database.run_sql(sql)
    logging.info(f"SQL response: {raw_response}")
    return SQLResult(sql_query=sql, sql_response_str=str(raw_response))
