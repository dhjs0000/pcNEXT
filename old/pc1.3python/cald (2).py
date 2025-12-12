import tkinter as tk

# 计算器按钮的点击事件处理函数
def button_click(num):
    current = entry.get()
    entry.delete(0, tk.END)
    entry.insert(tk.END, current + str(num))

def button_clear():
    entry.delete(0, tk.END)

def button_equal():
    try:
        result = eval(entry.get())
        entry.delete(0, tk.END)
        entry.insert(tk.END, result)
    except:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Error")

# 创建主窗口
window = tk.Tk()
window.title("计算器")

# 创建文本框
entry = tk.Entry(window, width=30)
entry.grid(row=0, column=0, columnspan=4)

# 创建按钮
button1 = tk.Button(window, text="1", width=8, command=lambda: button_click(1))
button1.grid(row=1, column=0)
button2 = tk.Button(window, text="2", width=8, command=lambda: button_click(2))
button2.grid(row=1, column=1)
button3 = tk.Button(window, text="3", width=8, command=lambda: button_click(3))
button3.grid(row=1, column=2)
button_add = tk.Button(window, text="+", width=8, command=lambda: button_click("+"))
button_add.grid(row=1, column=3)

button4 = tk.Button(window, text="4", width=8, command=lambda: button_click(4))
button4.grid(row=2, column=0)
button5 = tk.Button(window, text="5", width=8, command=lambda: button_click(5))
button5.grid(row=2, column=1)
button6 = tk.Button(window, text="6", width=8, command=lambda: button_click(6))
button6.grid(row=2, column=2)
button_sub = tk.Button(window, text="-", width=8, command=lambda: button_click("-"))
button_sub.grid(row=2, column=3)

button7 = tk.Button(window, text="7", width=8, command=lambda: button_click(7))
button7.grid(row=3, column=0)
button8 = tk.Button(window, text="8", width=8, command=lambda: button_click(8))
button8.grid(row=3, column=1)
button9 = tk.Button(window, text="9", width=8, command=lambda: button_click(9))
button9.grid(row=3, column=2)
button_mult = tk.Button(window, text="*", width=8, command=lambda: button_click("*"))
button_mult.grid(row=3, column=3)

button0 = tk.Button(window, text="0", width=8, command=lambda: button_click(0))
button0.grid(row=4, column=0)
button_clear = tk.Button(window, text="清除", width=8, command=button_clear)
button_clear.grid(row=4, column=1)
button_equal = tk.Button(window, text="=", width=8, command=button_equal)
button_equal.grid(row=4, column=2)
button_div = tk.Button(window, text="/", width=8, command=lambda: button_click("/"))
button_div.grid(row=4, column=3)
# 设置窗口不可缩放
window.resizable(False, False)
# 主循环
window.mainloop()
