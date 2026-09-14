# storage.py
"""
存储模块 - 负责联系人数据的持久化（保存到文件和从文件读取）

本模块包含：
1. 自定义异常类：用于处理存储相关的错误
2. Storage协议：定义存储类必须实现的方法（接口规范）
3. JsonStorage类：使用JSON格式存储数据的实现类
"""
# 这个模块属于 Infrastructure 层。
#
# 它的职责边界：
#   - 把「磁盘上的字节」翻译成「内存里的元组 (version, list[dict])」
#   - 把「内存里的当前版本数据」原子地写回磁盘
#   - 旧版本数据在 load 时触发 Migration，迁移成功立即写回
#
# 它不负责：业务规则（Domain）、用例编排（Application）。
# 它是「介质适配器」——换 SQLite 时替换这个模块，别处不动。

import json
# JSON 序列化/反序列化。把 Python 对象 → JSON 字符串（存盘），反之（读盘）。

import os
# 提供路径操作（os.path.exists）、原子替换（os.replace）、
# 关闭文件描述符（os.close）、删除文件（os.remove）。

import tempfile
# 提供 mkstemp：安全地创建临时文件，返回 (fd, path)。

from typing import Any, Protocol

from contact_manager.migration import Migration, MigrationError
# 导入 Migration（旧版本数据要交给它迁移）和 MigrationError（包装迁移失败）。
# 注意：JsonStorage 依赖 Migration，这是「Storage 编排迁移」的体现——
# 迁移的触发点在 Storage.load()，而不是 Application 或 Domain。

from contact_manager.migration import CURRENT_VERSION
# 当前数据版本

# ==================== 1. 自定义异常类 ====================
# 异常类的继承关系：StorageError > StorageNotFoundError, StorageDataCorruptedError
# 这样设计可以让代码通过捕获 StorageError 来捕获所有存储相关的异常

class StorageError(Exception):
    """
    存储操作的基类异常
    只需捕获StorageError，就能覆盖「文件不存在」「数据损坏」「读写失败」全部情况
    """

class StorageNotFoundError(StorageError):
    """
    文件未找到异常
    当存储文件不存在时抛出（例如首次运行程序时）

    单独分出这个子类，是因为「文件不存在」和「文件损坏」在业务上需要不同处理：
       - 不存在 → 首次运行，是正常情况，上层创建空 ContactBook。
       - 损坏   → 数据出问题了，上层应该报错而不是静默重建。
    """

class StorageDataCorruptedError(StorageError):
    """
    数据损坏异常
    文件存在但解析失败、或结构校验不过（缺 version、version 不是 int 等）时抛出
    """

# ==================== 2. 定义 Storage 协议（接口规范） ====================
class Storage(Protocol):
    """
    作用：规定所有存储类必须实现的方法
    任何实现了 load() 和 save() 方法的类都可以被视为 Storage 类型

    这是「端口」：Application 层依赖 Storage 这个抽象，
    不包含 JsonStorage / SqliteStorage 这些具体实现，只定义方法签名
    组装层决定注入哪个实现。
    """

    def load(self) -> list[dict[str, Any]]:
        """
        从存储介质加载数据
        返回值：包含字典的列表，每个字典代表一个联系人
        如果文件不存在，应该抛出 StorageNotFoundError
        如果数据损坏，应该抛出 StorageDataCorruptedError
    
        契约核心：返回「当前版本」的数据。
        如果磁盘上是旧版本，实现内部负责迁移，并确保迁移结果已落盘
        之后才返回——这是前面反复确立的 load() 成功契约：
        成功返回 ⟺ 磁盘上存在一份完整的、当前版本的数据。
    
        注意：调用方拿到的永远是当前版本，不需要知道磁盘上曾经是什么版本。
        """
        ...

    def save(self, data: list[dict[str, Any]]) -> None:
        """
        契约：把「当前版本数据」原子地写入磁盘
        参数：data 是包含字典的列表，每个字典代表一个联系人
        失败抛 StorageError，绝不静默吞掉，绝不写半成品。

        # 隐含契约：
            - save 必须原子：任意崩溃点下，磁盘要么是完整旧版，要么是完整新版。
            - save 永远写「当前版本」，版本号由实现自己补，调用方不用传。
        """

# ==================== 3. JsonStorage 实现类 ====================
class JsonStorage:
    """
    JSON格式的存储实现类
    将联系人数据以JSON格式保存到文件中
    
    特点：
    1. 使用JSON格式存储，可读性强，方便调试
    2. 实现了 load() 和 save() 方法，符合 Storage 协议
    """

    def __init__(
        self, 
        file_path: str,
        migration: Migration,
    ):
        """
        初始化 JsonStorage 对象
        参数：
            file_path: 字符串类型，指定数据文件的路径
            例如："contacts.json" 表示当前目录下的 contacts.json 文件
        """
        # 依赖注入：JsonStorage 需要两样东西——
        #   1. 文件路径（存哪）
        #   2. Migration（旧版本数据交给谁迁）
        # 两者都由组装层传入，JsonStorage 不自己 new。

        self.file_path = file_path
        # 目标文件路径。load/save 都以它为基准。

        self._migration = migration
        # 迁移器。load 时如果发现磁盘版本旧于当前，用它迁移。

    def load(self) -> list[dict[str, Any]]:
        """
        从JSON文件加载数据
        返回值：V2开始是一个带版本号的字典: {
            "version": CURRENT_VERSION,     当前版本号
            "contacts": data,            list[dict]，每个字典包含一个联系人的信息，例如：[{"name": "张三", "phone": "13800138000"}, ...]
        }
        完整契约还包括「返回当前版本数据」——旧版本会在内部被迁移
        
        可能抛出的异常：
            1. StorageNotFoundError: 文件不存在（首次运行）
            2. StorageDataCorruptedError: 文件存在但内容损坏（JSON格式错误）
        """

        # 第1步：检查文件是否存在
        if not os.path.exists(self.file_path):
            # 文件不存在 → 抛 StorageNotFoundError。
            # 上层（ApplicationLifecycle.start）会捕获它，
            # 当作「首次运行」，用空 ContactBook 继续。
            #
            # 注意：这里用「抛异常」而不是「返回空列表」表达首次运行，
            # 是因为「文件不存在」和「文件是空通讯录」在语义上不同：
            #   - 文件不存在 → 首次运行
            #   - 文件存在但内容是 [] → 用户主动清空了通讯录
            # 混在一起会让上层无法区分。
            raise StorageNotFoundError("首次运行，没有数据")
        
        # 第2步：尝试打开并读取文件
        try:    
            with open(self.file_path, "r", encoding="utf-8") as f:
                # with 保证文件自动关闭，异常也不泄漏。
                # encoding="utf-8" 显式指定，避免依赖系统默认编码（Windows 上默认可能是 GBK）。

                raw_data = json.load(f)
                # json.load 从文件读 JSON → Python 对象。
                # 失败会抛 json.JSONDecodeError。

        # 第3步：捕获JSON解析错误
        except json.JSONDecodeError as e:
            # 文件存在、能打开，但内容不是合法 JSON。
            # 这是「数据损坏」，不是「首次运行」，所以抛不同的异常。
            raise StorageDataCorruptedError(
                f"文件 {self.file_path} 内容损坏，无法解析"
            ) from e
            # `from e` 保留原始异常链，排查时能看到具体的 JSON 错误位置。

        except OSError as e:
            # 文件系统层面的错误：权限不足、磁盘错误、路径是目录等。
            # 归入 StorageError（而非 Corrupted），因为不是数据本身的问题。
            raise StorageError(
                f"读取文件 {self.file_path} 失败"
            ) from e
        
        # 第4步：从磁盘原始数据里解析出「版本号 + 数据本体」
        try:
            # raw_data 是刚读进来的原始内容（比如整个 JSON 对象）。
            # _read_versioned_data 负责把 version 字段和数据部分拆开：
            #   {"version": 1, "contacts": [...]}  →  (1, [...])
            #
            # 注意：这一步只做「解析」，不做「迁移」。
            # 它按磁盘上实际写的版本号如实报告，不管这个版本是不是当前版本
            version, data = self._read_versioned_data(raw_data)

            # 判断是否需要对磁盘数据做升级
            #
            # 只有磁盘版本 ≠ 当前版本时才迁移。
            # 判断依据永远是「磁盘上读到的版本」，而不是「上次是否迁移过」——
            # 因为 save 失败时磁盘没变，下次启动必须重新走一遍。
            if version != CURRENT_VERSION:
                # 调用 Migration 做纯数据转换：
                #   输入：磁盘上的旧版本数据
                #   输出：当前版本的数据
                #
                # Migration 不碰磁盘、不产生副作用，只是「v1 形状 → v2 形状」。
                # 所以此刻 data 还只活在内存里，磁盘上仍然是旧版本。
                version, data = self._migration.migrate(
                    version,
                    data,
                )
                # Migration 成功只是内存转换完成。
                # 必须成功持久化后，load() 才能成功返回。
                # 为什么要在这里立即 save，而不是等程序退出时再存？
                #   1. 压缩崩溃窗口：迁完立刻落盘，之后崩溃也不会退回 v1。
                #   2. 建立 load() 契约：load() 返回的数据必须是磁盘上真实存在的，
                #      所以「内存里有了 v2」还不够，得先让磁盘也变成 v2。
                #
                # save() 内部是原子写（临时文件 → fsync → rename），
                # 保证磁盘在任意崩溃点都是完整的旧版或完整的新版，不会半截。
                #
                # 如果 save 失败，它会抛 StorageError：
                #   - 磁盘仍是完整的 v1（原子写保证了这点）
                #   - load() 不会返回 v2（异常向上传播，不会走到下面的 return）
                #   - 下次启动读到 v1，重新迁移，逻辑闭环
                self.save(data)
            # 返回当前版本数据 ──
            #
            # 能走到这里，说明：
            #   - 磁盘本来就是当前版本（跳过了 if 块），或
            #   - 磁盘是旧版本，但迁移 + 原子写回都已成功
            # 两种情况都满足 load() 的成功契约：
            #   「磁盘上存在一份完整的、当前版本的数据
            return data
        
        except MigrationError as e:
            raise StorageError(
                f"数据迁移失败：{e}"
            ) from e

    def save(self, data: list[dict[str, Any]]) -> None:
    # 对外契约：把「当前版本的数据」原子地写入磁盘。
    #
    # 契约的三个要点：
    #   1. 写入的永远是「当前版本」——版本号由 save 自己补，调用方不用管。
    #   2. 原子性——任意崩溃点下，磁盘要么是完整的旧版本，要么是完整的新版本。
    #   3. 失败即抛 StorageError——绝不静默吞掉，绝不写出一份半成品。

        payload = {
            "version": CURRENT_VERSION,
            "contacts": data,
        }
        # 将数据打包成带版本号的字典
        # 这个字典有两个键值对：
            # "version" → 值 2
            # "contacts" → 值 [...]（一个列表）
        # 组装最终落盘的 JSON 结构：{version, contacts}。
        # 注意 version 是 save 自己填的，不是调用方传的。


        directory = os.path.dirname(
            os.path.abspath(self.file_path)
        )
        # 取得目标文件所在的目录（绝对路径），因为临时文件必须和目标文件在「同一个文件系统」内

        fd = None
        temp_path = None
        # 在 try 之前先置空，是为了让 finally 能安全地判断
        # 「这两个资源是否已经创建过、需要清理」。
        # 如果一开始就赋值，finally 里就无法区分「创建成功」和「还没创建」。

        try:
            fd, temp_path = tempfile.mkstemp(
                dir=directory,
                prefix=".contacts_",
                suffix=".tmp",
            )
            # mkstemp：以「安全、唯一」的方式创建一个临时文件，返回 (文件描述符, 路径)。
            #
            # 为什么用 mkstemp 而不是自己拼一个 "contacts.json.tmp"？
            #   - mkstemp 保证文件名唯一，避免两个进程/两次调用撞名。
            #   - mkstemp 用 O_EXCL 打开，避免「检查存在性 → 创建」之间的竞态。
            #   - 前缀用 "." 打头，是 Unix 惯例，让临时文件默认不被 ls 列出。
            #   - dir=directory 保证它和目标文件在同一个文件系统（见上）。

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as f:
                # 把文件描述符包装成 Python 文件对象，用 with 管理生命周期：
                # 退出 with 块时自动 flush 并 close。
                fd = None
                # 关键：立刻把 fd 置 None。
                # 因为 fdopen 之后，文件的所有权已经交给文件对象 f，
                # 如果 finally 里再去 os.close(fd)，就会双重关闭（OSError）。
                # 置 None 是在告诉 finally：「这个 fd 已经不用你管了」。

                json.dump(
                    payload,
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
                # 把 payload 序列化写入临时文件。
                #   ensure_ascii=False → 中文原样写出，不转成 \uXXXX。
                #   indent=2           → 便于人阅读（对正确性没影响）。

                f.flush()
                # 把 Python 缓冲区的数据刷到操作系统缓冲区。
                # 注意：这一步只到「OS 缓冲区」，还没真正落盘。

                os.fsync(f.fileno())
                # 强制把 OS 缓冲区的数据刷到物理磁盘
                # 否则如果只 flush 不 fsync，数据可能还在 OS 页缓存里，此时断电会丢失

            os.replace(temp_path, self.file_path)
            # 原子替换：把临时文件改名成目标文件。
            #
            # 为什么是原子的？
            #   POSIX 的 rename 不复制数据，只改目录项指针。
            #   所以不存在「替换到一半」的状态——要么指向旧文件，要么指向新文件。
            #
            # 为什么用 os.replace 而不是 os.rename？
            #   os.replace 在目标已存在时会覆盖（Windows 上也是），
            #   语义更明确，跨平台一致。

            temp_path = None
            # 替换成功后，临时文件已经不存在了（它「变成」了目标文件）。
            # 置 None 告诉 finally：「没有临时文件需要清理了」。
            # 如果这里不置 None，finally 会去 remove 一个已经不存在的路径，
            # 虽然会被 try/except 吞掉，但语义上是错的。

        except OSError as e:
            # 任何文件系统层面的失败（磁盘满、权限错、IO 错误……）
            # 统一包装成 StorageError，并保留原始异常链。
            #
            # 注意：这里只 catch OSError，不 catch 一切 Exception。
            # 因为 save 里可能出现的「非 OSError」异常（比如 json 序列化失败），
            # 属于编程错误，不该被伪装成 StorageError。
            raise StorageError(
                "保存数据失败"
            ) from e
            # 抛出后，调用方（load）不会走到 return，
            # 也就不会返回一份「没落盘的 v2」——契约成立。

        finally:
            # 无论成功、失败还是异常，都要清理资源。

            if fd is not None:
                os.close(fd)
                # 只有当 fd 还没被 fdopen 接管时，才需要手动关闭。
                # 正常路径下 fd 早在 with 里被置 None 了，不会走到这里。
                # 走到这里说明 mkstemp 成功、但 fdopen 之前就出错了。

            if temp_path is not None:
                # 只有当临时文件还没被 replace 成目标文件时，才需要删除。
                # 正常成功后 temp_path 已被置 None，不会走到这里。
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
                # 删除临时文件是「尽力而为」：
                #   - 删不掉（比如权限问题）也不该让整个 save 失败，
                #     因为原始异常（如果有）比这个清理失败更重要。
                #   - 残留的临时文件不会影响正确性：
                #     下次 load 只读 self.file_path，不会读临时文件。

    @staticmethod
    def _read_versioned_data(
        raw_data: Any,
    ) -> tuple[int, list[dict[str, Any]]]:
        # 静态方法：不依赖实例状态，纯粹是「输入 → 输出」的解析函数。
        # 职责：把从磁盘读到的原始数据，拆成 (version, contacts) 这个元组，并在拆的过程中做「结构校验」。

        if isinstance(raw_data, list):
            # 判断读到的原始数据是不是「裸列表」。
            #
            # 什么情况下会走到这里？
            #   v1 时期的文件格式是「没有版本字段」的，磁盘上直接就是：
            #       [ {"name": "Tom", "phone": "..."}, ... ]
            #   而 v2 及以后的结构是：
            #       { "version": 2, "contacts": [...] }
            #
            #   所以「顶层是 list」等价于「这是一份 v1 数据」——
            #   因为没有 version 字段可读，只能靠结构来判断版本。
            return 1, raw_data
            #   - 版本号硬编码为 1，因为「顶层是 list」就是 v1 的识别特征。
            #   - raw_data 直接作为数据本体返回，不需要再解包——
            #     v1 没有外层对象，list 本身就是 contacts。
            #
            # 返回后，调用方（load）拿到的就是 (1, [...])，
            # 和读 v2 文件时得到 (2, [...]) 的形状完全一致，
    # 后续 Migration、save 都能用同一套逻辑处理。

        if not isinstance(raw_data, dict):
            raise StorageDataCorruptedError(
                "数据缺少版本信息"
            )
        # 第一层校验：整个文件必须是一个 JSON 对象。
        # 如果读到的是数组、字符串、null 等，说明数据损坏或格式错误，
        # 直接报 StorageDataCorruptedError，不做任何猜测。

        version = raw_data.get("version")
        data = raw_data.get("contacts")
        # 用 .get 而不是 ["version"]：
        # 字段缺失时返回 None，交给下面显式判断，
        # 而不是让 KeyError 冒出来（KeyError 语义不清晰，不好定位）。

        if not isinstance(version, int):
            raise StorageDataCorruptedError(
                "数据版本无效"
            )
        # 第二层校验：version 必须是 int。
        # 注意 isinstance(True, int) 为 True——如果你在意，
        # 可以额外排除 bool，但通常没必要。
        #
        # 这里不接受「version 是字符串 "1"」之类的宽松解析：
        # 数据格式是契约，不符合就报错，不猜。

        if not isinstance(data, list):
            raise StorageDataCorruptedError(
                "联系人数据无效"
            )
        # 第三层校验：contacts 必须是列表。
        # 这里只校验「是列表」，不校验「列表里每个元素是不是 dict」——
        # 元素级的校验交给 Migration 或更上层的 from_data()。
        # 分层校验：这一层只负责「顶层形状」，不越界管更深的结构。

        return version, data
        # 返回解析结果（一个元组）。
        # Python语法规则：return a, b 里的逗号会自动把 a, b 构成一个元组
        # 等价于 return (version, data)
        # 或者等价于 return tuple((version, data))，但没必要

        # tuple() 接收的是一个可迭代对象，比如 tuple([1, 2, 3])。它不接受两个独立参数