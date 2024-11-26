#conda create -n kegongxin python=3.6 -y
#conda activate kegongxin
import os
import random
import shutil
import json
from PIL import Image
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
import torch
import torch.nn as nn


# 自定义裁剪函数
def bottom_center_crop(img, crop_width, crop_height):
    """裁剪图片底部中间部分"""
    img_width, img_height = img.size
    left = (img_width - crop_width) // 2
    upper = img_height - crop_height
    right = left + crop_width
    lower = img_height
    return img.crop((left, upper, right, lower))


# 自定义裁剪的 Transform
class BottomCenterCrop:
    def __init__(self, crop_width, crop_height):
        self.crop_width = crop_width
        self.crop_height = crop_height

    def __call__(self, img):
        return bottom_center_crop(img, self.crop_width, self.crop_height)


# 数据路径
base_path = r"C:\Users\Administrator\Desktop\机器学习可供性学习机械臂\数据"
train_path = os.path.join(base_path, "train")
test_path = os.path.join(base_path, "test")
model_save_path = r"C:\Users\Administrator\Desktop\机器学习可供性学习机械臂\train_model(me)\affordance_model.pth"


# 自定义数据集类
class AffordanceDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.data = self._load_data()
        if len(self.data) == 0:
            print(f"警告: 数据集为空，请检查路径 {data_dir} 是否包含有效数据！")

    def _load_data(self):
        data = []
        for file in os.listdir(self.data_dir):
            if file.endswith(("o.jpg", "o.png")):  # 匹配原始图像
                prefix = file[:-5]
                orig_img_path = os.path.join(self.data_dir, f"{prefix}o.jpg")
                if not os.path.exists(orig_img_path):
                    orig_img_path = os.path.join(self.data_dir, f"{prefix}o.png")
                labeled_img_path = os.path.join(self.data_dir, f"{prefix}p.jpg")
                if not os.path.exists(labeled_img_path):
                    labeled_img_path = os.path.join(self.data_dir, f"{prefix}p.png")
                json_path = os.path.join(self.data_dir, f"{prefix}p.json")
                if os.path.exists(orig_img_path) and os.path.exists(json_path):
                    data.append((orig_img_path, labeled_img_path, json_path))
        return data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        orig_img_path, labeled_img_path, json_path = self.data[idx]

        # 加载原始图像
        orig_img = Image.open(orig_img_path).convert("RGB")
        labeled_img = Image.open(labeled_img_path).convert("L")  # 转为灰度图

        # 加载标注点
        with open(json_path, 'r') as f:
            annotations = json.load(f)["annotations"]

        if self.transform:
            orig_img = self.transform(orig_img)
            labeled_img = self.transform(labeled_img)

        # 确保标注图像是单通道
        labeled_img = labeled_img.unsqueeze(0)

        # 转换标注点为张量
        annotations = torch.tensor(annotations, dtype=torch.float32)

        return orig_img, labeled_img, annotations


# 数据预处理
transform = transforms.Compose([
    BottomCenterCrop(256, 256),  # 使用自定义底部中间裁剪
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5]),  # 单通道归一化
])

# 加载数据集
train_dataset = AffordanceDataset(train_path, transform=transform)
test_dataset = AffordanceDataset(test_path, transform=transform)

# 自定义 collate_fn
def custom_collate_fn(batch):
    images, labels, annotations = zip(*batch)
    images = torch.stack(images, dim=0)  # 合并图像张量
    labels = torch.stack(labels, dim=0)  # 合并标注图像张量
    annotations = list(annotations)  # 保留标注点为列表
    return images, labels, annotations


# 修正 DataLoader
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, collate_fn=custom_collate_fn)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False, collate_fn=custom_collate_fn)

# 检查数据是否加载成功
print(f"训练集大小: {len(train_dataset)}")
print(f"测试集大小: {len(test_dataset)}")


# 定义 U-Net 模型
class UNet(nn.Module):
    def __init__(self):
        super(UNet, self).__init__()

        # Encoder
        self.enc1 = self.conv_block(3, 64)
        self.enc2 = self.conv_block(64, 128)
        self.enc3 = self.conv_block(128, 256)
        self.enc4 = self.conv_block(256, 512)

        # Bottleneck
        self.bottleneck = self.conv_block(512, 1024)

        # Decoder
        self.up4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.dec4 = self.conv_block(1024, 512)

        self.up3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec3 = self.conv_block(512, 256)

        self.up2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = self.conv_block(256, 128)

        self.up1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = self.conv_block(128, 64)

        # Final output layer
        self.final = nn.Conv2d(64, 1, kernel_size=1)

        # Max pooling
        self.pool = nn.MaxPool2d(2)

    def conv_block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)
        enc2 = self.enc2(self.pool(enc1))
        enc3 = self.enc3(self.pool(enc2))
        enc4 = self.enc4(self.pool(enc3))

        # Bottleneck
        bottleneck = self.bottleneck(self.pool(enc4))

        # Decoder
        dec4 = self.up4(bottleneck)
        dec4 = torch.cat((dec4, enc4), dim=1)
        dec4 = self.dec4(dec4)

        dec3 = self.up3(dec4)
        dec3 = torch.cat((dec3, enc3), dim=1)
        dec3 = self.dec3(dec3)

        dec2 = self.up2(dec3)
        dec2 = torch.cat((dec2, enc2), dim=1)
        dec2 = self.dec2(dec2)

        dec1 = self.up1(dec2)
        dec1 = torch.cat((dec1, enc1), dim=1)
        dec1 = self.dec1(dec1)

        return torch.sigmoid(self.final(dec1))


# 初始化模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UNet().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.BCELoss()

# 开始训练
for epoch in range(10):  # 假设训练 10 个 epoch
    model.train()
    running_loss = 0.0
    for images, labels, annotations in train_loader:
        images, labels = images.to(device), labels.to(device)

        # 修正标签形状
        labels = labels.squeeze(1)  # 移除多余的维度

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    print(f"Epoch {epoch + 1}, Loss: {running_loss / len(train_loader)}")

# 保存模型
if not os.path.exists(os.path.dirname(model_save_path)):
    os.makedirs(os.path.dirname(model_save_path))
torch.save(model.state_dict(), model_save_path)
print(f"模型已保存到: {model_save_path}")

print("训练完成！")
