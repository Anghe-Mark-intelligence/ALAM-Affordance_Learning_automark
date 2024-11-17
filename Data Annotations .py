import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json
import cv2


class ImageAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("图像可供性标注工具")

        # 初始化变量
        self.image_path = None
        self.img = None
        self.tk_img = None
        self.canvas = None
        self.points = []

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 菜单栏
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="打开图片", command=self.open_image)
        file_menu.add_command(label="保存标注", command=self.save_annotations)
        menu.add_cascade(label="文件", menu=file_menu)
        self.root.config(menu=menu)

        # 画布
        self.canvas = tk.Canvas(self.root, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.add_annotation)

    def open_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*.bmp")]
        )
        if self.image_path:
            self.img = cv2.imread(self.image_path)
            self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            self.display_image()

    def display_image(self):
        # 转换图像为Tkinter格式
        pil_img = Image.fromarray(self.img)
        self.tk_img = ImageTk.PhotoImage(pil_img)

        # 更新画布
        self.canvas.config(width=self.tk_img.width(), height=self.tk_img.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

    def add_annotation(self, event):
        if self.img is None or self.img.size == 0:  # 修复条件判断
            return

        # 获取点击位置
        x, y = event.x, event.y
        self.points.append((x, y))
        print(f"标注点: {x}, {y}")

        # 在图像上标注
        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red", outline="black")

    def save_annotations(self):
        if not self.image_path:
            messagebox.showerror("错误", "未加载任何图片！")
            return

        # 自动生成 JSON 文件名，与图片路径同名但扩展名为 .json
        save_path = self.image_path.rsplit('.', 1)[0] + ".json"

        data = {
            "image_path": self.image_path,
            "annotations": self.points,
        }

        try:
            with open(save_path, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("保存成功", f"标注已保存至: {save_path}")
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存标注文件：{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageAnnotator(root)
    root.mainloop()
