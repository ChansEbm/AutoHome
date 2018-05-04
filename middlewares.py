# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time

import requests
import random

import scrapy
from scrapy import signals
import re


class ScrapyredisSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapyredisDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class UserAgentMiddleware(object):
    # def __init__(self, crawler):
    #     # self.ua = UserAgent()
    #     # self.ua_type = crawler.settings.get("UA_TYPE", "random")
    #
    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(crawler)

    def process_request(self, request, spider):
        # def get_ua():
        #     return getattr(self.ua, self.ua_type)
        # request.meta["proxy"] = "http://117.69.201.201:23591"
        request.headers.setdefault("User-Agent",
                                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36")
        request.headers.setdefault("Host", "www.autohome.com.cn")
        request.headers.setdefault("Referer", "https://www.autohome.com.cn/car/")


class SeleniumMiddleware(object):
    def process_request(self, request, spider):
        global time
        if spider.name == 'autohome' or spider.name == 't':
            # spider.browser.add_cookie(request.cookies)
            spider.browser.get(request.url)
            if request.meta.get("need_refresh", False):
                spider.browser.refresh()
            if request.meta.get("need_auto_scroll", False):
                last_height = spider.browser.execute_script("return document.body.scrollHeight")
                while True:
                    spider.browser.execute_script(
                        'window.scrollTo(0, document.body.scrollHeight);')
                    import time
                    time.sleep(random.uniform(0.5, 3.5))
                    new_height = spider.browser.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
            from scrapy.http import HtmlResponse
            return HtmlResponse(url=request.url, body=spider.browser.page_source, request=request, encoding='utf-8')


# http://piping.mogumiao.com/proxy/api/get_ip_al?appKey=099b7b5cf94a4b998b35cd265a3c0f4f&count=1&expiryDate=3&format=1
# def wrapper_proxy(get_proxy):
#     def wrapper_func(func):
#         def fun(*args, **kwargs):
#             f = func(*args, **kwargs)
#             for x in args:
#                 if isinstance(x, scrapy.Request):
#                     x.meta["proxy"] = get_proxy()
#                     break
#             return f
#
#         return fun
#
#     return wrapper_func


class MoguProxyMiddleware(object):
    def __init__(self, crawler):
        self.t = int(time.time())
        self.l_proxies = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def __load_proxy(self):
        req = requests.get(
            "http://piping.mogumiao.com/proxy/api/get_ip_al?appKey=b94f48b8146c474b8a940d618554562e&count=3&expiryDate=3&format=1")
        import json
        proxies = json.loads(req.text, encoding="utf-8")["msg"]
        self.l_proxies.clear()
        self.l_proxies += proxies
        # self.l_proxies = [{"ip": "58.22.177.45", "port": "44408"}]

    def __get_proxy(self):
        now_time = int(time.time())
        if now_time - self.t > 3 * 55 or not any(self.l_proxies):
            self.__load_proxy()
            self.t = time.time()

        def __random_proxy():
            random_index = random.randint(0, len(self.l_proxies) - 1)
            obj = self.l_proxies[random_index]
            random_proxy = f"http://{obj['ip']}:{obj['port']}"
            return random_proxy

        if not any(self.l_proxies):
            self.__load_proxy()

        return __random_proxy()

    def process_request(self, request, spider):
        if request.meta.get("need_proxy", False):
            if not any(request.meta.get("proxy", "")):
                request.meta.update({"proxy": self.__get_proxy()})
        print(request.meta.get("proxy", "Empty Proxy"))

    def process_response(self, request, response, spider):
        status_code = response.status
        if status_code >= 500:
            ip, port = self.__get_ip_port(request.meta.get("proxy", ""))
            item = {"ip": ip, "port": port}
            self.l_proxies.remove(item)
            request.meta["proxy"] = self.__get_proxy()
            return request
        return response

    def process_exception(self, request, exception, spider):
        print(exception)
        proxy = request.meta.get("proxy", "")
        ip, port = self.__get_ip_port(proxy)
        self.l_proxies.remove({"ip": ip, "port": port})
        request.meta["proxy"] = self.__get_proxy()
        return request

    def __get_ip_port(self, proxy_agent):
        if any(proxy_agent):
            agent = re.match(r"https?://(.*):(\d+)", proxy_agent).groups()
            if agent:
                return agent
            raise AttributeError(f"proxy_agent format error:{proxy_agent}")
        raise AttributeError("proxy_agent is empty")
