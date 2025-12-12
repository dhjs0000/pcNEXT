import os
import const
import bb
print("pythonc-cmd")
print("正式版1.3")
t_str = ""
t_int = ""
const.DEVELOPER = "只有一个人——“dh-js0000”"
const.VERSION = "正式版V1.3,第18个版本"+"\n"+const.DEVELOPER
while True:
    UserInput = input("pythoncmd -#")
    if UserInput == "help":
        print("ver      -h显示徽标     显示详细信息（关于）")
        print("dir   显示目录的文件  dir -c   指定目录 dir -s 显示子目录内容")
        print("python os   运行python程序")
        print("exit    直接退出")
        print("break   退出")
        print("cmd   命令提示符 cmd -start    在新窗口中启动")
        print("newfile    新建空文件")
        print("open ......  打开")
        print("powershell")
        print("fsutil  新建指定大小的空文件")
        print("openTXTfile    读取TXT")
        print("求首项是1的等差数列和(这是中文的命令)")
        print("时钟(这是中文的命令)")
        print("cald 计算器")
    #
    elif UserInput == "ver":
        bb.bb()
        print(const.VERSION)
        print("版本信息显示完毕")
    elif UserInput == "ver -h":
        bb.hb()
        print("徽标信息显示完毕")

    elif UserInput == "dir":
        os.system("dir")
    #
    elif UserInput == "dir -c":
        UserInput = input("目录：")
        os.system("dir "+UserInput)
    #
    elif UserInput == "dir -s":
        os.system("dir /s")
    #
    elif UserInput == "python os":
        print("温馨提示：请把python文件放在此文件根目录下")
        pythonlins = input("python名:")
        os.system(pythonlins)
#
    elif UserInput == "exit":
        exit()
    elif UserInput == "cald":
        os.system("cald.py")
#
    elif UserInput == "break":
        break
#
    elif UserInput == "open":
        os.system("open.py")
#
    elif UserInput == "cmd":
        os.system("cmd")
#
    elif UserInput == "newver":
        print("优化")
#
    elif UserInput == "newfile":
        UserInput = input("文件名（加后缀）：")
#
        os.system("fsutil file createnew "+UserInput+" 0")
    elif UserInput == "powershell":
        os.system("start C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe")
#
    elif UserInput == "cmd -start":
        os.system("start c:\windows\system32\cmd.exe")
#
    elif UserInput == "fsutil":
        filename_fsutil = input("文件名称")
        length = input("大小(B)")
        os.system("fsutil file createnew "+filename_fsutil+" "+str(length))
    elif UserInput == "openTXTfile":
        UserInput = input("filename:")
        #以 utf-8 的编码格式打开指定文件

        f = open(UserInput,encoding = "utf-8")

        #输出读取到的数据

        print(f.read())

        #关闭文件

        f.close()
    elif UserInput == "求首项是1的等差数列和":
        while True:
            UserInput = input("末项：")
            if str.isdigit(UserInput) == True:
                UserInput = int(UserInput)
                t_int1 = 1+UserInput
                t_int2 = UserInput - 1
                t_int3 = t_int2 / 1 + 1
                t_int = t_int1 * t_int3 / 2
                print(t_int)
                break
    elif UserInput == "时钟":
        os.system("Clock_dll.py")
    elif UserInput == "cald":
        os.system("cald.py")
    elif UserInput == "升级":
        print("正在升级,本功能仅用于测试")
        os.system("..\pc1.1python版本\pc1.1.py")
    elif UserInput == "降级":
        print("正在降级,本功能仅用于测试")
        os.system("..\pc1.0.py")
    else:
        print("您输入的",UserInput,"不是程序特定的代码")
