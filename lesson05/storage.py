"""
存储模块 - 负责联系人数据的持久化（保存到文件和从文件读取）

本模块包含：
1. 自定义异常类：用于处理存储相关的错误
2. Storage协议：定义存储类必须实现的方法（接口规范）
3. JsonStorage类：使用JSON格式存储数据的实现类
"""
import json                         # JSON模块，用于将Python对象转换为JSON格式（序列化）和反向转换（反序列化）
import os                           # OS模块，用于检查文件是否存在等操作系统相关功能
from typing import Protocol, Any    # Protocol用于定义接口规范，Any表示任意类型

# ==================== 1. 自定义异常类 ====================
# 异常类的继承关系：StorageError > StorageNotFoundError, StorageDataCorruptedError
# 这样设计可以让代码通过捕获 StorageError 来捕获所有存储相关的异常
class StorageError(Exception):
    """
    存储操作的基类异常
    所有与存储相关的异常都应该继承这个类
    作用：统一处理存储错误，方便调用者用 except StorageError 捕获所有存储异常
    """
    pass
class StorageNotFoundError(StorageError):
    """
    文件未找到异常
    继承自 StorageError
    当存储文件不存在时抛出（例如首次运行程序时）
    """
    pass
class StorageDataCorruptedError(StorageError):
    """
    数据损坏异常
    继承自 StorageError
    当存储文件存在但内容损坏（如JSON格式错误）时抛出
    """
    pass

# ==================== 2. 定义 Storage 协议（接口规范） ====================
class Storage(Protocol):
    """
    Storage 协议（类似于Java中的接口）
    作用：规定所有存储类必须实现的方法
    这是一个抽象规范，不包含具体实现，只定义方法签名
    
    任何实现了 load() 和 save() 方法的类都可以被视为 Storage 类型
    这符合 Python 的"鸭子类型"（Duck Typing）哲学
    """
    def load(self) -> list[dict[str, Any]]:
        """
        从存储介质加载数据
        返回值：包含字典的列表，每个字典代表一个联系人
        如果文件不存在，应该抛出 StorageNotFoundError
        如果数据损坏，应该抛出 StorageDataCorruptedError
        """
        ...
    def save(self, data: list[dict[str, Any]]) -> None:
        """
        将数据保存到存储介质
        参数：data 是包含字典的列表，每个字典代表一个联系人
        如果保存失败，应该抛出 StorageError
        """
        ...

# ==================== 3. JsonStorage 实现类 ====================
class JsonStorage:
    """
    JSON格式的存储实现类
    将联系人数据以JSON格式保存到文件中
    
    特点：
    1. 使用JSON格式存储，可读性强，方便调试
    2. 支持UTF-8编码，可以保存中文姓名
    3. 实现了 load() 和 save() 方法，符合 Storage 协议
    """
    def __init__(self, file_path: str):   # ← 接收文件路径
        """
        初始化 JsonStorage 对象
        参数：
            file_path: 字符串类型，指定数据文件的路径
                      例如："contacts.json" 表示当前目录下的 contacts.json 文件
        """
        self.file_path = file_path        # 将文件路径保存为实例属性，供其他方法使用

    def load(self) -> list[dict[str, Any]]:
        """
        从JSON文件加载数据
        返回值：list[dict]，每个字典包含一个联系人的信息
                例如：[{"name": "张三", "phone": "13800138000"}, ...]
        
        可能抛出的异常：
            1. StorageNotFoundError: 文件不存在（首次运行）
            2. StorageDataCorruptedError: 文件存在但内容损坏（JSON格式错误）
        """
        # 第1步：检查文件是否存在
        # os.path.exists() 返回 True 表示文件存在，False 表示不存在
        if not os.path.exists(self.file_path):
            # 文件不存在时，抛出 StorageNotFoundError 异常
            # 上层代码（main.py）会捕获这个异常并创建新数据
            raise StorageNotFoundError("首次运行，没有数据")
        
        # 第2步：尝试打开并读取文件
        try:    
            with open(self.file_path, "r", encoding="utf-8") as f:   # with open() 会自动关闭文件，即使发生异常也能保证资源释放
                return json.load(f)                                  # json.load() 从文件读取JSON数据并转换为Python对象
        # 第3步：捕获JSON解析错误（文件内容格式不正确），例如：文件内容不是合法的JSON格式
        except json.JSONDecodeError as e:                            # "from e" 表示链式异常，保留原始异常信息以便调试
            raise StorageDataCorruptedError(                          # 抛出 StorageDataCorruptedError 异常，并附上具体的错误信息
                f"文件 {self.file_path} 内容损坏，无法解析"
            ) from e     

    def save(self, data: list[dict[str, Any]]) -> None:
        """
        将数据保存到JSON文件
        参数：
            data: list[dict]，要保存的联系人数据列表
                  每个字典必须包含 "name" 和 "phone" 键
        
        可能抛出的异常：
            StorageError: 写入文件失败（如磁盘已满、权限不足等）
        """
        # 尝试打开文件并写入数据
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except OSError as e:
            # 捕获操作系统相关的错误（如磁盘已满、权限不足、路径不存在等）
            # OSError 是文件操作常见的异常基类
            # 抛出 StorageError 异常，让上层代码统一处理
            raise StorageError(f"写入文件 {self.file_path} 失败") from e