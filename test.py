import torch
from your_model_file import YourModelClass  # 替换为实际的模型类和文件

# 初始化模型
model = YourModelClass()

# 加载模型权重
model.load_state_dict(torch.load("C:\\Users\\Administrator\\Desktop\\机器学习可供性学习机械臂\\trained_models\\policy\\tabletop\\vapo\\trained_models\\most_tasks_from_15.pth"))

# 将模型设为评估模式
model.eval()
