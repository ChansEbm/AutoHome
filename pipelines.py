# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ScrapyredisPipeline(object):
    def process_item(self, item, spider):
        return item

class AutoHomePipeline(object):
    def __init__(self):
        from pymongo import MongoClient
        self.db = MongoClient("mongodb://auto:auto123@192.168.31.50/auto_home").auto_home
        pass

    def process_item(self, item, spider):
        self.db.cars.save(
            {
                "bloc": item.get("bloc", "暂无"),
                "car_name": item.get("car_name", "暂无"),
                "score": item.get("score", "暂无"),
                "failures_of_hundred_cars": item.get("failures_of_hundred_cars", "暂无"),
                "new_car_guidance": item.get("new_car_guidance", "暂无"),
                "car_shop_guidance": item.get("car_shop_guidance", "暂无"),
                "secondhand_guidance": item.get("secondhand_guidance", "暂无"),
                "engine": item.get("engine", "暂无"),
                "gearbox": item.get("gearbox", "暂无"),
                "car_structure": item.get("car_structure", "暂无"),
                "rate": item.get("rate", [])
            }
        )
        pass
