"""
ContactService - Application Layer

职责：
- 对外提供业务用例入口（添加、删除、查看、搜索、列出）
    add_contact()
    get_contact()
    delete_contact()
    search_contacts()
    list_all_contacts()
    change_phone()
- 协调 Domain 层（ContactBook）完成业务操作
- 将 UI 的业务语言翻译为 Domain 的技术语言
- 不负责持久化（由外部生命周期管理）
- 不暴露技术细节（如 index）
"""

from domain import Contact, ContactBook, ContactValidationError


class ContactNotFoundError(Exception):
    pass

class ContactService:
    """
    通讯录服务 - Application 层核心

    API Boundary:
        - 对外：使用业务概念（name, phone）
        - 对内：调用 ContactBook 的技术接口（index）
        - 不暴露 ContactBook 的 index 给 UI
    """

    def __init__(self, contact_book: ContactBook):    # Service 依赖 ContactBook
        """
        这行代码是依赖注入（Dependency Injection）的经典体现
        把外部传入的 contact_book 对象保存为 ContactService 实例的私有属性 _book，供后续方法调用使用。
        使用时，Service 收到请求后，不自己处理数据，而是委托给 _book：
            service = ContactService(book)   # book 是 ContactBook 实例
            service._book.add_contact(...)   # 内部通过 _book 调用 Domain 层方法
        """
        self._book = contact_book

    def add_contact(self, name: str, phone: str) -> Contact:
        """
        用例：添加联系人

        职责：
            1. 创建 Contact 对象，Contact 自己验证数据
            2. 调用 ContactBook.add_contact()， ContactBook检查集合规则，加入通讯录
            3. 返回创建的联系人
        """
        contact = Contact(name, phone)
        self._book.add_contact(contact)
        return contact

    def delete_contact(self, position: int) -> Contact:
        """
        用例：删除指定位置的联系人。

        职责：
            1. 将 position 翻译为 index
            2. 调用 ContactBook.remove(index)
            3. 返回被删除的 Contact 对象

        Raises:
            ContactValidationError: position < 1
            ContactNotFoundError: position 超出范围
        """
        if position < 1:
            raise ContactValidationError(f"Position must be positive, got {position}")

        index = position - 1

        try:
            deleted_contact = self._book.remove(index)  # Domain 返回被删除的 Contact
        except IndexError as e:
            raise ContactNotFoundError(f"Contact at position {position} not found") from e

        return deleted_contact
        
    def get_contact(self, position: int) -> Contact:
        """
        用例：查看联系人详情

        职责：
            1. 将 position 翻译为 index
            2. 调用 ContactBook.get(index) 获取联系人
            3. 返回 Contact 对象
        """
        # 第 1 步：检查 position 是否合法（≥ 1）
        if position < 1:
            raise ContactValidationError(f"Position must be positive, got {position}")

        # 第 2 步：position（1-based）→ index（0-based）
        index = position - 1
        
        # 第 3 步：调用 ContactBook
        try:
            contact = self._book.get(index)
        except IndexError as e:
            # 第 4 步：联系人不存在 → 转换为 ContactNotFoundError
            raise ContactNotFoundError(f"Contact at position {position} not found") from e
        
        # 第 5 步：返回 Contact
        return contact

    def search_contacts(self, keyword: str) -> list[Contact]:
        """
        用例：搜索联系人

        职责：
            1. 调用 ContactBook.search_by_name(keyword)
            2. 返回匹配的联系人列表（可能为空）
        """
        return self._book.search_by_name(keyword)

    def list_all_contacts(self) -> list[Contact]:
        """
        用例：列出所有联系人

        职责：
            1. 通过 list(self._book) 利用 __iter__() 协议创建新列表
                - 新列表中的 Contact 对象仍是原对象的引用
                - 但列表容器本身是新创建的，修改列表（增删元素）不会影响 ContactBook 内部状态
            2. 所有联系人的列表（新列表，独立于 ContactBook 内部存储）
        """
        return list(self._book)   # ← 利用 __iter__() 协议
    
    def change_phone(self, position: int, new_phone: str) -> None:
        # 1. 参数校验：position 必须是正数
        if position < 1:
            raise ContactValidationError(f"Position must be positive, got {position}")
        
        # 2. 转换用户位置为列表索引
        index = position - 1
        
        # 3. 获取联系人（若不存在则抛 ContactNotFoundError）
        try:
            contact = self._book.get(index)
        except IndexError as e:
            raise ContactNotFoundError(
                f"Contact at position {position} not found"
            ) from e
        
        # 4. 请求 ContactBook 完成手机号修改
        self._book.change_contact_phone(contact, new_phone)
        
