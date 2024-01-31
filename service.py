import json
from datetime import datetime, timedelta

import requests

from config import API_KEY
from db import db
from models import Article
from schemas import ArticleDto, DATE_FORMAT_STRING

ARTICLES_IN_NEWS_PAGE = 25


class Service:
    def __init__(self):
        self.from_time = datetime.now() - timedelta(days=1)

    def fetch_articles(self) -> list[ArticleDto]:
        base_news_api_url = "https://newsapi.org"
        news_api_everything_url = f"{base_news_api_url}/v2/everything"
        page_size = 100
        payload = {
            "apiKey": API_KEY,
            "q": "drone",
            "sortBy": "popularity",
            "from": self.from_time.strftime(DATE_FORMAT_STRING),
            "pageSize": page_size,
        }
        r = requests.get(news_api_everything_url, params=payload)
        content = json.loads(r.text)
        articles: list[dict] = content["articles"]
        total_results = int(content["totalResults"])
        for page_index in range(2, int(total_results / page_size)):
            payload = {
                "apiKey": API_KEY,
                "q": "drone",
                "sortBy": "popularity",
                "from": self.from_time.strftime(DATE_FORMAT_STRING),
                "pageSize": page_size,
                "page": page_index,
            }
            r = requests.get(news_api_everything_url, params=payload)
            content = json.loads(r.text)
            current_articles: list[dict] = content["articles"]
            articles = articles + current_articles

        return [ArticleDto(**article) for article in articles]

    def save_articles(self, articles: list[ArticleDto]):
        for article in articles:
            if self.from_time < article.publishedAt:
                self.from_time = article.publishedAt

            article_in_db = db.session.query(Article).filter_by(url=article.url).first()
            if not article_in_db:
                db.session.add(
                    Article(
                        url=article.url,
                        title=article.title,
                        publishedAt=article.publishedAt,
                    )
                )
                db.session.commit()
            else:
                article_in_db.title = article.title
                article_in_db.publishedAt = article.publishedAt
                db.session.commit()

    def fetch_and_save_articles(self):
        articles = self.fetch_articles()
        self.save_articles(articles)
        print(
            db.session()
            .query(Article)
            .order_by(Article.publishedAt.desc())
            .limit(ARTICLES_IN_NEWS_PAGE)
            .all()
        )

    def get_latest_articles(self, keyword: str | None) -> list[Article]:
        if keyword:
            return (
                db.session()
                .query(Article)
                .filter(Article.title.icontains(keyword))
                .order_by(Article.publishedAt.desc())
                .limit(ARTICLES_IN_NEWS_PAGE)
                .all()
            )

        return (
            db.session()
            .query(Article)
            .order_by(Article.publishedAt.desc())
            .limit(ARTICLES_IN_NEWS_PAGE)
            .all()
        )
