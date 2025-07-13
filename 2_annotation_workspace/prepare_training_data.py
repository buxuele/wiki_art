import json
import os
import re
import random

# --- 1. 配置路径 ---
METADATA_FILE = 'artworks.jsonl'
LIKES_DIR = 'good'
DISLIKES_DIR = r'C:\Users\Administrator\Desktop\del_me'

# 我们直接生成最终的、干净的、平衡的数据集
FINAL_DATASET_FILE = 'final_dataset.jsonl'


# --- 2. 定义我们的“强力清洗”函数 ---
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


# --- 3. 加载元数据 ---
print("--- Step 1: Loading Metadata ---")
metadata_map = {}
with open(METADATA_FILE, 'r', encoding='utf-8') as f:
    for record in (json.loads(line) for line in f):
        if record.get('image_local_path'):
            metadata_map[record['image_local_path']] = record
print(f"Loaded {len(metadata_map)} records.\n")


# --- 4. 定义一个集“匹配、清洗、标记”于一体的函数 ---
def process_directory_and_clean(directory_path, label):
    cleaned_records = []
    if not os.path.exists(directory_path):
        print(f"Warning: Directory not found, skipping: '{directory_path}'")
        return cleaned_records

    print(f"--- Step 2: Processing directory '{directory_path}' ---")
    for filename_with_prefix in os.listdir(directory_path):
        original_filename = re.sub(r'^\d{8}_\d{6}_', '', filename_with_prefix)
        base_name, ext = os.path.splitext(original_filename)
        if len(base_name) > 100:
            base_name = base_name[:100]
        truncated_filename = f"{base_name}{ext}"
        generated_path = f"full/{truncated_filename}"

        if generated_path in metadata_map:
            record = metadata_map[generated_path]
            cleaned_record = {
                'artist': clean_artist(record.get('artist')),
                'title': clean_title(record.get('title')),
                'year': clean_year(record.get('year')),
                'medium': record.get('medium', '').strip(),
                'categories': record.get('categories', []),
                'image_local_path': record.get('image_local_path'),
                'label': label
            }
            cleaned_records.append(cleaned_record)

    print(f"Found and cleaned {len(cleaned_records)} items.\n")
    return cleaned_records


# --- 5. 执行处理和清洗 ---
liked_data = process_directory_and_clean(LIKES_DIR, 1)  # 喜欢=1
disliked_data = process_directory_and_clean(DISLIKES_DIR, 0)  # 不喜欢=0

# --- 6. 创建平衡的数据集 (欠采样) ---
print("--- Step 3: Building balanced dataset ---")
num_likes = len(liked_data)
if num_likes == 0:
    print("FATAL ERROR: No liked items found. Cannot build a dataset.")
    exit()

if len(disliked_data) < num_likes:
    dislikes_sampled = disliked_data
else:
    dislikes_sampled = random.sample(disliked_data, num_likes)

print(f"Using {len(liked_data)} liked items and {len(dislikes_sampled)} disliked items.")

# --- 7. 合并、打乱并保存最终结果 ---
final_dataset = liked_data + dislikes_sampled
random.shuffle(final_dataset)

with open(FINAL_DATASET_FILE, 'w', encoding='utf-8') as f:
    for record in final_dataset:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')

print(f"\n--- All Done! ---")
print(f"Final balanced and cleaned dataset with {len(final_dataset)} items saved to '{FINAL_DATASET_FILE}'.")