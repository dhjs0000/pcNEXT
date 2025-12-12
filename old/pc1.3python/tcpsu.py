import socket
import time
confirm = False
whether = False
#获取计算机ip和主机名
hostname = socket.gethostname()
lIP = socket.gethostbyname(hostname)
def s():
    print("BBYC TCP聊天工具")
    print("BBYC 2021-2023© 版权所有")
def main():
    while True:
        global hostname
        global lIP
        s()
        #询问用户IP是否正确
        import re
        print("您的局域网ip是否是"+str(lIP)+"? 如果是，请输入“是”，如果不是，输入正确的ip")
        while True:
            UserInputii = input("请输入：")
            if UserInputii == "是":
                break
            else:
                while True:
                    UserInput = input("是否想使用输入的IP进行通讯？填想或不想，返回返回：")
                    if UserInput == "想":
                        ip_pattern = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

                        if ip_pattern.match(UserInputii):
                            lIP = UserInputii
                            break
                        else:
                            print("IP地址格式错误，请重新输入")
                    elif UserInput == "返回":
                        break
                    else:
                        break
        print("您想使用您的主机名“"+hostname+"”作为昵称吗？这个昵称会在聊天时显示在前面，就像这样")
        print("<主机名>信息")
        print("您输入想设定的昵称就可以设置")
        while True:
            nn = 0
            UserInputii = input("请输入：")
            if UserInputii == "想":
                break
            else:
                while True:
                    UserInput = input("是否使用输入的昵称进行通讯？填是或否，输入返回返回：")
                    if UserInput == "是":
                        hostname = UserInputii
                        nn = 1
                        break
                    elif UserInput == "返回":
                        break
                    else:
                        pass
                if nn == 1:
                    break
            
                


        #创建套接字tcp客户端
        while True:
            try:
                client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                #连接服务器
                addr=('127.0.0.1',9999)
                addrl=()
                client.connect(addr)
                        #发送数据
                data=input('请输入发送的信息:')
                client.send(data.encode('utf8'))
                #接收服务器返回的数据
                data=client.recv(1024)
                print(data.decode())
                #关闭套接字
                client.close()
            except Exception as e:
                print("对方未开启服务器或者没有权限！")
                input("确认开启后按回车")

main()
