from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import SQLALCHEMY_DATABASE_URI
from db import db

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# Set your classes here.

class Article(Base):
    __tablename__ = "articles"
    url = db.Column(db.String, unique=True, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    publishedAt = db.Column(db.DateTime, nullable=False)


# Create tables.
Base.metadata.create_all(bind=engine)
