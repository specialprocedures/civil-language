from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Table,
    create_engine,
)

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from scrapy.utils.project import get_project_settings


Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(engine)


tag_article = Table(
    "tag_article",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("article.article_id")),
    Column("tag_id", Integer, ForeignKey("tag.tag_id")),
)


class Article(Base):
    __tablename__ = "article"
    article_id = Column(Integer, primary_key=True)
    civil_id = Column(Integer)
    url = Column(String(50))
    date = Column(DateTime)
    lang = Column(String(3))
    hot = Column(Integer)
    title = Column(String(100))
    body = Column(Text)
    tags = relationship("Tag", secondary=tag_article, lazy="dynamic", backref="article")


class Tag(Base):
    __tablename__ = "tag"
    tag_id = Column(Integer, primary_key=True)
    name = Column(String)
    articles = relationship(
        "Article", secondary="tag_article", lazy="dynamic", backref="tag"
    )
