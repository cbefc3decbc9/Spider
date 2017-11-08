# -*- coding: utf-8 -*-
import scrapy
from douban.items import DoubanItem


class TopSpider(scrapy.Spider):
    name = 'top'
    allowed_domains = ['douban.com']
    url = 'https://movie.douban.com/top250?start='
    offset = 0
    start_urls = [url + str(offset)]

    def parse(self, response):

        item = DoubanItem()
        movie_list = response.xpath('//div[@class="info"]')

        for each in movie_list:

            name = each.xpath('./div[@class="hd"]/a/span[1]/text()')[0]

            info = each.xpath('./div[@class="bd"]/p/text()').extract()[1::2][0].strip()
            infolist = info.split("/")

            year = infolist[0].strip()
            area = infolist[1].strip()
            category = infolist[2].strip()

            score = each.xpath('./div[@class="bd"]/div[@class="star"]/span[@class="rating_num"]/text()')[0]

            try:
                desc = each.xpath('./div[@class="bd"]/p[@class="quote"]/span/text()')[0]

                item['desc'] = desc.extract()
            except:
                item['desc'] = "无"


            item['name'] = name.extract()
            item['year'] = year
            item['area'] = area
            item['category'] = category
            item['score'] = score.extract()

            yield item

        if self.offset <= 225:
            self.offset += 25

        yield scrapy.Request(self.url + str(self.offset), callback = self.parse)



