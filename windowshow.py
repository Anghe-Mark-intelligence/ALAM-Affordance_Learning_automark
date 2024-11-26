import os
import json
import torch
from PIL import Image, ImageTk, ImageDraw
from torchvision import transforms
import tkinter as tk
from tkinter import filedialog, messagebox

# 定义模型（需要和训练时的模型一致）
class CustomModel(torch.nn.Module):
    def __init__(self):
        super(CustomModel, self).__init__()
        self.encoder = torch.nn.Sequential(
            torch.nn.Conv2d(3, 64, kernel_size=3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.Conv2d(64, 128, kernel_size=3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
        )
        self.decoder = torch.nn.Sequential(
            torch.nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose2d(64, 1, kernel_size=2, stride=2),
            torch.nn.Sigmoid(),
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x


# 定义应用界面
class AffordanceVisualizer:
    def __init__(self, root, model_path):
        self.root = root
        self.root.title("可供性可视化界面")
        self.model_path = model_path
        self.model = self.load_model()

        # 初始化变量
        self.image_path = None
        self.json_path = None
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])

        # 界面组件
        self.create_widgets()

    def create_widgets(self):
        # 创建按钮
        self.open_button = tk.Button(self.root, text="打开图像", command=self.open_image, width=15, bg="lightblue")
        self.open_button.pack(pady=10)

        # 创建画布
        self.canvas = tk.Canvas(self.root, bg="gray", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def load_model(self):
        # 加载模型
        if not os.path.exists(self.model_path):
            messagebox.showerror("错误", f"未找到模型文件: {self.model_path}")
            return None
        try:
            model = CustomModel()  # 使用与训练时一致的模型架构
            model.load_state_dict(torch.load(self.model_path))
            model.eval()
            print("模型加载成功！")
            return model
        except Exception as e:
            messagebox.showerror("错误", f"加载模型失败: {str(e)}")
            return None

    def open_image(self):
        # 打开图像文件
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png")])
        if not self.image_path:
            return

        # 自动找到对应的 JSON 文件
        prefix = os.path.splitext(os.path.basename(self.image_path))[0]
        self.json_path = os.path.join(os.path.dirname(self.image_path), f"{prefix}.json")

        if not os.path.exists(self.json_path):
            messagebox.showerror("错误", f"未找到标注文件: {self.json_path}")
            return

        # 显示图像
        self.display_image()

    def display_image(self):
        # 打开原始图像
        orig_img = Image.open(self.image_path).convert("RGB")

        # 显示可供性标注点
        with open(self.json_path, 'r') as f:
            annotations = json.load(f)["annotations"]

        annotated_img = orig_img.copy()
        draw = ImageDraw.Draw(annotated_img)
        for point in annotations:
            x, y = point
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill="red")

        # 转换图像为 Tkinter 格式
        orig_img = orig_img.resize((400, 300), Image.ANTIALIAS)
        annotated_img = annotated_img.resize((400, 300), Image.ANTIALIAS)

        tk_orig_img = ImageTk.PhotoImage(orig_img)
        tk_annotated_img = ImageTk.PhotoImage(annotated_img)

        # 在画布上显示图像
        self.canvas.create_image(50, 150, anchor=tk.NW, image=tk_orig_img)
        self.canvas.create_image(450, 150, anchor=tk.NW, image=tk_annotated_img)

        # 防止垃圾回收
        self.canvas.image1 = tk_orig_img
        self.canvas.image2 = tk_annotated_img


# 主函数
if __name__ == "__main__":
    model_path = r"C:\Users\Administrator\Desktop\课程设计\何昂机器学习可供性学习机械臂\train_model(me)\affordance_model.pth"

    root = tk.Tk()
    app = AffordanceVisualizer(root, model_path)
    root.mainloop()
