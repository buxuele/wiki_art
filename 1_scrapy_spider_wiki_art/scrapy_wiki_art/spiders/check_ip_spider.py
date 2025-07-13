# -*- coding: utf-8 -*-
import scrapy
import json


class CheckIpSpider(scrapy.Spider):
    name = 'check_ip'

    # 我们不再需要 allowed_domains，因为这个爬虫就是用来访问外部服务的
    # allowed_domains = []

    # 我们访问一个会返回我们请求信息的公共服务
    start_urls = ['http://httpbin.org/ip']

    def parse(self, response):
        """
        这个爬虫非常简单，它只做一件事：
        打印出 httpbin.org 看到的我们的IP地址。
        """
        # httpbin.org/ip 返回的是一个JSON，例如：{"origin": "1.2.3.4"}
        data = json.loads(response.text)
        ip_address = data['origin']

        self.logger.info("=" * 50)
        self.logger.info(f"Scrapy is sending requests from IP: {ip_address}")
        self.logger.info("=" * 50)