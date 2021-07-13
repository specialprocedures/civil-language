from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from civilscraper.models import db_connect, create_table, tag_article, Article, Tag

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class CivilscraperPipeline:
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        # Save articles in the database

        session = self.Session()
        article = Article()
        tag = Tag()
        article.civil_id = int(item["url"].split("/")[-1])
        article.url = item["url"]
        article.hot = item["hot"]
        article.date = item["date"]
        article.title = item["title"]
        article.body = item["body"]
        article.lang = item["lang"]

        # check whether the current quote has tags or not
        if "tags" in item:
            for tag_name in item["tags"]:
                tag = Tag(name=tag_name)
                # check whether the current tag already exists in the database
                exist_tag = session.query(Tag).filter_by(name=tag.name).first()
                if exist_tag is not None:  # the current tag exists
                    tag = exist_tag
                article.tags.append(tag)

        try:
            session.add(article)
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

        return item
