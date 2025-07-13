from PIL import Image

# 目的  调整图片大小。做 Chrome ，需要用到图标。
# 先找2张图片插件的时候

def resize_image(input_name, out_name, out_width, out_height):
    img = Image.open(input_name)
    out = img.resize((out_width, out_height))
    out.save(out_name)


# 插件激活状态的图标
input_image = "g1.jpg"
for i in [16, 48, 128]:
    out_image = f"icon{i}_active.png"
    resize_image(input_image, out_image, i, i)

