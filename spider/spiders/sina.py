import scrapy
import time
import json
from datetime import datetime


def get_attrs(d, *fields):
    return {k: v for k, v in d.items() if k in fields}


class SinaSpider(scrapy.Spider):
    name = "sina"
    allowed_domains = []
    start_urls = []
    channels = {
        # 2509: "全部",
        2510: "国内",
        2511: "国际",
        2512: "体育",
        2513: "娱乐",
        2514: "军事",
        2515: "科技",
        2516: "财经",
        2517: "股市",
        2518: "美股",
        2669: "社会",
    }

    api = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid={lid}&k=&num=50&page={page}&r=0.7534897522230548"

    def start_requests(self):
        for lid, subject in self.channels.items():
            url = self.api.format(lid=lid, page=1)
            yield scrapy.Request(url, meta=dict(page=1, lid=lid, subject=subject))

    def parse(self, response):
        meta = response.meta
        lid = meta["lid"]
        try:
            result = json.loads(response.text)["result"]
        except:
            pass
        else:
            start_ts = result["start"]
            if datetime.fromtimestamp(start_ts).strftime(
                "%Y-%m-%d"
            ) == datetime.now().strftime("%Y-%m-%d"):
                # 列表
                for item in result["data"]:
                    meta["item"] = item
                    yield scrapy.Request(
                        item["url"], meta=meta, callback=self.parse_page
                    )

                # 翻页
                meta["page"] += 1
                url = self.api.format(lid=lid, page=1)
                yield scrapy.Request(url, meta=meta)

    def parse_page(self, response):
        meta = response.meta
        data = meta["item"]
        text = ""
        html = ""
        for el in response.css(
            "#article,#artibody > *:not(.wap_special):not(script):not(#left_hzh_ad):not(style)"
        ):
            text += el.xpath("string(.)").extract_first() + "\n"
            html += el.extract() + "\n"
        item = get_attrs(
            data,
            "title",
            "url",
            "keywords",
            "intro",
            "media_name",
            "docid",
            "wapurl",
            "images",
            "img",
        )
        item["img"] = json.dumps(item["img"], ensure_ascii=False)
        item["images"] = json.dumps(item["images"], ensure_ascii=False)
        item["subject"] = meta["subject"]
        item["text"] = text
        item["html"] = html
        item["intime"] = datetime.fromtimestamp(int(data["intime"])).strftime(
            "%Y-%m-%d"
        )
        if item["media_name"] != "新浪彩票":
            yield item
