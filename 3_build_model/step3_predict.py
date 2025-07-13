import torch
import timm
from PIL import Image
import os
import shutil
from tqdm import tqdm

# --- 1. 配置 (简单明了，都在当前目录下) ---
# 模型和权重路径
MODEL_PATH = "timm/vit_base_patch14_dinov2.lvd142m"
MODEL_WEIGHTS_PATH = "DINOv2_base_finetuned_best.pth"

# 输入和输出文件夹名称
INPUT_DIR = "new_images"
OUTPUT_GOOD_DIR = "pred_good"
OUTPUT_BAD_DIR = "pred_bad"

# 类别标签 (必须和训练时一致: {'bad': 0, 'good': 1})
CLASS_NAMES = ['bad', 'good']

# --- 2. 模型构建与加载 ---
print("--- Step 1: Loading the fine-tuned model ---")
model = timm.create_model(MODEL_PATH, pretrained=False, num_classes=2)
try:
    model.load_state_dict(torch.load(MODEL_WEIGHTS_PATH))
except FileNotFoundError:
    print(f"FATAL ERROR: Model weights '{MODEL_WEIGHTS_PATH}' not found.")
    exit()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()
print(f"Model loaded successfully on {device}.")

# --- 3. 准备预处理流程 ---
data_config = timm.data.resolve_model_data_config(model)
transforms = timm.data.create_transform(**data_config, is_training=False)
print("Preprocessing transforms are ready.")

# --- 4. 准备文件夹 ---
print("\n--- Step 2: Preparing input and output directories ---")
# 确保输入文件夹存在
if not os.path.exists(INPUT_DIR):
    print(f"INFO: Input directory '{INPUT_DIR}' not found. Creating it for you.")
    os.makedirs(INPUT_DIR)
    print(f"Please put the images you want to predict into the '{INPUT_DIR}' folder and run again.")
    exit()

# 创建(或清空)输出文件夹
for dir_path in [OUTPUT_GOOD_DIR, OUTPUT_BAD_DIR]:
    if os.path.exists(dir_path):
        # 清空文件夹，以便每次运行都是全新的结果
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)
print(f"Output directories '{OUTPUT_GOOD_DIR}' and '{OUTPUT_BAD_DIR}' are ready.")

# --- 5. 核心流程：批量预测与自动分拣 ---
print("\n--- Step 3: Starting batch prediction and sorting ---")
image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

if not image_files:
    print(f"No images found in '{INPUT_DIR}'. Nothing to do.")
    exit()

good_count = 0
bad_count = 0

with torch.no_grad():
    for filename in tqdm(image_files, desc="Predicting images"):
        image_path = os.path.join(INPUT_DIR, filename)
        try:
            with Image.open(image_path).convert('RGB') as img:
                input_tensor = transforms(img).unsqueeze(0).to(device)
                outputs = model(input_tensor)

                # 获取预测结果
                _, predicted_idx = torch.max(outputs, 1)
                predicted_class_name = CLASS_NAMES[predicted_idx.item()]

                # 根据预测结果，移动文件
                if predicted_class_name == 'good':
                    shutil.move(image_path, os.path.join(OUTPUT_GOOD_DIR, filename))
                    good_count += 1
                else:  # 'bad'
                    shutil.move(image_path, os.path.join(OUTPUT_BAD_DIR, filename))
                    bad_count += 1
        except Exception as e:
            print(f"\nError processing file {filename}: {e}")

# --- 6. 输出最终报告 ---
print("\n" + "=" * 50)
print("         BATCH PREDICTION SUMMARY")
print("=" * 50)
print(f"Total images processed: {len(image_files)}")
print(f"Moved to '{OUTPUT_GOOD_DIR}': {good_count} images")
print(f"Moved to '{OUTPUT_BAD_DIR}': {bad_count} images")
print("=" * 50)
print("Prediction process complete.")