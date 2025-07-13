import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision.datasets import ImageFolder
import timm
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os
from tqdm import tqdm
import numpy as np

# --- 1. 配置 ---
# 模型在Hugging Face Hub上的路径
# https://huggingface.co/timm/vit_large_patch14_reg4_dinov2.lvd142m

# model = timm.create_model('vit_large_patch14_reg4_dinov2.lvd142m', pretrained=True)

MODEL_PATH = "timm/vit_large_patch14_reg4_dinov2.lvd142m"
# 用于命名输出文件的别名
MODEL_ALIAS = "DINOv2_large_reg4"

# 数据和训练参数
DATA_DIR = 'data'
BATCH_SIZE = 4  # Large模型非常大， 我的显存不够！ 此时已经占了 12G! 所以此模型放弃！
EPOCHS = 10
LEARNING_RATE = 1e-4

# --- 2. 准备数据集 (与上一个脚本完全相同) ---
print(f"--- Preparing Datasets for {MODEL_ALIAS} ---")
model_for_preprocessing = timm.create_model(MODEL_PATH, pretrained=True)
data_config = timm.data.resolve_model_data_config(model_for_preprocessing)
train_transforms = timm.data.create_transform(**data_config, is_training=True)
val_transforms = timm.data.create_transform(**data_config, is_training=False)
del model_for_preprocessing

full_dataset = ImageFolder(DATA_DIR, transform=train_transforms)
print(f"Found {len(full_dataset)} images in {len(full_dataset.classes)} classes: {full_dataset.class_to_idx}")

train_size = int(0.8 * len(full_dataset))
val_size = len(full_dataset) - train_size
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
val_dataset.dataset.transform = val_transforms

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
print("Datasets and DataLoaders are ready.")

# --- 3. 模型构建 (与上一个脚本完全相同) ---
print(f"\n--- Building {MODEL_ALIAS} Model ---")
model = timm.create_model(MODEL_PATH, pretrained=True, num_classes=2)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print(f"Model built and moved to {device}.")

# --- 4. 训练 (与上一个脚本完全相同) ---
print(f"\n--- Starting Fine-tuning for {MODEL_ALIAS} ---")
class_counts = np.bincount(full_dataset.targets)
if class_counts.size > 1 and class_counts[0] > 0 and class_counts[1] > 0:
    class_weights = torch.tensor([max(class_counts) / class_counts[0], max(class_counts) / class_counts[1]],
                                 dtype=torch.float32).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    print(f"Using class weights to handle imbalance: {class_weights.cpu().numpy()}")
else:
    criterion = nn.CrossEntropyLoss()

optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE)
best_val_accuracy = 0.0

for epoch in range(EPOCHS):
    model.train()
    train_pbar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{EPOCHS} [Training]")
    for inputs, labels in train_pbar:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        train_pbar.set_postfix({'loss': f'{loss.item():.4f}'})

    model.eval()
    all_preds_epoch, all_labels_epoch = [], []
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            all_preds_epoch.extend(predicted.cpu().numpy())
            all_labels_epoch.extend(labels.cpu().numpy())
    val_accuracy = 100 * np.sum(np.array(all_preds_epoch) == np.array(all_labels_epoch)) / len(all_labels_epoch)
    print(f"Epoch {epoch + 1}: Val Accuracy: {val_accuracy:.2f}%")
    if val_accuracy > best_val_accuracy:
        best_val_accuracy = val_accuracy
        print(f"  -> New best model found! Saving...")
        torch.save(model.state_dict(), f'{MODEL_ALIAS}_finetuned_best.pth')

# --- 5. 最终评估与保存结果 (与上一个脚本完全相同) ---
print(f"\n--- Final Evaluation for {MODEL_ALIAS} using best model (Val Acc: {best_val_accuracy:.2f}%) ---")
model.load_state_dict(torch.load(f'{MODEL_ALIAS}_finetuned_best.pth'))
model.eval()
all_preds, all_labels = [], []
with torch.no_grad():
    for inputs, labels in val_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        _, predicted = torch.max(outputs, 1)
        all_preds.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

print(classification_report(all_labels, all_preds, target_names=full_dataset.classes, digits=4, zero_division=0))

cm = confusion_matrix(all_labels, all_preds)
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=full_dataset.classes, yticklabels=full_dataset.classes)
plt.title(f'Confusion Matrix for {MODEL_ALIAS} (Best Model)')
plot_filename = f'{MODEL_ALIAS}_confusion_matrix.png'
plt.savefig(plot_filename)
plt.close()
print(f"Confusion matrix plot saved to '{plot_filename}'")

