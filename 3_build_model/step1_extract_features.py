import torch
import timm  # 导入我们强大的新武器
from PIL import Image
import numpy as np
import os
from tqdm import tqdm

# --- 1. 配置你的文件夹路径
GOOD_DIR = r'good'
BAD_DIR = r"bad"



# 输出文件 (保存在当前 '3_build_model' 文件夹下)
FEATURES_OUTPUT_FILE = 'features_and_labels_eva02.npz'

# --- 2. 选择并初始化 Hugging Face / timm 模型 ---
MODEL_NAME = 'eva02_base_patch14_224.mim_in22k'
print(f"--- Initializing Pre-trained Model: {MODEL_NAME} ---")

# timm.create_model 会自动从Hugging Face Hub下载并缓存模型
# pretrained=True: 加载预训练权重
# num_classes=0: 移除最后的分类头，让模型直接输出特征向量
model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=0)

# 设置设备 (GPU优先)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()  # 切换到评估模式
print(f"Using device: {device}")

# --- 3. 获取模型的预处理配置 ---
# timm模型自带了它的预处理配置，我们直接获取，不再需要手动定义
data_config = timm.data.resolve_model_data_config(model)
transforms = timm.data.create_transform(**data_config, is_training=False)
print("\nModel preprocessing config loaded automatically.")


# --- 4. 定义一个函数来处理整个文件夹 ---
def process_folder(folder_path, label):
    features = []
    labels = []

    if not os.path.exists(folder_path):
        print(f"Warning: Directory not found, skipping: {folder_path}")
        return [], []

    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

    for filename in tqdm(image_files, desc=f"Processing '{os.path.basename(folder_path)}' folder"):
        image_path = os.path.join(folder_path, filename)
        try:
            with Image.open(image_path).convert('RGB') as img:
                # 预处理图片，并移到GPU
                input_tensor = transforms(img).unsqueeze(0).to(device)

                with torch.no_grad():
                    # 一步到位，得到特征向量
                    feature_vector = model(input_tensor)

                features.append(feature_vector.squeeze().cpu().numpy())
                labels.append(label)

        except Exception as e:
            print(f"\nError processing image {image_path}: {e}")

    return features, labels


# --- 5. 执行特征提取 ---
print(f"\n--- Extracting features from folders... ---")
good_features, good_labels = process_folder(GOOD_DIR, 1)  # "喜欢" 的标签是 1
bad_features, bad_labels = process_folder(BAD_DIR, 0)  # "不喜欢" 的标签是 0

# --- 6. 合并并保存结果 ---
if good_features and bad_features:
    all_features = np.array(good_features + bad_features)
    all_labels = np.array(good_labels + bad_labels)

    np.savez(FEATURES_OUTPUT_FILE, features=all_features, labels=all_labels)
    print(f"\n--- Feature extraction complete! ---")
    print(f"Total samples processed: {len(all_features)}")
    print(f"  - Liked samples: {len(good_features)}")
    print(f"  - Disliked samples: {len(bad_features)}")
    print(f"Saved all features and labels to '{FEATURES_OUTPUT_FILE}'.")
else:
    print("\n--- No features were extracted. Please check your folder paths and content. ---")