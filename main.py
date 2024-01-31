from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from flask_apispec import marshal_with

from config import SQLALCHEMY_DATABASE_URI
from db import db
from schemas import ArticleSchema
from service import Service


service = Service()


def init_app():
    """Initialize the core application."""
    app = Flask(__name__)
    # configure the SQLite database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

    # Initialize Plugins
    db.init_app(app)
    with app.app_context():
        service.fetch_and_save_articles()
        define_background_data_polling()

        @app.route("/news")
        @marshal_with(ArticleSchema(many=True))
        def get_news():
            keyword = request.args.get("keyword")
            articles = service.get_latest_articles(keyword)
            return articles

        return app


def define_background_data_polling():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(service.fetch_and_save_articles, "interval", minutes=60)
    sched.start()


if __name__ == "__main__":
    init_app().run(debug=True, port=3000)
