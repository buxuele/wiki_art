BOT_NAME = "scrapy_wiki_art"

SPIDER_MODULES = ["scrapy_wiki_art.spiders"]
NEWSPIDER_MODULE = "scrapy_wiki_art.spiders"


# 设置一个友好的 User-Agent，假装我们是浏览器
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# 设置下载延迟，给对方服务器减轻压力，单位是秒。这是非常重要的礼貌行为！
DOWNLOAD_DELAY = 2

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8 #  32

FEEDS = {
    'artworks.jsonl': {
        'format': 'jsonlines',
        'encoding': 'utf8',
        'store_empty': False,
        'fields': None,
        'indent': 4,
    }
}

# --- 新增和修改的配置 ---

# 1. 设置爬取深度限制
DEPTH_LIMIT = 2

# 2. 设置爬取 Item 数量限制
CLOSESPIDER_ITEMCOUNT = 500

# 3. 配置 Item Pipelines，启用图片管道
ITEM_PIPELINES = {
   'scrapy_wiki_art.pipelines.CustomImagesPipeline': 1,
}

# 4. 设置图片下载目录
IMAGES_STORE = r'C:\Users\Administrator\Work\wiki_fish_imgs'


# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
   "Accept-Language": "en",
}

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# --- 在文件末尾添加下面这行 ---
# 限制下载文件的最大尺寸，单位是字节。
# 20MB = 20 * 1024 * 1024 = 20971520 字节
DOWNLOAD_MAXSIZE = 20971520