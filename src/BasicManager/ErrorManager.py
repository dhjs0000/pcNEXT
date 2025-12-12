"""
错误管理器 - 统一管理所有模拟器错误
错误码范围：0-1024
分配规则：
0-99:   系统级错误
100-199: 文件系统错误  
200-299: 命令执行错误
300-399: 参数解析错误
400-499: 配置错误
500-599: 权限错误
600-699: 网络错误
700-799: 内存错误
800-899: 插件错误
900-999: 用户操作错误
1000-1024: 保留错误
"""

class PythonCMDError(Exception):
    """基础错误类"""
    def __init__(self, code, message, details=None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(f"[{code}] {message}" + (f": {details}" if details else ""))

class SystemError(PythonCMDError):
    """系统级错误 (0-99)"""
    pass

class FileSystemError(PythonCMDError):
    """文件系统错误 (100-199)"""
    pass

class CommandError(PythonCMDError):
    """命令执行错误 (200-299)"""
    pass

class ArgumentError(PythonCMDError):
    """参数解析错误 (300-399)"""
    pass

class ConfigError(PythonCMDError):
    """配置错误 (400-499)"""
    pass

class PermissionError(PythonCMDError):
    """权限错误 (500-599)"""
    pass

class NetworkError(PythonCMDError):
    """网络错误 (600-699)"""
    pass

class MemoryError(PythonCMDError):
    """内存错误 (700-799)"""
    pass

class PluginError(PythonCMDError):
    """插件错误 (800-899)"""
    pass

class UserError(PythonCMDError):
    """用户操作错误 (900-999)"""
    pass

class ErrorCodes:
    """错误码定义"""
    
    # 系统级错误 (0-99)
    SUCCESS = 0
    UNKNOWN_ERROR = 1
    INITIALIZATION_FAILED = 2
    SHUTDOWN_FAILED = 3
    RESOURCE_NOT_FOUND = 4
    OPERATION_TIMEOUT = 5
    SYSTEM_BUSY = 6
    VERSION_MISMATCH = 7
    DEPENDENCY_MISSING = 8
    ENVIRONMENT_ERROR = 9
    
    # 文件系统错误 (100-199)
    FILE_NOT_FOUND = 100
    DIRECTORY_NOT_FOUND = 101
    FILE_ACCESS_DENIED = 102
    DIRECTORY_ACCESS_DENIED = 103
    FILE_READ_ERROR = 104
    FILE_WRITE_ERROR = 105
    FILE_CREATE_ERROR = 106
    FILE_DELETE_ERROR = 107
    FILE_COPY_ERROR = 108
    FILE_MOVE_ERROR = 109
    DIRECTORY_CREATE_ERROR = 110
    DIRECTORY_DELETE_ERROR = 111
    PATH_TOO_LONG = 112
    INVALID_PATH = 113
    DISK_FULL = 114
    FILE_CORRUPTED = 115
    FILE_LOCKED = 116
    FILE_EXISTS = 117
    DIRECTORY_EXISTS = 118
    FILE_NOT_DIRECTORY = 119
    DIRECTORY_NOT_FILE = 120
    
    # 命令执行错误 (200-299)
    COMMAND_NOT_FOUND = 200
    COMMAND_EXECUTION_FAILED = 201
    COMMAND_SYNTAX_ERROR = 202
    COMMAND_PERMISSION_DENIED = 203
    COMMAND_TIMEOUT = 204
    COMMAND_INTERRUPTED = 205
    COMMAND_NOT_IMPLEMENTED = 206
    COMMAND_DEPRECATED = 207
    COMMAND_CONFLICT = 208
    COMMAND_CYCLIC_DEPENDENCY = 209
    INVALID_COMMAND = 210
    COMMAND_USAGE_ERROR = 211
    
    # 参数解析错误 (300-399)
    MISSING_ARGUMENT = 300
    TOO_MANY_ARGUMENTS = 301
    INVALID_ARGUMENT_TYPE = 302
    INVALID_ARGUMENT_FORMAT = 303
    ARGUMENT_OUT_OF_RANGE = 304
    REQUIRED_ARGUMENT_MISSING = 305
    OPTIONAL_ARGUMENT_ERROR = 306
    FLAG_CONFLICT = 307
    UNKNOWN_OPTION = 308
    INVALID_OPTION_VALUE = 309
    PARAMETER_VALIDATION_FAILED = 310
    
    # 配置错误 (400-499)
    CONFIG_FILE_NOT_FOUND = 400
    CONFIG_FILE_INVALID = 401
    CONFIG_PARSE_ERROR = 402
    CONFIG_VALUE_INVALID = 403
    CONFIG_MISSING_REQUIRED = 404
    CONFIG_TYPE_MISMATCH = 405
    CONFIG_DEPRECATED = 406
    CONFIG_CONFLICT = 407
    CONFIG_PERMISSION_DENIED = 408
    CONFIG_BACKUP_FAILED = 409
    CONFIG_RESTORE_FAILED = 410
    
    # 权限错误 (500-599)
    PERMISSION_DENIED = 500
    INSUFFICIENT_PRIVILEGES = 501
    ACCESS_FORBIDDEN = 502
    AUTHENTICATION_FAILED = 503
    AUTHORIZATION_FAILED = 504
    SESSION_EXPIRED = 505
    TOKEN_INVALID = 506
    PASSWORD_INCORRECT = 507
    ACCOUNT_LOCKED = 508
    ACCOUNT_DISABLED = 509
    
    # 网络错误 (600-699)
    NETWORK_CONNECTION_FAILED = 600
    NETWORK_TIMEOUT = 601
    NETWORK_DISCONNECTED = 602
    HOST_NOT_FOUND = 603
    PORT_UNAVAILABLE = 604
    PROTOCOL_ERROR = 605
    NETWORK_PERMISSION_DENIED = 606
    CONNECTION_REFUSED = 607
    CONNECTION_RESET = 608
    NETWORK_UNREACHABLE = 609
    
    # 内存错误 (700-799)
    OUT_OF_MEMORY = 700
    MEMORY_ALLOCATION_FAILED = 701
    MEMORY_LEAK_DETECTED = 702
    MEMORY_CORRUPTION = 703
    MEMORY_ACCESS_VIOLATION = 704
    STACK_OVERFLOW = 705
    HEAP_CORRUPTION = 706
    
    # 插件错误 (800-899)
    PLUGIN_LOAD_FAILED = 800
    PLUGIN_INIT_FAILED = 801
    PLUGIN_NOT_FOUND = 802
    PLUGIN_VERSION_MISMATCH = 803
    PLUGIN_DEPENDENCY_MISSING = 804
    PLUGIN_CONFLICT = 805
    PLUGIN_PERMISSION_DENIED = 806
    PLUGIN_EXECUTION_FAILED = 807
    PLUGIN_UNLOAD_FAILED = 808
    
    # 用户操作错误 (900-999)
    USER_CANCELLED = 900
    USER_INPUT_INVALID = 901
    USER_CONFIRMATION_FAILED = 902
    USER_TIMEOUT = 903
    OPERATION_ABORTED = 904
    INVALID_USER_INPUT = 905
    USER_NOT_FOUND = 906
    USER_ALREADY_EXISTS = 907

class ErrorManager:
    """错误管理器"""
    
    def __init__(self):
        self.error_count = 0
        self.error_history = []
    
    def raise_error(self, error_class, code, message, details=None):
        """抛出错误"""
        self.error_count += 1
        error = error_class(code, message, details)
        self.error_history.append({
            'code': code,
            'message': message,
            'details': details,
            'timestamp': __import__('time').time()
        })
        print(error)
    
    def log_error(self, code, message, details=None):
        """记录错误但不抛出"""
        self.error_count += 1
        self.error_history.append({
            'code': code,
            'message': message,
            'details': details,
            'timestamp': __import__('time').time()
        })
    
    def get_error_count(self):
        """获取错误总数"""
        return self.error_count
    
    def get_error_history(self):
        """获取错误历史"""
        return self.error_history.copy()
    
    def clear_error_history(self):
        """清空错误历史"""
        self.error_history.clear()
    
    def format_error_message(self, code, message, details=None):
        """格式化错误信息"""
        error_type = self.get_error_type(code)
        base_msg = f"[{code}] {error_type}: {message}"
        if details:
            return f"{base_msg} ({details})"
        return base_msg
    
    def get_error_type(self, code):
        """根据错误码获取错误类型"""
        if 0 <= code <= 99:
            return "SYSTEM"
        elif 100 <= code <= 199:
            return "FILE_SYSTEM"
        elif 200 <= code <= 299:
            return "COMMAND"
        elif 300 <= code <= 399:
            return "ARGUMENT"
        elif 400 <= code <= 499:
            return "CONFIG"
        elif 500 <= code <= 599:
            return "PERMISSION"
        elif 600 <= code <= 699:
            return "NETWORK"
        elif 700 <= code <= 799:
            return "MEMORY"
        elif 800 <= code <= 899:
            return "PLUGIN"
        elif 900 <= code <= 999:
            return "USER"
        else:
            return "UNKNOWN"

# 全局错误管理器实例
error_manager = ErrorManager()

# 便捷的错误输出函数（直接打印错误，不抛出异常）
def raise_system_error(code, message, details=None):
    """系统错误 - 直接输出错误信息"""
    error = SystemError(code, message, details)
    error_manager.log_error(code, message, details)
    print(error_manager.format_error_message(code, message, details))
    return error

def raise_filesystem_error(code, message, details=None):
    """文件系统错误 - 直接输出错误信息"""
    error = FileSystemError(code, message, details)
    error_manager.log_error(code, message, details)
    print(error_manager.format_error_message(code, message, details))
    return error

def raise_command_error(code, message, details=None):
    """命令错误 - 直接输出错误信息"""
    error = CommandError(code, message, details)
    error_manager.log_error(code, message, details)
    print(error_manager.format_error_message(code, message, details))
    return error

def raise_argument_error(code, message, details=None):
    """参数错误 - 直接输出错误信息"""
    error = ArgumentError(code, message, details)
    error_manager.log_error(code, message, details)
    print(error_manager.format_error_message(code, message, details))
    return error

def raise_config_error(code, message, details=None):
    """配置错误 - 直接输出错误信息"""
    error = ConfigError(code, message, details)
    error_manager.log_error(code, message, details)
    print(error_manager.format_error_message(code, message, details))
    return error

def raise_permission_error(code, message, details=None):
    """权限错误 - 直接输出错误信息"""
    error = PermissionError(code, message, details)
    error_manager.log_error(code, message, details)
    print(error_manager.format_error_message(code, message, details))
    return error

def raise_network_error(code, message, details=None):
    """网络错误 - 直接输出错误信息"""
    error = NetworkError(code, message, details)
    error_manager.log_error(code, message, details)
    print(error_manager.format_error_message(code, message, details))
    return error

def raise_memory_error(code, message, details=None):
    """内存错误 - 直接输出错误信息"""
    error = MemoryError(code, message, details)
    error_manager.log_error(code, message, details)
    print(error_manager.format_error_message(code, message, details))
    return error

def raise_plugin_error(code, message, details=None):
    """插件错误 - 直接输出错误信息"""
    error = PluginError(code, message, details)
    error_manager.log_error(code, message, details)
    print(error_manager.format_error_message(code, message, details))
    return error

def raise_user_error(code, message, details=None):
    """用户错误 - 直接输出错误信息"""
    error = UserError(code, message, details)
    error_manager.log_error(code, message, details)
    print(error_manager.format_error_message(code, message, details))
    return error