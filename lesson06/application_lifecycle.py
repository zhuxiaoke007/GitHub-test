from domain import ContactBook
from storage import Storage, StorageNotFoundError


class ApplicationLifecycle:
    """
    应用程序生命周期控制器

    职责：
        控制应用程序的启动、运行和退出流程

    依赖：
        ContactBook: 内存数据容器
        Storage: 持久化执行者
    """

    def __init__(self, book: ContactBook, storage: Storage):
        """
        初始化应用程序生命周期控制器

        Args:
            book: 内存数据容器（Domain 层）
            storage: 持久化执行者（Infrastructure 层）
        """
        self._book = book
        self._storage = storage
        self._is_dirty = False   # ← 初始状态：干净

    def start(self) -> None:
        """
        启动应用程序：从持久化存储加载数据到内存

        流程：
            1. 调用 Storage.load() 从文件读取数据
            2. 调用 ContactBook.from_data() 加载到内存

        Raises:
            StorageDataCorruptedError: 持久化数据损坏且无法恢复时抛出
        """
        try:
            data = self._storage.load()
        except StorageNotFoundError:       # 如果文件不存在，触发异常 StorageNotFoundError，执行这里的代码
            data = []                      # 第一次运行：没有数据文件，创建了内存中的空通讯录
        self._book.from_data(data)

    def mark_dirty(self) -> None:
        """标记数据已被修改"""
        self._is_dirty = True

    def shutdown(self) -> None:
        """
        关闭应用程序：如有修改则保存

        流程：
            1. 检查 _is_dirty
            2. 如果脏，从 book 获取数据
            3. 交给 storage 保存
            4. 保存成功后，标记为干净
        """
        if self._is_dirty:
            data = self._book.to_data()
            self._storage.save(data)
            self._is_dirty = False   # ← 保存成功后重置