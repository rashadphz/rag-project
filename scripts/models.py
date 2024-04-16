from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import json

Base = declarative_base()


class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), unique=True)
    title = Column(Text)
    publication_date = Column(Date)
    abstract = Column(Text)


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))


class Affiliation(Base):
    __tablename__ = "affiliations"
    id = Column(Integer, primary_key=True)
    name = Column(Text)


class PaperAuthor(Base):
    __tablename__ = "paper_authors"
    paper_id = Column(Integer, ForeignKey("papers.id"), primary_key=True)
    author_id = Column(Integer, ForeignKey("authors.id"), primary_key=True)


class AuthorAffiliation(Base):
    __tablename__ = "author_affiliations"
    author_id = Column(Integer, ForeignKey("authors.id"), primary_key=True)
    affiliation_id = Column(Integer, ForeignKey("affiliations.id"), primary_key=True)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class PaperCategory(Base):
    __tablename__ = "paper_categories"
    paper_id = Column(Integer, ForeignKey("papers.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)


if __name__ == "__main__":
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(engine)
