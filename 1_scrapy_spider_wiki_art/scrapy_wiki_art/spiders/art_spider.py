# -*- coding: utf-8 -*-
import scrapy
from scrapy_wiki_art.items import WikiArtCrawlerItem
import re


class ArtSpiderSpider(scrapy.Spider):
    name = 'art_spider'

    allowed_domains = []  # 'commons.wikimedia.org', 'upload.wikimedia.org'

    # 告诉爬虫，404错误我们也可以自己处理，不要直接忽略
    handle_httpstatus_list = [404]

    def __init__(self, start_url=None, *args, **kwargs):
        super(ArtSpiderSpider, self).__init__(*args, **kwargs)
        if start_url:
            self.start_urls = [start_url]
        else:
            self.start_urls = []


    def clean_text(self, text_list):
        """一个辅助函数，用来清理提取出的文本列表"""
        if not text_list:
            return ""
        # 将列表中的所有文本合并，然后去除首尾的空白和换行符
        full_text = "".join(text_list).strip()
        # 使用正则表达式替换掉多个连续的空白符为一个空格
        return re.sub(r'\s+', ' ', full_text)

    def parse(self, response):
        # 如果页面不存在，就记录一下然后跳过
        if response.status == 404:
            self.logger.warning(f"Page not found: {response.url}")
            return

        item = WikiArtCrawlerItem()

        # --- 使用更健壮的选择器和清理函数 ---
        artist_text = response.xpath(
            "//td[contains(., 'Artist') or contains(., 'Author')]/following-sibling::td[1]//text()").getall()
        item['artist'] = self.clean_text(artist_text)

        title_text = response.xpath("//td[contains(., 'Title')]/following-sibling::td[1]//text()").getall()
        item['title'] = self.clean_text(title_text)

        year_text = response.xpath("//td[contains(., 'Date')]/following-sibling::td[1]//text()").getall()
        item['year'] = self.clean_text(year_text)

        medium_text = response.xpath("//td[contains(., 'Medium')]/following-sibling::td[1]//text()").getall()
        item['medium'] = self.clean_text(medium_text)
        # --- END ---

        original_image_url = response.css('div.fullImageLink a::attr(href)').get()
        item['original_image_url'] = response.urljoin(original_image_url)
        item['source_page_url'] = response.url

        if item['original_image_url']:
            item['image_urls'] = [item['original_image_url']]
        else:
            item['image_urls'] = []

        category_links = response.css('#mw-normal-catlinks ul li a, #mw-hidden-catlinks ul li a')
        item['categories'] = [self.clean_text([text]) for text in category_links.css('::text').getall()]

        yield item

        for link in category_links:
            yield response.follow(link, callback=self.parse_category)

    def parse_category(self, response):
        if response.status == 404:
            self.logger.warning(f"Category page not found: {response.url}")
            return

        image_page_links = response.css('#mw-category-media div.gallerytext a.galleryfilename-truncate')
        for link in image_page_links:
            yield response.follow(link, callback=self.parse)

        next_page = response.xpath("//a[contains(., 'next page')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_category)