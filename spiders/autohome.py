# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from ScrapyRedis.items import AutoItemLoader, AuthHomeItems


def process_request(request):
    request.meta.update({"need_auto_scroll": True})
    return request


def load_request_proxy(request):
    request.meta.update({"need_proxy": True})
    return request


class AutohomeSpider(CrawlSpider):
    name = 'autohome'
    allowed_domains = ['www.autohome.com.cn', 'www.che168.com']
    start_urls = ['https://www.autohome.com.cn/guangzhou/']
    download_timeout = 3
    rules = (
        Rule(LinkExtractor(allow=r"/car/.*",
                           restrict_xpaths=r"//div[@class='homepage-findcar']"), process_request=process_request,
             follow=True),

        Rule(LinkExtractor(allow=r"/\d+/#levelsource=\d+_\d+&pvareaid=\d+"), process_request=load_request_proxy,
             callback="parse_item", follow=True),
        # Rule(LinkExtractor(r"/\d+/#pvareaid=\d+"), callback="parse_item", follow=True),
    )

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {"ScrapyRedis.middlewares.SeleniumMiddleware": 200,
                                   # "ScrapyRedis.middlewares.MoguProxyMiddleware": 100,
                                   },
        "ITEM_PIPELINES": {
            "ScrapyRedis.pipelines.AutoHomePipeline": 100,
        }
    }

    def __init__(self):
        super(AutohomeSpider, self).__init__()
        from selenium import webdriver
        self.opts = webdriver.ChromeOptions()
        # 不加载图片
        # prefs = {"profile.managers_default_content.images": 2}
        # self.opts.add_experimental_option("prefs", prefs)
        # self.opts.add_argument("-headless")
        self.browser = webdriver.Chrome(options=self.opts)

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], meta={"need_refresh": True})

    def parse_item(self, response):
        auto_loader = AutoItemLoader(item=AuthHomeItems(), response=response)
        auto_loader.add_xpath("bloc", "//div[@class='subnav-title-name']//text()")
        auto_loader.add_xpath("car_name", "//div[@class='subnav-title-name']//text()")
        auto_loader.add_xpath("score", "//a[@class='font-score']/text()")
        auto_loader.add_xpath("failures_of_hundred_cars", "//a[contains(@class,'font-fault')]/text()")
        auto_loader.add_xpath("new_car_guidance",
                              "//div[@class='autoseries-info']/dl/dt[1]/a[1]/text()|//div[@id='tab1-1']//div[@class='car_price']//span[@class='price'][1]/strong//text()")
        auto_loader.add_xpath("car_shop_guidance", "//dt[@id='area_mallprice']/a[1]/text()")
        auto_loader.add_xpath("secondhand_guidance",
                              "//dt[@id='series_che168']/a[1]/text()|//div[@id='tab1-1']//div[@class='car_price']//span[@class='price'][2]/strong//text()")
        auto_loader.add_xpath("engine",
                              "//div[@class='autoseries-info']/dl/dd[2]/a/text()|//div[@id='tab1-1']//div[@class='models_info']/dl[2]//span/text()")
        auto_loader.add_xpath("gearbox",
                              "//div[@class='autoseries-info']/dl/dd[3]/a[1]/text()|//div[@id='tab1-1']//div[@class='models_info']/dl[3]/dd[1]/span//text()")
        auto_loader.add_xpath("car_structure",
                              "//div[@class='autoseries-info']/dl/dd[3]/a[position()>1]/text()|//div[@id='tab1-1']//div[@class='models_info']/dl[3]/dd[2]/span//text()")
        url = response.xpath(
            "//span[@class='preservation-entrance']/a/@href|//table[@class='loan-table']//a/@href").extract_first()
        yield scrapy.Request(url=f"https://{url}", meta={"car_detail": auto_loader}, callback=self.parse_all_info)

    def parse_all_info(self, response):
        auto_loader = response.request.meta.get("car_detail", None)
        if auto_loader is None:
            return
        rates = response.xpath("//div[@class='rate qingse']/text()").extract()
        auto_loader.add_value("rate", rates)
        yield auto_loader.load_item()
