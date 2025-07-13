import json
import os
import re
import uuid
import shutil

# --- 1. 定义工作区内的路径 (所有路径都是相对当前脚本的) ---
# 我们假设这个脚本就放在 2_annotation_workspace 文件夹里
ORIGINAL_METADATA_FILE = 'artworks.jsonl'
ORIGINAL_IMAGES_DIR = 'full'  # 原始图片就在当前目录下的'full'文件夹里

# 我们将要创建的、全新的、干净的目标
NEW_IMAGES_DIR = 'images_renamed_by_uuid'
NEW_METADATA_FILE = 'artworks_final.jsonl'


# --- 2. 定义数据清洗函数 (保持不变) ---
def clean_artist(raw_artist):
    if not isinstance(raw_artist, str): return ""
    cleaned = re.sub(r'\.mw-parser-output.*\}', '', raw_artist, flags=re.S)
    cleaned = re.sub(r'Authority file.*', '', cleaned, flags=re.S)
    return re.sub(r'\s+', ' ', cleaned).strip()


def clean_title(raw_title):
    if not isinstance(raw_title, str): return ""
    cleaned = re.sub(r'title QS:.*|label QS:.*', '', raw_title, flags=re.I)
    return re.sub(r'\s+', ' ', cleaned).strip()


def clean_year(raw_year):
    if not isinstance(raw_year, str): return ""
    match = re.search(r'\b\d{4}\b', raw_year)
    return match.group(0) if match else raw_year.strip()


# --- 3. 主流程：就地取材，完成重生 ---
def regenerate_in_workspace():
    print("--- Starting Data Regeneration Process (Workspace Mode) ---")

    # 检查输入文件和文件夹是否存在
    if not os.path.exists(ORIGINAL_METADATA_FILE):
        print(f"FATAL ERROR: Metadata file not found in current directory: '{ORIGINAL_METADATA_FILE}'")
        return
    if not os.path.exists(ORIGINAL_IMAGES_DIR):
        print(f"FATAL ERROR: Images directory not found in current directory: '{ORIGINAL_IMAGES_DIR}'")
        return

    # 创建新的目标文件夹
    if os.path.exists(NEW_IMAGES_DIR):
        print(f"Warning: Overwriting existing directory '{NEW_IMAGES_DIR}'.")
        shutil.rmtree(NEW_IMAGES_DIR)
    os.makedirs(NEW_IMAGES_DIR)
    print(f"Created new image directory at: '{NEW_IMAGES_DIR}'")

    with open(NEW_METADATA_FILE, 'w', encoding='utf-8') as f_out:
        with open(ORIGINAL_METADATA_FILE, 'r', encoding='utf-8') as f_in:

            print("\n--- Processing records and renaming files... ---")
            total_count = 0
            success_count = 0

            for line in f_in:
                total_count += 1
                record = json.loads(line)

                if not record.get('image_local_path'):
                    continue

                # --- 核心变通：直接使用当前工作区内的路径 ---
                # 'image_local_path' 的值是 'full/image.jpg'
                # 这正好就是我们需要的、相对于当前目录的路径！
                original_file_path = record['image_local_path'].replace('/', os.sep)

                if not os.path.exists(original_file_path):
                    print(f"Skipping, file not found: '{original_file_path}'")
                    continue

                # 生成UUID并重命名
                _, ext = os.path.splitext(original_file_path)
                new_filename = f"{uuid.uuid4()}{ext}"
                new_file_path = os.path.join(NEW_IMAGES_DIR, new_filename)

                shutil.copy(original_file_path, new_file_path)

                # 清洗元数据并更新路径
                cleaned_record = {
                    'uuid': os.path.splitext(new_filename)[0],
                    'artist': clean_artist(record.get('artist')),
                    'title': clean_title(record.get('title')),
                    'year': clean_year(record.get('year')),
                    'medium': record.get('medium', '').strip(),
                    # 新的路径，相对于当前工作区
                    'image_local_path': os.path.join(NEW_IMAGES_DIR, new_filename).replace('\\', '/'),
                    'original_source_url': record.get('original_image_url')
                }

                f_out.write(json.dumps(cleaned_record, ensure_ascii=False) + '\n')
                success_count += 1

    print("\n--- Regeneration Complete! ---")
    print(f"Successfully created {success_count} cleaned and renamed items.")
    print(f"Your new, golden dataset is now ready in the current workspace:")
    print(f"  - Cleaned metadata: '{NEW_METADATA_FILE}'")
    print(f"  - Renamed images:   '{NEW_IMAGES_DIR}'")


if __name__ == '__main__':
    regenerate_in_workspace()