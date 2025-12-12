from .BasicManager.VersionManager import VersionManager
from .CommandManager.Command import CommandExecutor

class pc:
    def __init__(self):
        self.versionManager = VersionManager()
    
    def run(self):
        print(f"{self.versionManager.getName()}")
        print(f"{self.versionManager.getVersion()}")
        self.main()
    
    def main(self):
        while True:
            userInput = input("> ")
            CE = CommandExecutor()
            CE.execute(userInput)