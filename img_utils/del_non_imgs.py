import os
import shutil

# 删掉此文件夹中所有非图片文件
def del_non_imgs(img_dir):
    for file in os.listdir(img_dir):
        if not file.endswith('.jpg') and not file.endswith('.png') and not file.endswith('.jpeg'):
            os.remove(os.path.join(img_dir, file))

if __name__ == '__main__':
    dd = r"C:\Users\Administrator\Work\wiki_art\scrapy_wiki_art\wiki_imgs\full"
    del_non_imgs(dd)


