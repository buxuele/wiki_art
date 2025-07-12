import scrapy


class WikiArtCrawlerItem(scrapy.Item):
    # 定义我们要抓取的数据字段

    # 艺术品标题
    title = scrapy.Field()

    # 艺术家
    artist = scrapy.Field()

    # 创作年份
    year = scrapy.Field()

    # 媒介/风格，比如 "oil on canvas"
    medium = scrapy.Field()

    # 原始大图的直接URL
    original_image_url = scrapy.Field()

    # 抓取来源的维基页面URL
    source_page_url = scrapy.Field()

    # 该图片所属的分类列表
    categories = scrapy.Field()


    # Scrapy图片管道需要这个字段来获取下载URL列表
    image_urls = scrapy.Field()
    # 图片管道处理完后，会把结果（路径、URL等）放回这里
    images = scrapy.Field()

    # --- 新增字段，用来保存图片在本地的路径 ---
    image_local_path = scrapy.Field()

