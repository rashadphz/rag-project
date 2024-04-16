import os

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
from metadata_extraction import PaperMetadata
from supabase import create_client, Client
from dotenv import load_dotenv
from models import (
    Base,
    Category,
    Paper,
    Author,
    Affiliation,
    AuthorAffiliation,
    PaperAuthor,
    PaperCategory,
)
from sqlalchemy.dialects.postgresql import insert

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()




def read_extractions(file: str) -> list[PaperMetadata]:
    with open(file, "r") as f:
        return [PaperMetadata.model_validate_json(line) for line in f.readlines()]


def clear_db():
    session.query(Paper).delete()
    session.query(Author).delete()
    session.commit()


def insert_extractions(extractions: list[PaperMetadata]):
    clear_db()
    for extraction in extractions:
        paper = Paper(
            filename=extraction.id,
            title=extraction.title,
            publication_date=extraction.publication_date,
            abstract=extraction.abstract,
        )
        session.add(paper)
        session.flush()

        for author in extraction.authors:
            db_author = (
                session.query(Author)
                .filter_by(first_name=author.first_name, last_name=author.last_name)
                .first()
            )
            if not db_author:
                db_author = Author(
                    first_name=author.first_name, last_name=author.last_name
                )
                session.add(db_author)
                session.flush()

            db_paper_author = (
                session.query(PaperAuthor)
                .filter_by(paper_id=paper.id, author_id=db_author.id)
                .first()
            )
            if not db_paper_author:
                db_paper_author = PaperAuthor(
                    paper_id=paper.id, author_id=db_author.id
                )
                session.add(db_paper_author)
                session.flush()

            for affiliation in author.affiliations:
                db_affiliation = (
                    session.query(Affiliation).filter_by(name=affiliation).first()
                )
                if not db_affiliation:
                    db_affiliation = Affiliation(name=affiliation)
                    session.add(db_affiliation)
                    session.flush()

                db_author_affiliation = (
                    session.query(AuthorAffiliation)
                    .filter_by(author_id=db_author.id, affiliation_id=db_affiliation.id)
                    .first()
                )
                if not db_author_affiliation:
                    author_affiliation = AuthorAffiliation(
                        author_id=db_author.id, affiliation_id=db_affiliation.id
                    )
                    session.add(author_affiliation)
                    session.flush()

        for category in extraction.categories:
            db_category = session.query(Category).filter_by(name=category).first()
            if not db_category:
                db_category = Category(name=category)
                session.add(db_category)
                session.flush()

            db_paper_category = (
                session.query(PaperCategory)
                .filter_by(paper_id=paper.id, category_id=db_category.id)
                .first()
            )
            if not db_paper_category:
                paper_category = PaperCategory(
                    paper_id=paper.id, category_id=db_category.id
                )
                session.add(paper_category)
                session.flush()

        session.commit()


if __name__ == "__main__":

    Base.metadata.create_all(engine)

    extractions = read_extractions("./meta-output/meta-extractions.jsonl")
    insert_extractions(extractions)
