# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose


class ScrapyredisItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def identity_empty_filed(value):
    return value.strip()


def price_formatter(value):
    x = identity_empty_filed(value)
    x = x[0:-1].strip().split("-")
    return x


def bloc_formatter(value):
    x = identity_empty_filed(value)
    return "-".join(x.split("-")[0:-1])


def car_name_formatter(value):
    print(f"car_name:{value}")
    x = identity_empty_filed(value)
    return x.split("-")[-1:]


class AutoItemLoader(ItemLoader):
    # default_output_processor = TakeFirst()
    default_input_processor = MapCompose(identity_empty_filed)


class AuthHomeItems(scrapy.Item):
    class BlocCarNameFormatter(object):
        def __init__(self, flag):
            self.flag = flag

        def __call__(self, values):
            return self.formatter("".join(values).strip())

        def formatter(self, value):
            return {
                "car_name": value.split("-")[-1:],
                "bloc": value.split("-")[0:-1]
            }.get(self.flag, "")

    bloc = scrapy.Field(
        input_processor=BlocCarNameFormatter("bloc"),
        output_processor=TakeFirst()
    )
    car_name = scrapy.Field(
        input_processor=BlocCarNameFormatter("car_name"),
        output_processor=TakeFirst()
    )
    score = scrapy.Field(
        output_processor=TakeFirst()
    )
    failures_of_hundred_cars = scrapy.Field(
        output_processor=TakeFirst()
    )
    new_car_guidance = scrapy.Field(
        input_processor=MapCompose(price_formatter),
    )
    car_shop_guidance = scrapy.Field(
        input_processor=MapCompose(price_formatter),
    )
    secondhand_guidance = scrapy.Field(
        input_processor=MapCompose(price_formatter),
    )
    engine = scrapy.Field(
    )
    gearbox = scrapy.Field(
    )
    car_structure = scrapy.Field(
    )
    rate = scrapy.Field(
        input_processor=MapCompose(lambda value: value[0:-1])
    )
