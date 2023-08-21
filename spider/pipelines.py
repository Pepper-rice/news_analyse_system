# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_analysis_system.settings")
django.setup()


class SpiderPipeline:
    def process_item(self, item, spider):
        from news.models import News

        try:
            n = News.objects.create(**item)
            spider.log(f'{n.title}, {n.intro}')
        except:
            pass
        return None
