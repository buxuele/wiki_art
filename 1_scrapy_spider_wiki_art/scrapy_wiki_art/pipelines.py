# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline
import re
import os
from PIL import Image  # 导入Image模块


class CustomImagesPipeline(ImagesPipeline):
    """
    我们自定义的图片管道，继承自官方的 ImagesPipeline。
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # --- 核心修复：禁用Pillow的解压缩炸弹检查 ---
        # 将其设置为 None 可以移除像素数量限制
        Image.MAX_IMAGE_PIXELS = None
        # (或者设置为一个非常大的值，比如 Image.MAX_IMAGE_PIXELS = 933120000)

    def file_path(self, request, response=None, info=None, *, item=None):
        # 1. 从原始的图片URL中获取真实的扩展名
        _, ext = os.path.splitext(request.url)
        if not ext:
            ext = '.jpg'

        # 2. 从 item 的 title 字段生成干净的文件名主干
        if item and item.get('title'):
            image_name_base = re.sub(r'[\\/*?:"<>|]', "", item['title']).strip()
            if len(image_name_base) < 3:
                image_guid = self.get_media_requests(item, info)[0].meta.get('image_guid')
                image_name_base = image_guid
        else:
            image_guid = self.get_media_requests(item, info)[0].meta.get('image_guid')
            image_name_base = image_guid

        # 3. 确保主干部分不会太长
        if len(image_name_base) > 100:
            image_name_base = image_name_base[:100]

        # 4. 拼接成最终的文件名
        final_filename = f"{image_name_base}{ext}"

        return f'full/{final_filename}'

    def item_completed(self, results, item, info):
        if results and results[0][0]:
            item['image_local_path'] = results[0][1]['path']
        return item