import os
import json
import re
import shlex
import sys
import time
import subprocess
import platform
import shutil
import getpass
from collections import deque
from ..BasicManager.VersionManager import VersionManager
from ..BasicManager.ErrorManager import (
    ErrorCodes, error_manager, PythonCMDError,
    raise_filesystem_error, raise_command_error,
    raise_argument_error, raise_permission_error,
    raise_config_error, raise_system_error
)

class Commands:
    """命令实现类"""
    
    def _read_file(self, path, fallback_encoding='gbk'):
        """内部工具：自动处理编码fallback的生成器"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                yield from f
        except UnicodeDecodeError:
            with open(path, 'r', encoding=fallback_encoding) as f:
                yield from f
    
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

    def run(self, *args):
        """运行可执行文件（支持PATH路径和当前目录）"""
        import subprocess
        import platform
        
        if not args:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请指定要运行的可执行文件", "run命令需要指定可执行文件路径")
            return
        
        executable = args[0]
        run_args = list(args[1:]) if len(args) > 1 else []
        
        # 定义支持的可执行文件扩展名
        executable_extensions = ['.exe', '.com', '.bat', '.cmd']
        if platform.system() != 'Windows':
            # 在非Windows系统上，也支持无扩展名的可执行文件
            executable_extensions.append('')
        
        # 特殊处理Python脚本
        python_extensions = ['.py', '.pyw']
        
        def find_executable(file_path):
            """查找可执行文件的完整路径"""
            # 如果文件已经存在（绝对路径或相对路径）
            if os.path.exists(file_path):
                # 检查是否是文件
                if os.path.isfile(file_path):
                    # 在Windows上检查扩展名，在非Windows系统上检查执行权限
                    if platform.system() == 'Windows':
                        if any(file_path.lower().endswith(ext) for ext in executable_extensions):
                            return file_path
                        # 检查Python脚本
                        if any(file_path.lower().endswith(ext) for ext in python_extensions):
                            return file_path
                    else:
                        # 检查是否有执行权限
                        if os.access(file_path, os.X_OK):
                            return file_path
                        # 检查Python脚本
                        if any(file_path.lower().endswith(ext) for ext in python_extensions):
                            return file_path
                return None
            
            # 如果没有扩展名，尝试添加可能的扩展名
            if platform.system() == 'Windows' and not any(executable.lower().endswith(ext) for ext in executable_extensions + python_extensions):
                for ext in executable_extensions + python_extensions:
                    test_path = file_path + ext
                    if os.path.exists(test_path) and os.path.isfile(test_path):
                        return test_path
            
            return None
        
        def find_in_path(file_name):
            """在PATH环境变量中查找可执行文件"""
            path_dirs = os.environ.get('PATH', '').split(os.pathsep)
            
            for directory in path_dirs:
                directory = directory.strip('"')  # 移除可能的引号
                if not directory:
                    continue
                
                # 尝试直接路径
                full_path = os.path.join(directory, file_name)
                found_path = find_executable(full_path)
                if found_path:
                    return found_path
                
                # 如果没有扩展名，尝试添加扩展名
                if platform.system() == 'Windows' and not any(file_name.lower().endswith(ext) for ext in executable_extensions):
                    for ext in executable_extensions:
                        test_path = os.path.join(directory, file_name + ext)
                        found_path = find_executable(test_path)
                        if found_path:
                            return found_path
            
            return None
        
        # 首先检查是否是相对路径（以./或.\开头）
        is_relative_path = executable.startswith('./') or executable.startswith('.\\')
        
        if is_relative_path:
            # 相对路径，直接在当前目录查找
            found_path = find_executable(executable)
            if not found_path:
                # 抛出异常，让调用者处理
                raise PythonCMDError(ErrorCodes.FILE_NOT_FOUND, f"找不到可执行文件: {executable}", "请检查文件路径是否正确")
        else:
            # 先在PATH中查找
            found_path = find_in_path(executable)
            
            if not found_path:
                # 如果PATH中没找到，检查当前目录
                current_dir_path = find_executable(executable)
                if current_dir_path:
                    # 当前目录有，但PATH中没有，且没有使用./前缀，应该报错
                    raise PythonCMDError(ErrorCodes.COMMAND_EXECUTION_FAILED,
                                      f"无法执行 '{executable}'",
                                      f"文件存在于当前目录，但PATH中未找到。请使用 './{executable}' 或 '.\\{executable}' 来执行当前目录的文件")
                else:
                    # 完全找不到
                    raise PythonCMDError(ErrorCodes.FILE_NOT_FOUND, f"找不到可执行文件: {executable}",
                                         "文件不存在于PATH路径或当前目录中")
        
        # 执行可执行文件
        try:
            # 检查是否是Python脚本
            if any(found_path.lower().endswith(ext) for ext in python_extensions):
                # 使用Python解释器运行Python脚本
                python_exe = sys.executable  # 获取当前Python解释器路径
                result = subprocess.run([python_exe, found_path] + run_args, capture_output=False, text=True)
            else:
                # 使用subprocess运行程序
                result = subprocess.run([found_path] + run_args, capture_output=False, text=True)
            
            # 如果程序返回非零退出码，显示警告
            if result.returncode != 0:
                print(f"[INFO] 程序返回码: {result.returncode}")
                
        except PermissionError:
            # 抛出异常，让调用者处理
            raise PythonCMDError(ErrorCodes.PERMISSION_DENIED, f"没有权限执行文件: {found_path}",
                               "请检查文件权限或使用管理员权限运行")
        except FileNotFoundError:
            # 抛出异常，让调用者处理
            raise PythonCMDError(ErrorCodes.FILE_NOT_FOUND, f"无法执行文件: {found_path}",
                               "文件可能不存在或不是有效的可执行文件")
        except Exception as e:
            # 抛出异常，让调用者处理
            raise PythonCMDError(ErrorCodes.COMMAND_EXECUTION_FAILED, f"执行文件失败: {found_path}", str(e))
    
    def cd(self, directory=None):
        """切换工作目录"""
        if directory is None:
            # 如果没有指定目录，显示当前目录
            current_dir = os.getcwd()
            print(f"当前目录: {current_dir}")
            return
        
        try:
            # 尝试切换目录
            os.chdir(directory)
            new_dir = os.getcwd()
            print(f"已切换到目录: {new_dir}")
        except FileNotFoundError:
            raise_filesystem_error(ErrorCodes.DIRECTORY_NOT_FOUND, f"目录不存在: {directory}", "请检查路径是否正确")
        except PermissionError:
            raise_permission_error(ErrorCodes.DIRECTORY_ACCESS_DENIED, f"无法访问目录: {directory}", "权限不足")
        except Exception as e:
            raise_filesystem_error(ErrorCodes.FILE_ACCESS_DENIED, f"无法切换到目录: {directory}", str(e))
    
    def cat(self, *files):
        """显示文件内容（类似Linux cat命令）"""
        if not files:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请指定要显示的文件", "cat命令需要至少一个文件名")
            return
        
        for file_path in files:
            try:
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    raise_filesystem_error(ErrorCodes.FILE_NOT_FOUND, f"文件不存在: {file_path}", "请检查文件路径")
                    continue
                
                # 检查是否是文件
                if not os.path.isfile(file_path):
                    raise_filesystem_error(ErrorCodes.FILE_NOT_DIRECTORY, f"不是普通文件: {file_path}", "cat命令只能显示普通文件内容")
                    continue
                
                # 使用流式读取，避免大文件内存问题
                try:
                    for line in self._read_file(file_path):
                        sys.stdout.write(line)  # 比print少一次strip/add，保持原始格式
                except Exception:
                    # 如果还是失败，尝试以二进制模式读取并显示部分信息
                    raise_filesystem_error(ErrorCodes.FILE_READ_ERROR, f"无法读取文件: {file_path}", "文件可能不是文本文件或编码不支持")
                    continue
                    
            except PythonCMDError as e:
                # 捕获并显示错误，但继续处理下一个文件
                error_manager.log_error(e.code, e.message, e.details)
                formatted_msg = error_manager.format_error_message(e.code, e.message, e.details)
                print(formatted_msg)
                continue
            except Exception as e:
                error_manager.log_error(ErrorCodes.FILE_READ_ERROR, f"处理文件失败: {file_path}", str(e))
                formatted_msg = error_manager.format_error_message(ErrorCodes.FILE_READ_ERROR, f"处理文件失败: {file_path}", str(e))
                print(formatted_msg)
                continue
    
    def mkdir(self, *dirs):
        """创建目录（类似Linux mkdir命令）"""
        if not dirs:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请指定要创建的目录", "mkdir命令需要至少一个目录名")
            return
        
        for dir_path in dirs:
            try:
                if os.path.exists(dir_path):
                    raise_filesystem_error(ErrorCodes.DIRECTORY_EXISTS, f"目录已存在: {dir_path}", "无法创建已存在的目录")
                    continue
                
                os.makedirs(dir_path)
                print(f"已创建目录: {dir_path}")
            except Exception as e:
                raise_filesystem_error(ErrorCodes.DIRECTORY_CREATE_ERROR, f"创建目录失败: {dir_path}", str(e))
                continue
    
    def rm(self, *paths):
        """删除文件或目录（类似Linux rm命令）"""
        if not paths:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请指定要删除的文件或目录", "rm命令需要至少一个路径")
            return
        
        for path in paths:
            try:
                if not os.path.exists(path):
                    raise_filesystem_error(ErrorCodes.FILE_NOT_FOUND, f"文件或目录不存在: {path}", "无法删除不存在的项目")
                    continue
                
                if os.path.isfile(path):
                    os.remove(path)
                    print(f"已删除文件: {path}")
                elif os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
                    print(f"已删除目录: {path}")
            except Exception as e:
                raise_filesystem_error(ErrorCodes.FILE_DELETE_ERROR, f"删除失败: {path}", str(e))
                continue
    
    def touch(self, *files):
        """创建空文件或更新时间戳（类似Linux touch命令）"""
        if not files:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请指定要创建的文件", "touch命令需要至少一个文件名")
            return
        
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    # 文件存在，更新修改时间
                    os.utime(file_path, None)
                    print(f"已更新时间戳: {file_path}")
                else:
                    # 文件不存在，创建空文件
                    with open(file_path, 'w') as f:
                        pass
                    print(f"已创建文件: {file_path}")
            except Exception as e:
                raise_filesystem_error(ErrorCodes.FILE_CREATE_ERROR, f"操作失败: {file_path}", str(e))
                continue
    
    def pwd(self):
        """显示当前工作目录（类似Linux pwd命令）"""
        current_dir = os.getcwd()
        print(current_dir)
    
    def whoami(self):
        """显示当前用户（类似Linux whoami命令）"""
        import getpass
        username = getpass.getuser()
        print(username)
    
    def which(self, command):
        """显示命令位置（类似Linux which命令）"""
        if not command:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请指定要查找的命令", "which命令需要指定命令名")
            return
        
        # 首先检查内置命令
        if command in self.command_map:
            print(f"{command}: 内置命令")
            return
        
        # 在PATH中查找
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        found = False
        
        for directory in path_dirs:
            directory = directory.strip('"')
            if directory and os.path.exists(directory):
                # 尝试不同的扩展名
                extensions = ['', '.exe', '.com', '.bat', '.cmd']
                for ext in extensions:
                    full_path = os.path.join(directory, command + ext)
                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        print(f"{command}: {full_path}")
                        found = True
                        break
                if found:
                    break
        
        if not found:
            raise_command_error(ErrorCodes.COMMAND_NOT_FOUND, f"未找到命令: {command}", "命令不存在于PATH中")
    
    def _get_path_executables(self):
        """获取PATH中的可执行文件（带缓存机制）"""
        current_path = os.environ.get('PATH', '')
        current_time = time.time()
        current_path_hash = hash(current_path)
        
        # 检查是否需要更新缓存（PATH变化或超过5分钟）
        should_update = (
            not hasattr(self, '_path_cache') or not self._path_cache or  # 缓存为空
            current_path_hash != getattr(self, '_path_env_hash', None) or  # PATH环境变化
            (current_time - getattr(self, '_path_cache_time', 0)) > 300  # 超过5分钟
        )
        
        if should_update:
            # 更新缓存
            self._path_cache = {}
            self._path_env_hash = current_path_hash
            self._path_cache_time = current_time
            
            path_dirs = current_path.split(os.pathsep)
            common_exe_extensions = ['.exe', '.com', '.bat', '.cmd', '.vbs', '.js', '.ps1']
            
            for directory in path_dirs:
                directory = directory.strip('"')
                if directory and os.path.exists(directory):
                    try:
                        for item in os.listdir(directory):
                            # 更严格的可执行文件判断
                            if (not item.startswith('.') and
                                len(item) > 2 and  # 排除单字符和双字符文件
                                os.path.isfile(os.path.join(directory, item))):  # 确保是普通文件
                                
                                # 检查扩展名或没有扩展名（可能是可执行文件）
                                has_exe_extension = any(item.lower().endswith(ext) for ext in common_exe_extensions)
                                has_no_extension = '.' not in item
                                
                                if has_exe_extension or has_no_extension:
                                    # 移除扩展名，只保留基本名称用于匹配
                                    base_name = item
                                    if has_exe_extension:
                                        for ext in common_exe_extensions:
                                            if item.lower().endswith(ext):
                                                base_name = item[:-len(ext)]
                                                break
                                    self._path_cache[base_name] = os.path.join(directory, item)
                    except (OSError, PermissionError):
                        continue
        
        return list(self._path_cache.keys())
    
    def grep(self, pattern, file):
        """搜索文本模式（类似Linux grep命令）"""
        if not pattern or not file:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请提供搜索模式和文件名", "grep命令需要模式和文件名")
            return
        
        try:
            if not os.path.exists(file):
                raise_filesystem_error(ErrorCodes.FILE_NOT_FOUND, f"文件不存在: {file}", "请检查文件路径")
                return
            
            if not os.path.isfile(file):
                raise_filesystem_error(ErrorCodes.FILE_NOT_DIRECTORY, f"不是普通文件: {file}", "grep命令只能搜索普通文件")
                return
            
            with open(file, 'r', encoding='utf-8') as f:
                line_num = 0
                for line in f:
                    line_num += 1
                    if pattern in line:
                        print(f"{line_num}:{line.rstrip()}")
        except UnicodeDecodeError:
            try:
                with open(file, 'r', encoding='gbk') as f:
                    line_num = 0
                    for line in f:
                        line_num += 1
                        if pattern in line:
                            print(f"{line_num}:{line.rstrip()}")
            except Exception as e:
                raise_filesystem_error(ErrorCodes.FILE_READ_ERROR, f"无法读取文件: {file}", str(e))
        except Exception as e:
            raise_filesystem_error(ErrorCodes.FILE_READ_ERROR, f"搜索失败: {file}", str(e))
    
    def head(self, file, lines=10):
        """显示文件开头几行（类似Linux head命令）"""
        if not file:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请指定文件名", "head命令需要文件名")
            return
        
        try:
            if not os.path.exists(file):
                raise_filesystem_error(ErrorCodes.FILE_NOT_FOUND, f"文件不存在: {file}", "请检查文件路径")
                return
            
            if not os.path.isfile(file):
                raise_filesystem_error(ErrorCodes.FILE_NOT_DIRECTORY, f"不是普通文件: {file}", "head命令只能显示普通文件")
                return
            
            # 确保行数是正整数
            try:
                lines = int(lines)
                if lines <= 0:
                    lines = 10
            except (ValueError, TypeError):
                lines = 10
            
            # 使用流式读取，避免大文件内存问题
            line_num = 0
            for line in self._read_file(file):
                line_num += 1
                if line_num > lines:
                    break
                sys.stdout.write(line)  # 比print少一次strip/add，保持原始格式
        except Exception as e:
            raise_filesystem_error(ErrorCodes.FILE_READ_ERROR, f"读取失败: {file}", str(e))
    
    def tail(self, file, lines=10):
        """显示文件末尾几行（类似Linux tail命令）"""
        if not file:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请指定文件名", "tail命令需要文件名")
            return
        
        try:
            if not os.path.exists(file):
                raise_filesystem_error(ErrorCodes.FILE_NOT_FOUND, f"文件不存在: {file}", "请检查文件路径")
                return
            
            if not os.path.isfile(file):
                raise_filesystem_error(ErrorCodes.FILE_NOT_DIRECTORY, f"不是普通文件: {file}", "tail命令只能显示普通文件")
                return
            
            # 确保行数是正整数
            try:
                lines = int(lines)
                if lines <= 0:
                    lines = 10
            except (ValueError, TypeError):
                lines = 10
            
            # 使用deque维护最后N行，避免大文件内存问题
            last_lines = deque(maxlen=lines)
            for line in self._read_file(file):
                last_lines.append(line)
            
            # 输出最后几行
            for line in last_lines:
                sys.stdout.write(line)
                
        except Exception as e:
            raise_filesystem_error(ErrorCodes.FILE_READ_ERROR, f"读取失败: {file}", str(e))
    
    def wc(self, *files):
        """统计文件信息（类似Linux wc命令）"""
        if not files:
            raise_argument_error(ErrorCodes.MISSING_ARGUMENT, "请指定要统计的文件", "wc命令需要至少一个文件名")
            return
        
        total_lines = total_words = total_chars = 0
        
        for file_path in files:
            try:
                if not os.path.exists(file_path):
                    raise_filesystem_error(ErrorCodes.FILE_NOT_FOUND, f"文件不存在: {file_path}", "请检查文件路径")
                    continue
                
                if not os.path.isfile(file_path):
                    raise_filesystem_error(ErrorCodes.FILE_NOT_DIRECTORY, f"不是普通文件: {file_path}", "wc命令只能统计普通文件")
                    continue
                
                # 使用流式处理，避免大文件内存问题
                lines = words = chars = 0
                for line in self._read_file(file_path):
                    lines += 1
                    words += len(line.split())
                    chars += len(line)
                
                print(f"{lines:8}{words:8}{chars:8} {file_path}")
                
                total_lines += lines
                total_words += words
                total_chars += chars
                
            except Exception as e:
                error_manager.log_error(ErrorCodes.FILE_READ_ERROR, f"统计失败: {file_path}", str(e))
                continue
        
        # 如果是多个文件，显示总计
        if len(files) > 1:
            print(f"{total_lines:8}{total_words:8}{total_chars:8} 总计")

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
    
    def find_similar_commands(self, input_cmd):
        """查找相似的命令"""
        if not input_cmd:
            return []
        
        # 获取所有可用命令
        available_commands = list(self.command_map.keys())
        
        # 添加PATH中的可执行文件
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        path_executables = []
        common_exe_extensions = ['.exe', '.com', '.bat', '.cmd', '.vbs', '.js', '.ps1']
        
        for directory in path_dirs:
            directory = directory.strip('"')
            if directory and os.path.exists(directory):
                try:
                    for item in os.listdir(directory):
                        # 更严格的可执行文件判断
                        if (not item.startswith('.') and
                            len(item) > 2 and  # 排除单字符和双字符文件
                            os.path.isfile(os.path.join(directory, item))):  # 确保是普通文件
                            
                            # 检查扩展名或没有扩展名（可能是可执行文件）
                            has_exe_extension = any(item.lower().endswith(ext) for ext in common_exe_extensions)
                            has_no_extension = '.' not in item
                            
                            if has_exe_extension or has_no_extension:
                                # 移除扩展名，只保留基本名称用于匹配
                                base_name = item
                                if has_exe_extension:
                                    for ext in common_exe_extensions:
                                        if item.lower().endswith(ext):
                                            base_name = item[:-len(ext)]
                                            break
                                path_executables.append(base_name)
                except (OSError, PermissionError):
                    continue
        
        # 去重
        path_executables = list(set(path_executables))
        
        all_commands = available_commands + path_executables
        
        # 计算编辑距离（Levenshtein距离）
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        # 计算相似度并排序
        similar_commands = []
        for cmd in all_commands:
            distance = levenshtein_distance(input_cmd.lower(), cmd.lower())
            if distance <= 2:  # 编辑距离小于等于2
                similar_commands.append((cmd, distance))
        
        # 按距离排序
        similar_commands.sort(key=lambda x: x[1])
        
        # 返回最相似的命令（最多3个）
        return [cmd for cmd, distance in similar_commands[:3]]
    
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
            # 如果命令不在配置中，尝试作为可执行文件运行
            # 首先检查是否使用了相对路径前缀
            is_relative_path = cmd_name.startswith('./') or cmd_name.startswith('.\\')
            
            # 检查当前目录是否存在该文件（用于提供友好提示）
            import os
            import platform
            
            # 定义支持的可执行文件扩展名
            executable_extensions = ['.exe', '.com', '.bat', '.cmd']
            python_extensions = ['.py', '.pyw']
            if platform.system() != 'Windows':
                executable_extensions.append('')
            
            def check_current_directory(file_name):
                """检查当前目录是否存在该文件"""
                # 尝试直接查找
                if os.path.exists(file_name) and os.path.isfile(file_name):
                    return True
                
                # 如果没有扩展名，尝试添加可能的扩展名
                if platform.system() == 'Windows':
                    all_extensions = executable_extensions + python_extensions
                    if not any(file_name.lower().endswith(ext) for ext in all_extensions):
                        for ext in all_extensions:
                            test_path = file_name + ext
                            if os.path.exists(test_path) and os.path.isfile(test_path):
                                return True
                return False
            
            file_exists_in_current_dir = check_current_directory(cmd_name)
            
            try:
                # 使用shlex分割参数字符串，支持引号内的空格
                run_args = shlex.split(params_str) if params_str else []
                self.commands_instance.run(cmd_name, *run_args)
                return
            except PythonCMDError as e:
                # 根据是否使用相对路径前缀来决定错误信息
                if is_relative_path:
                    # 使用了相对路径前缀，显示文件相关的错误信息
                    # 这里保持run方法中已经显示的错误信息，不再重复显示
                    pass
                else:
                    # 没有使用相对路径前缀，显示命令不存在的错误
                    error_manager.log_error(ErrorCodes.COMMAND_NOT_FOUND, f"未知命令: {cmd_name}")
                    error_msg = error_manager.format_error_message(
                        ErrorCodes.COMMAND_NOT_FOUND,
                        f"未知命令: {cmd_name}",
                        f"请使用 'help' 命令查看可用命令列表"
                    )
                    print(error_msg)
                    
                    # 查找相似的命令
                    similar_commands = self.find_similar_commands(cmd_name)
                    if similar_commands:
                        if len(similar_commands) == 1:
                            print(f"是不是指: {similar_commands[0]}")
                        else:
                            suggestions = " | ".join(similar_commands)
                            print(f"是不是指: {suggestions}")
                    
                    # 如果文件存在于当前目录，提供额外的提示
                    if file_exists_in_current_dir:
                        print(f"提示: 当前目录存在文件 '{cmd_name}'，请使用 './{cmd_name}' 或 '.\\{cmd_name}' 来执行")
                return
            except Exception as e:
                # 其他错误，根据是否使用相对路径前缀来决定错误信息
                if is_relative_path:
                    # 使用了相对路径前缀，显示系统错误
                    error_manager.log_error(ErrorCodes.COMMAND_EXECUTION_FAILED, f"执行失败: {cmd_name}", str(e))
                    formatted_msg = error_manager.format_error_message(
                        ErrorCodes.COMMAND_EXECUTION_FAILED,
                        f"执行失败: {cmd_name}",
                        str(e)
                    )
                    print(formatted_msg)
                else:
                    # 没有使用相对路径前缀，显示命令不存在的错误
                    error_manager.log_error(ErrorCodes.COMMAND_NOT_FOUND, f"未知命令: {cmd_name}")
                    error_msg = error_manager.format_error_message(
                        ErrorCodes.COMMAND_NOT_FOUND,
                        f"未知命令: {cmd_name}",
                        f"请使用 'help' 命令查看可用命令列表"
                    )
                    print(error_msg)
                    
                    # 如果文件存在于当前目录，提供额外的提示
                    if file_exists_in_current_dir:
                        print(f"提示: 当前目录存在文件 '{cmd_name}'，请使用 './{cmd_name}' 或 '.\\{cmd_name}' 来执行")
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