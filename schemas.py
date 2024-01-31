from dataclasses import dataclass
from datetime import datetime

from marshmallow import Schema, fields

DATE_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


@dataclass
class SourceInfo:
    id: str
    name: str


@dataclass
class ArticleDto:
    source: SourceInfo
    author: str
    title: str
    description: str
    url: str
    urlToImage: str
    publishedAt: datetime
    content: str

    def __post_init__(self):
        self.publishedAt = datetime.strptime(self.publishedAt, DATE_FORMAT_STRING)


class ArticleSchema(Schema):
    url = fields.String()
    title = fields.String()
    publishedAt = fields.DateTime()
