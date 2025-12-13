from .BasicManager.VersionManager import VersionManager
from .CommandManager.Command import CommandExecutor

import os

class pc:
    def __init__(self):
        self.versionManager = VersionManager()
    
    def run(self):
        print(f"{self.versionManager.getName()}")
        print(f"{self.versionManager.getVersion()}")
        self.main()
    
    def main(self):
        """
        主函数，持续接收用户输入并执行命令
        包含异常处理，处理键盘中断和其他未知错误
        """
        while True:
            try:
                # 显示工作目录
                directory = os.getcwd()
                if os.name == 'nt':
                    print(f"PC {directory}\\ > ", end="")
                else:
                    print(f"PC {directory}/ > ", end="")
                userInput = input("")
                CE = CommandExecutor()
                CE.execute(userInput)
            except KeyboardInterrupt:
                print("^C")
            except Exception as e:
                print(f"Unknown Error: {e}")