import tomllib

class VersionManager:
    def __init__(self, versionPath = "version.toml"):
        self.Name = ""
        self.Version = ""
        self.versionPath = versionPath
        self.meta = {}
    
    def openVersionFile(self):
        import os
        # 获取项目根目录路径
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # 构建完整的文件路径
        full_path = os.path.join(root_path, self.versionPath)
        with open(full_path, "rb") as file:
            self.meta = tomllib.load(file)

    def updateVersionInfo(self):
        self.Name = self.meta["VersionInfo"]["Name"]
        self.Version = self.meta["VersionInfo"]["Version"]
    
    def getVersionInfo(self):
        self.openVersionFile()
        self.updateVersionInfo()
        return self.Name,self.Version

    def getName(self):
        self.openVersionFile()
        self.updateVersionInfo()
        return self.Name
    
    def getVersion(self):
        self.openVersionFile()
        self.updateVersionInfo()
        return self.Version