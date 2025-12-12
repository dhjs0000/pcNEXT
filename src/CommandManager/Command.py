import os
import json
import re
import shlex
from ..BasicManager.VersionManager import VersionManager
from ..BasicManager.ErrorManager import (
    ErrorCodes, error_manager, PythonCMDError,
    raise_filesystem_error, raise_command_error,
    raise_argument_error, raise_permission_error,
    raise_config_error, raise_system_error
)

class Commands:
    """命令实现类"""
    
    def __init__(self, executor=None):
        """
        初始化命令类
        :param executor: CommandExecutor实例的引用
        """
        self.executor = executor
        self.versionManager = VersionManager()
    
    def help(self):
        """显示所有可用命令"""
        if not self.executor:
            raise_command_error(ErrorCodes.COMMAND_EXECUTION_FAILED, "无法获取命令列表", "executor实例未初始化")
        
        print("可用命令：")
        for cmd in self.executor.commands_config:
            params = cmd.get('para', '')
            if isinstance(params, list):
                params_str = ' '.join([f'<{p}>' for p in params])
            elif params == '*argv':
                params_str = '<arg1> [arg2] ...'
            else:
                params_str = f'<{params}>' if params else ''
            
            print(f"  {cmd['cmd']} {params_str} - {cmd['info']}")
    
    def echo(self, *text):
        """回显所有参数（支持无限参数）"""
        print(' '.join(map(str, text)))
    
    def add(self, a, b):
        """计算两个数字的和"""
        try:
            result = float(a) + float(b)
            print(f"{a} + {b} = {result}")
        except ValueError:
            raise_argument_error(ErrorCodes.INVALID_ARGUMENT_TYPE, "参数类型错误", f"无法将 '{a}' 或 '{b}' 转换为数字")
    
    def config(self, key, value=None):
        """查看或设置配置项"""
        if not key:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "配置项键不能为空", "config命令需要指定配置项的键")
        
        if value is None:
            print(f"获取配置项: {key}")
        else:
            print(f"设置配置: {key} = {value}")

    def version(self):
        """显示当前版本信息"""
        try:
            version = self.versionManager.getVersion()
            name = self.versionManager.getName()
            print(f"版本: {version}")
            print(f"名称: {name}")
        except Exception as e:
            raise_system_error(ErrorCodes.INITIALIZATION_FAILED, "无法获取版本信息", str(e))
    
    def clear(self):
        """清空控制台"""
        try:
            result = os.system('cls' if os.name == 'nt' else 'clear')
            if result != 0:
                raise_system_error(ErrorCodes.COMMAND_EXECUTION_FAILED, "清空控制台失败", f"系统命令返回码: {result}")
        except Exception as e:
            raise_system_error(ErrorCodes.COMMAND_EXECUTION_FAILED, "清空控制台失败", str(e))
    
    def exit(self):
        """退出程序"""
        try:
            print("正在退出程序...")
            os._exit(0)
        except Exception as e:
            raise_system_error(ErrorCodes.SHUTDOWN_FAILED, "程序退出失败", str(e))

    def ls(self, *args):
        """列出目录内容（类似Linux ls命令）"""
        import time
        
        # 解析参数
        show_details = False
        show_all = False
        reverse_sort = False
        sort_by_time = False
        sort_by_size = False
        paths = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith('-'):
                # 处理选项
                if arg == '-l':
                    show_details = True
                elif arg == '-a':
                    show_all = True
                elif arg == '-r':
                    reverse_sort = True
                elif arg == '-t':
                    sort_by_time = True
                elif arg == '-S':
                    sort_by_size = True
                elif arg == '-la' or arg == '-al':
                    show_details = True
                    show_all = True
                elif arg.startswith('--'):
                    # 长选项
                    if arg == '--help':
                        print("用法: ls [选项]... [文件]...")
                        print("列出目录内容")
                        print()
                        print("选项:")
                        print("  -l            使用详细格式列表")
                        print("  -a            显示所有文件（包括隐藏文件）")
                        print("  -r            反向排序")
                        print("  -t            按修改时间排序")
                        print("  -S            按文件大小排序")
                        print("  --help        显示此帮助信息")
                        return
                    else:
                        raise_argument_error(ErrorCodes.UNKNOWN_OPTION, f"无法识别的选项 '{arg}'", "请使用 'ls --help' 获取帮助信息")
                else:
                    # 处理组合选项如 -la
                    for char in arg[1:]:
                        if char == 'l':
                            show_details = True
                        elif char == 'a':
                            show_all = True
                        elif char == 'r':
                            reverse_sort = True
                        elif char == 't':
                            sort_by_time = True
                        elif char == 'S':
                            sort_by_size = True
                        else:
                            raise_argument_error(ErrorCodes.INVALID_OPTION_VALUE, f"无效选项 -- '{char}'")
            else:
                # 路径参数
                paths.append(arg)
            i += 1
        
        # 如果没有指定路径，使用当前目录
        if not paths:
            paths = ['.']
        
        # 处理每个路径
        for path_idx, path in enumerate(paths):
            if len(paths) > 1:
                if path_idx > 0:
                    print()
                print(f"{path}:")
            
            try:
                entries = os.listdir(path)
                
                # 过滤隐藏文件
                if not show_all:
                    entries = [e for e in entries if not e.startswith('.')]
                
                # 获取文件信息
                entries_info = []
                for entry in entries:
                    full_path = os.path.join(path, entry)
                    try:
                        stat_info = os.stat(full_path)
                        entries_info.append({
                            'name': entry,
                            'is_dir': os.path.isdir(full_path),
                            'size': stat_info.st_size,
                            'mtime': stat_info.st_mtime,
                            'mode': stat_info.st_mode
                        })
                    except (OSError, PermissionError):
                        entries_info.append({
                            'name': entry,
                            'is_dir': os.path.isdir(full_path),
                            'size': 0,
                            'mtime': 0,
                            'mode': 0
                        })
                
                # 排序
                if sort_by_time:
                    entries_info.sort(key=lambda x: x['mtime'], reverse=not reverse_sort)
                elif sort_by_size:
                    entries_info.sort(key=lambda x: x['size'], reverse=not reverse_sort)
                else:
                    # 默认按名称排序，目录在前
                    entries_info.sort(key=lambda x: (not x['is_dir'], x['name'].lower()),
                                    reverse=reverse_sort)
                
                # 显示结果
                if show_details:
                    # 详细格式
                    total_blocks = len(entries_info)
                    print(f"总计: {total_blocks}")
                    
                    for info in entries_info:
                        name = info['name']
                        if info['is_dir']:
                            name += '/'
                        
                        if info['mode'] == 0:
                            # 无法获取详细信息
                            error_manager.log_error(ErrorCodes.FILE_READ_ERROR, f"无法读取文件信息: {name}", "权限不足或文件系统错误")
                            print(f"?{'?'*9} {'?':>8} {'?':>12} {name}")
                        else:
                            # 文件类型和权限
                            file_type = 'd' if info['is_dir'] else '-'
                            perms = []
                            perms.append('r' if info['mode'] & 0o400 else '-')
                            perms.append('w' if info['mode'] & 0o200 else '-')
                            perms.append('x' if info['mode'] & 0o100 else '-')
                            perms.append('r' if info['mode'] & 0o040 else '-')
                            perms.append('w' if info['mode'] & 0o020 else '-')
                            perms.append('x' if info['mode'] & 0o010 else '-')
                            perms.append('r' if info['mode'] & 0o004 else '-')
                            perms.append('w' if info['mode'] & 0o002 else '-')
                            perms.append('x' if info['mode'] & 0o001 else '-')
                            
                            perm_str = ''.join(perms)
                            
                            # 文件大小（人性化显示）
                            size = info['size']
                            if size < 1024:
                                size_str = str(size)
                            elif size < 1024 * 1024:
                                size_str = f"{size/1024:.1f}K"
                            elif size < 1024 * 1024 * 1024:
                                size_str = f"{size/(1024*1024):.1f}M"
                            else:
                                size_str = f"{size/(1024*1024*1024):.1f}G"
                            
                            # 修改时间
                            time_str = time.strftime('%b %d %H:%M', time.localtime(info['mtime']))
                            
                            print(f"{file_type}{perm_str} {size_str:>8} {time_str} {name}")
                else:
                    # 简单格式 - 纯文件名，目录在前，按字母排序
                    dirs = [info['name'] + '/' for info in entries_info if info['is_dir']]
                    files = [info['name'] for info in entries_info if not info['is_dir']]
                    
                    # 每行显示多个，自动换行
                    all_entries = dirs + files
                    if all_entries:
                        # 计算合适的列宽
                        max_len = max(len(name) for name in all_entries)
                        col_width = max_len + 2
                        terminal_width = 80  # 默认终端宽度
                        
                        cols = max(1, terminal_width // col_width)
                        
                        for i, name in enumerate(all_entries):
                            print(f"{name:<{col_width}}", end='')
                            if (i + 1) % cols == 0:
                                print()
                        if len(all_entries) % cols != 0:
                            print()
                    
            except FileNotFoundError:
                raise_filesystem_error(ErrorCodes.DIRECTORY_NOT_FOUND, f"无法访问 '{path}'", "没有那个文件或目录")
            except PermissionError:
                raise_permission_error(ErrorCodes.DIRECTORY_ACCESS_DENIED, f"无法打开目录 '{path}'", "权限不够")
            except Exception as e:
                raise_filesystem_error(ErrorCodes.FILE_ACCESS_DENIED, f"无法访问 '{path}'", str(e))

    def test_func(self, required1, optional1=None, required2=None):
        """测试命令：混合必需和可选参数"""
        print(f"必需参数1: {required1}")
        if optional1 is not None:
            print(f"可选参数1: {optional1}")
        if required2 is not None:
            print(f"必需参数2: {required2}")

    def copy_func(self, source=None, destination=None):
        """复制文件：所有参数都是可选的"""
        if source is None and destination is None:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请提供源文件和目标文件", "copy命令需要指定源文件和目标文件")
            return
        if source is None:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请提供源文件", "必须指定要复制的源文件")
            return
        if destination is None:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请提供目标文件", "必须指定目标文件路径")
            return
        print(f"复制文件: {source} -> {destination}")

class CommandExecutor:
    """命令执行器"""
    
    def __init__(self, json_filename='Commands.json'):
        # 获取当前脚本所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 构建JSON文件的绝对路径
        json_path = os.path.join(current_dir, json_filename)
        
        # 加载配置
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.commands_config = json.load(f)
        except FileNotFoundError:
            error_msg = f"找不到配置文件: {json_path}"
            details = f"当前工作目录: {os.getcwd()}, 脚本所在目录: {current_dir}"
            raise_filesystem_error(ErrorCodes.CONFIG_FILE_NOT_FOUND, error_msg, details)
        except json.JSONDecodeError as e:
            error_msg = f"配置文件格式错误: {json_path}"
            raise_config_error(ErrorCodes.CONFIG_FILE_INVALID, error_msg, str(e))
        
        # 创建命令映射
        self.command_map = {cmd['cmd']: cmd for cmd in self.commands_config}
        
        # 命令实例（传递self引用）
        self.commands_instance = Commands(self)
    
    def parse_arguments(self, param_config, input_params):
        """智能参数解析器"""
        if not param_config:
            return []
        
        if input_params.strip():
            params = shlex.split(input_params)
        else:
            params = []
        
        if param_config == '*argv':
            return params
        
        if isinstance(param_config, list):
            # 处理可选参数（中括号格式）
            required_params = []
            optional_params = []
            
            for p in param_config:
                if p.startswith('[') and p.endswith(']'):
                    optional_params.append(p[1:-1])  # 去掉中括号
                else:
                    required_params.append(p)
            
            # 检查必需参数
            if len(params) < len(required_params):
                raise ValueError(f"参数不足，至少需要 {len(required_params)} 个参数")
            
            # 返回所有参数（包括可选的）
            return params
        
        # 处理单个可选参数（中括号格式）
        if isinstance(param_config, str) and param_config.startswith('[') and param_config.endswith(']'):
            return params  # 可选参数，返回所有提供的参数
        
        if not params:
            raise ValueError("需要参数")
        return params[:1]
    
    def execute(self, input_str):
        """执行命令"""
        if not input_str.strip():
            return
        
        parts = input_str.split(maxsplit=1)
        cmd_name = parts[0]
        params_str = parts[1] if len(parts) > 1 else ""
        
        if cmd_name not in self.command_map:
            error_manager.log_error(ErrorCodes.COMMAND_NOT_FOUND, f"未知命令: {cmd_name}")
            error_msg = error_manager.format_error_message(
                ErrorCodes.COMMAND_NOT_FOUND,
                f"未知命令: {cmd_name}",
                f"请使用 'help' 命令查看可用命令列表"
            )
            print(error_msg)
            return
        
        config = self.command_map[cmd_name]
        
        # 提取方法名
        func_str = config.get('func', '')
        method_name = re.match(r'(\w+)', func_str).group(1)
        
        # 获取方法
        method = getattr(self.commands_instance, method_name, None)
        if not method or not callable(method):
            error_msg = f"方法 {method_name} 未实现"
            details = f"命令 '{cmd_name}' 对应的执行方法不存在"
            raise_command_error(ErrorCodes.COMMAND_NOT_IMPLEMENTED, error_msg, details)
        
        # 解析参数配置
        param_config = config.get('para', '')
        
        try:
            # 解析参数
            args = self.parse_arguments(param_config, params_str)
            
            # 动态调用方法
            method(*args)
            
        except ValueError as e:
            error_msg = "参数解析错误"
            details = str(e)
            error_manager.log_error(ErrorCodes.INVALID_ARGUMENT_FORMAT, error_msg, details)
            formatted_msg = error_manager.format_error_message(
                ErrorCodes.INVALID_ARGUMENT_FORMAT,
                error_msg,
                details
            )
            print(formatted_msg)
            self._show_usage(config)
        except PythonCMDError as e:
            # 捕获并显示错误，不抛出
            error_manager.log_error(e.code, e.message, e.details)
            formatted_msg = error_manager.format_error_message(e.code, e.message, e.details)
            print(formatted_msg)
        except Exception as e:
            error_msg = "命令执行失败"
            details = f"执行命令 '{cmd_name}' 时发生未知错误"
            error_manager.log_error(ErrorCodes.COMMAND_EXECUTION_FAILED, error_msg, details)
            formatted_msg = error_manager.format_error_message(
                ErrorCodes.COMMAND_EXECUTION_FAILED,
                error_msg,
                details
            )
            print(formatted_msg)
    
    def _show_usage(self, config):
        """显示命令用法"""
        cmd = config['cmd']
        params = config.get('para', '')
        
        if isinstance(params, list):
            params_list = []
            for p in params:
                if p.startswith('[') and p.endswith(']'):
                    # 中括号格式可选参数
                    params_list.append(f'[{p[1:-1]}]')
                elif p.startswith('?'):
                    # 旧的问号格式可选参数（向后兼容）
                    params_list.append(f'[{p[1:]}]')
                else:
                    params_list.append(f'<{p}>')
            params_str = ' '.join(params_list)
        elif isinstance(params, str) and params.startswith('[') and params.endswith(']'):
            # 单个可选参数
            params_str = f'[{params[1:-1]}]'
        elif params == '*argv':
            params_str = '<arg1> [arg2] ...'
        elif params:
            params_str = f'<{params}>'
        else:
            params_str = ''
        
        print(f"INFO: 用法: {cmd} {params_str}")