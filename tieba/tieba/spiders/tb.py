# -*- coding: utf-8 -*-
import scrapy
import re
import requests

from urllib import parse
# from copy import deepcopy

class TbSpider(scrapy.Spider):
    name = 'tb'
    allowed_domains = ['baidu.com']
    # start_urls = ['https://tieba.baidu.com/mo/q---6E0A2EB6531D439003E63D99780EBCD4%3AFG%3D1--1-3-0--2--wapp_1537667986783_459/m?kw=cat&lp=5011&lm=&pn=100']
    start_urls = ['http://tieba.baidu.com/mo/q----,sz@320_240-1-3---2/m?kw=cat&lp=5011&lm=&pn=0']

    def parse(self, response):
        div_list = response.xpath("//div[contains(@class,'i')]")
        for div in div_list:
            item = {}
            # 获取title， 标题链接，并且设置一个空的存放img列表
            item['title'] = div.xpath("./a/text()").extract_first()
            item['href'] = div.xpath("./a/@href").extract_first()
            item['img'] = []
            # print(item)
            # print(type(item['href']))
            # 组织详细链接url,并且抛出request对象交给引擎处理
            if item['href'] is not None:
                item['href'] = parse.urljoin(response.url, item['href'])
            yield scrapy.Request(
                item['href'],
                callback=self.parse_detail,
                meta={'item':item}
            )

        # 设置下一页url
        if 'page' in response.meta:
            print('11')
            page = response.meta['page']
            total_page = page['total_page']
            page['page_text'] = page['page_text'] + 1
            page_text = page['page_text']

        else:
            # print('22')
            total_page = response.xpath("//input[@name='pnum']/@value").extract_first()
            page_text = response.xpath("//div[@class='bc p']/text()").extract()
            page_text = re.sub(r'\xa0', '', page_text[1])

            # print(page_text)
            page_text = re.match(r'第(.*)/', page_text).group(1)
            page = {}
            page['total_page'] = total_page
            page['page_text'] = int(page_text)
            page_text = int(page_text)

        # 构造下一页url,并且抛出request对象给引擎处理
        if page_text <= int(total_page):
            next_url = 'http://tieba.baidu.com/mo/q----,sz@320_240-1-3---2/m?kw=cat&lp=5011&lm=&pn={}'.format(int(page_text)*10)
            yield scrapy.Request(
                next_url,
                callback=self.parse,
                meta={'page':page}
            )
            print(next_url)

    def parse_detail(self, response):
        '''处理详细链接中的内容'''
        # 这里只获取img, 也可以在这个地方编写获取内容的代码
        item = response.meta['item']
        item['img'].extend(response.xpath("//div[contains(@class,'i')][1]//img[@class='BDE_Image']/@src").extract())

        item['img'] = [requests.utils.unquote(i).split('src=')[-1] for i in item['img']]
        # print(item)
        # print('-----'*10)
        # 抛出item给引擎， 让引擎把item给pipeline
        yield item



