# application_lifecycle.py

from contact_manager.domain import ContactBook, DomainError
from contact_manager.storage import Storage, StorageNotFoundError, StorageError
from contact_manager.logger import Logger
from contact_manager.protocols import DirtyTracker  # ✅ 导入 Protocol

class ApplicationStartupError(Exception):
    """应用程序启动失败。"""
    pass

class ApplicationShutdownError(Exception):
    """应用程序关闭失败。"""
    pass

class ApplicationLifecycle:
    """
    应用程序生命周期控制器。

    职责：
        1. 控制应用程序启动和退出流程
        2. 管理持久化加载与保存时机
        3. 管理 dirty 状态
        4. 实现 DirtyTracker Protocol
        5. 将 Domain / Infrastructure 异常转换为
           Application 层能够理解的语义
    """
    def __init__(self, book: ContactBook, storage: Storage, logger: Logger):
        """
        初始化应用程序生命周期控制器

        Args:
            book: 内存数据容器（Domain 层）
            storage: 持久化执行者（Infrastructure 层）
            logger: 日志记录器（Infrastructure 层）
        """
        self._book = book
        self._storage = storage
        self._logger = logger
        self._is_dirty = False   # ← 初始状态：干净

    def start(self) -> None:
        """
        启动应用程序：从持久化存储加载数据到内存

        流程：
             1. 从 Storage 加载数据
            2. 如果数据文件不存在，则使用空数据
            3. 将数据恢复到 ContactBook
            4. 根据最终结果记录日志

        Raises:
            ApplicationStartupError: 启动过程中无法恢复有效应用状态。
        """
        try:
            try:
                data = self._storage.load()
                load_from_storage = True
            except StorageNotFoundError:
                data = []
                load_from_storage = False

            self._book.from_data(data)

        except StorageError as e:
            raise ApplicationStartupError(
                f"应用启动时无法读取数据：{e}"
            ) from e
        except DomainError as e:
            raise ApplicationStartupError(
                f"应用启动时无法恢复通讯录数据：{e}"
            ) from e

        if load_from_storage:
            self._logger.info("数据加载成功")
        else:
            self._logger.warning("数据文件不存在，使用空通讯录")

    def mark_dirty(self) -> None:
        """
        标记应用内存状态已发生修改。

        这里只负责记录 dirty 状态，
        不负责保存数据。
        """
        self._is_dirty = True

    def shutdown(self) -> None:
        """
        关闭应用程序。

        如果数据已修改：
            1. 获取当前领域数据
            2. 保存到 Storage
            3. 保存成功后清除 dirty
            4. 记录保存成功

        无论是否保存：
            最后关闭 Logger。
        """
        try:
            if self._is_dirty:
                data = self._book.to_data()

                try:
                    self._storage.save(data)
                except StorageError as e:
                    raise ApplicationShutdownError("应用关闭时数据保存失败") from e

                self._is_dirty = False
                self._logger.info("数据保存成功")

        finally:
            # Logger 是辅助设施。
            # Logger 失败不能覆盖主业务异常。
            try:
                self._logger.info("应用程序关闭")
            except Exception:
                pass

            try:
                self._logger.close()
            except Exception:
                pass