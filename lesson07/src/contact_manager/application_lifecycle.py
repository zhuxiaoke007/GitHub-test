from contact_manager.domain import ContactBook
from contact_manager.storage import Storage, StorageNotFoundError
from contact_manager.logger import Logger

class ApplicationLifecycle:
    """
    应用程序生命周期控制器

    职责：
        控制应用程序的启动、运行和退出流程
        管理所有资源的生命周期（ContactBook、Storage、Logger）

    依赖：
        ContactBook: 内存数据容器
        Storage: 持久化执行者
        Logger: 日志记录器（Infrastructure 层
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
            StorageDataCorruptedError: 持久化数据损坏且无法恢复时抛出
        """
        try:
            data = self._storage.load()
            load_from_storage = True
        except StorageNotFoundError:
            data = []
            load_from_storage = False

        self._book.from_data(data)

        if load_from_storage:
            self._logger.info("数据加载成功")
        else:
            self._logger.warning("数据文件不存在，使用空通讯录")

    def mark_dirty(self) -> None:
        """标记数据已被修改"""
        self._is_dirty = True

    def shutdown(self) -> None:
        """
        关闭应用程序：如有修改则保存

        流程：
            1. 检查 _is_dirty
            2. 如果脏，从 book 获取数据，交给 storage 保存
            3. 保存成功后，标记为干净
            4. 记录"应用程序关闭"日志
            5. 关闭 Logger（最后关闭）
        """
        try:
            # 保存数据（如果已修改）
            if self._is_dirty:
                data = self._book.to_data()
                self._storage.save(data)
                self._is_dirty = False   # ← 保存成功后重置
                self._logger.info("数据保存成功")
        except Exception as e:
            # 保存失败 → 记录错误日志
            self._logger.error(f"数据保存失败：{e}")
            raise
        finally:
            # 记录关闭日志（无论保存成功还是失败）
            self._logger.info("应用程序关闭")
            # 最后才关闭 Logger
            self._logger.close()