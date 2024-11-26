import os

def list_files(directory):
    # 使用os.walk()遍历目录
    for root, dirs, files in os.walk(directory):
        # 输出当前目录
        print(f'当前目录: {root}')
        
        # 输出当前目录下的所有文件
        for file in files:
            print(f'文件: {os.path.join(root, file)}')

        # 输出当前目录下的所有子目录
        for dir in dirs:
            print(f'子目录: {os.path.join(root, dir)}')

# 设定路径
directory_path = r'C:\Users\Administrator\Desktop\机器学习可供性学习机械臂\数据'

# 调用函数
list_files(directory_path)
