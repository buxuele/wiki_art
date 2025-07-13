import sys
import torch

# 检查  GPU 是否可用
ret = torch.cuda.is_available()
print(ret)
print(torch.cuda.current_device())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0))
print()

print("Python version: ", sys.version)
print("torch version: ", torch.__version__)
print("cudu version: ", torch.version.cuda)


"""输出:

安装 torch 2.5 
pip install torch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 --index-url https://download.pytorch.org/whl/cu118

True
0
1
NVIDIA GeForce RTX 3060

Python version:  3.11.1 (tags/v3.11.1:a7a450f, Dec  6 2022, 19:58:39) [MSC v.1934 64 bit (AMD64)]
torch version:  2.5.0+cu118
cudu version:  11.8

Process finished with exit code 0

"""

