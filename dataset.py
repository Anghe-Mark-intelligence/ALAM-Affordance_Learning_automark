import os
import json
from PIL import Image
import torch
from torch.utils.data import Dataset

class AffordanceDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        """
        初始化数据集
        :param data_dir: 数据路径 (包含 o 图像、p 图像和 JSON 文件)
        :param transform: 数据预处理
        """
        self.data_dir = data_dir
        self.transform = transform
        self.data = self._load_data()

    def _load_data(self):
        """
        加载数据 (原始图像路径和标注文件)
        """
        data = []
        for file in os.listdir(self.data_dir):
            if file.endswith("o.jpg"):  # 原始图像后缀
                prefix = file.split("o.jpg")[0]
                orig_img_path = os.path.join(self.data_dir, f"{prefix}o.jpg")
                labeled_img_path = os.path.join(self.data_dir, f"{prefix}p.jpg")
                json_path = os.path.join(self.data_dir, f"{prefix}p.json")
                if os.path.exists(orig_img_path) and os.path.exists(json_path):
                    data.append((orig_img_path, labeled_img_path, json_path))
        return data

    def __len__(self):
        """
        数据集大小
        """
        return len(self.data)

    def __getitem__(self, idx):
        """
        获取单个样本
        :param idx: 索引
        :return: 原始图像，标注图像，标注点
        """
        orig_img_path, labeled_img_path, json_path = self.data[idx]
        
        # 加载原始图像
        orig_img = Image.open(orig_img_path).convert("RGB")
        
        # 加载标注图像，并转为灰度图
        labeled_img = Image.open(labeled_img_path).convert("L")  # 转为单通道灰度图

        # 加载 JSON 中的标注点
        with open(json_path, "r") as f:
            annotations = json.load(f)["annotations"]  # JSON 文件中标注点

        if self.transform:
            orig_img = self.transform(orig_img)
            labeled_img = self.transform(labeled_img)

        # 确保标注图像是单通道 (C=1, H, W)
        labeled_img = labeled_img.unsqueeze(0)  # 添加通道维度

        # 转换标注点为张量
        annotations = torch.tensor(annotations, dtype=torch.float32)

        return orig_img, labeled_img, annotations
