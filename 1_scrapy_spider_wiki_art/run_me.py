import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run_spider():

    # 确保 入口 url 是有效的！！！
    # fish
    start_url = "https://commons.wikimedia.org/wiki/File:L%C3%A1brido_tablero_a_cuadros_(Halichoeres_hortulanus),_mar_Rojo,_Egipto,_2023-04-19,_DD_43.jpg"

    # 如果存在旧的输出文件，先删除它，以便每次运行都是全新的开始
    output_file = 'new_artworks.jsonl'

    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed old output file: {output_file}")

    # 获取项目设置
    settings = get_project_settings()

    # 创建一个 CrawlerProcess 实例
    process = CrawlerProcess(settings)

    # 告诉 Scrapy 要启动哪个爬虫，并通过 -a 参数传递我们的 start_url
    process.crawl('art_spider', start_url=start_url)

    # 启动爬虫
    process.start()  # 脚本会在这里阻塞，直到爬虫完成


if __name__ == '__main__':
    run_spider()
    print("Crawling finished.")