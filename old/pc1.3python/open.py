# 导入必要的模块
import os
import tkinter as tk
from tkinter import filedialog

# 定义打开文件的函数
def open_file(file_path):
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 在默认应用程序中打开文件
        os.startfile(file_path)
    else:
        print("文件不存在")

def browse_file():
    # 使用文件对话框获取文件路径
    file_path = filedialog.askopenfilename()

    # 调用打开文件的函数
    try:
        open_file(file_path)
    except SyntaxError:
        print("无效的十进制字面量")

# 创建图形化界面
root = tk.Tk()
root.title("文件浏览器")

# 设置窗口大小
root.geometry("300x200")

# 添加标签
label = tk.Label(root, text="请选择要打开的文件：")
label.pack(pady=10)

# 添加按钮
browse_button = tk.Button(root, text="浏览文件", command=browse_file)
browse_button.pack(pady=10)

# 运行界面
root.mainloop()
