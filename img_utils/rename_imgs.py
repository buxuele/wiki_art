import os
import uuid


# 遍历指定目录中的图片文件，并使用新的 UUID（前12位）作为文件名重命名，
def just_rename_imgs(directory, show=False):
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff'}

    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)

        if not os.path.isfile(full_path):
            continue

        _, file_extension = os.path.splitext(entry)
        if file_extension.lower() not in valid_extensions:
            continue

        new_id = str(uuid.uuid4()).replace('-', '')[:12]
        new_name = f"{new_id}{file_extension.lower()}"
        new_path = os.path.join(directory, new_name)

        os.rename(full_path, new_path)
        if show:
            print(f"Renamed: {entry} -> {new_name}")


if __name__ == "__main__":
    target = r" C:\Users\Administrator\Desktop\del_me ".strip()
    just_rename_imgs(target, show=True)


