from datetime import datetime
from scrapy.spiders import SitemapSpider
from bs4 import BeautifulSoup
import re


class CivilSpider(SitemapSpider):
    name = "civil"
    # allowed_domains = ["civil.ge/archives"],
    sitemap_urls = ["https://civil.ge/sitemap-index-1.xml"]
    sitemap_rules = [(r"/archives/", "parse")]

    def parse(self, response):

        # Build initial output dict from xpath
        sels = {
            "title": "/html/body/div[1]/div/div/div[2]/div/div/article/header/div/h1//text()",
            "date": "/html/body/div[1]/div/div/div[2]/div/div/article/header/div/div/span//text()",
            "hot": "/html/body/div[1]/div/div/div[2]/div/div/article/header/div/div/div/span[1]//text()",
            "tags": "/html/body/div[1]/div/div/div[2]/div/div/article/div[3]/div[2]/span//text()",
        }

        d = {k: response.xpath(v).extract() for k, v in sels.items()}

        # Record url
        d["url"] = response.url

        # Get language from url ('/ka/' and '/ru/ are present, defaults to English if None,
        for lang in ["ru", "ka"]:
            if re.search(lang, d["url"]):
                d["lang"] = lang

        if d.get("lang") is None:
            d["lang"] = "en"

        # The body's a bit more fiddly as it contains a lot of junk and there's not good selector
        # I revert to bs4 where I'm more comfortable, and hack about with a heuristic
        soup = BeautifulSoup(response.text, "lxml")
        body = soup.find("div", attrs={"class": "entry-content entry clearfix"})
        text = "\n\n".join([i.text for i in body.find_all("p")]).replace(u"\xa0", u" ")

        for tail_hint in [
            "Also read:",
            "Also Read:",
            "Read also:",
            "Read Also:",
            "ასევე წაიკითხეთ",
            "По теме",
            "This post is also available",
        ]:
            d["body"] = "".join(text.split(tail_hint)[0]).strip()

        # Some simple clearing up of other fields
        d["title"] = d["title"][0]
        d["date"] = datetime.strptime(d["date"][0], "%d/%m/%Y - %H:%M")
        d["hot"] = int(d["hot"][0].strip())
        d["tags"] = [i.strip() for i in d["tags"] if i != " "]
        if len(d["tags"]) == 0:
            d.pop("tags", None)

        yield d
