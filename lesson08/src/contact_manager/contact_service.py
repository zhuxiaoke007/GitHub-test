"""
ContactService - Application Layer

职责：
- 对外提供业务用例入口（添加、删除、查看、搜索、列出）
    add_contact(name, phone)
    delete_contact(contact_id)
    get_contact(contact_id)
    search_contacts(keyword)
    list_all_contacts()
    change_phone(contact_id, new_phone)
- Service 将外部用例请求协调为 Domain 操作，并将 Domain 结果/异常转换为 Application 语义
- 在业务状态成功修改后通知 DirtyTracker
- 不暴露技术细节（如 index）
"""

from contact_manager.domain import (
    Contact, 
    ContactBook, 
    DomainError, 
    ContactValidationError, 
    ContactIdNotFoundError,
    ContactConflictError, 
    DuplicateContactIdError,
    DuplicatePhoneError
)
from contact_manager.protocols import DirtyTracker, ContactIdGenerator, ContactIdGenerationError


class ContactServiceError(Exception):
    """Service 层异常的基类"""
    pass

class ContactNotFoundError(ContactServiceError):
    """联系人不存在"""
    pass

class ContactInputError(ContactServiceError):
    """用户提供的数据无法通过输入/业务验证）"""
    pass

class ContactDuplicateError(ContactServiceError):
    """用户请求造成了联系人唯一性冲突"""
    pass

class ContactServiceInternalError(ContactServiceError):
    """用户无法修复的系统内部错误"""
    pass

class ContactService:
    """
    通讯录服务 - Application 层核心

    API Boundary:
        - 对外：使用业务概念（name, phone）
        - 对内：调用 ContactBook 的技术接口（index）
        - 不暴露 ContactBook 的 index 给 UI
    """

    def __init__(
            self, 
            contact_book: ContactBook, 
            tracker: DirtyTracker, 
            id_generator: ContactIdGenerator
            ):
        """
        这行代码是依赖注入（Dependency Injection）的经典体现
        把外部传入的 contact_bootrackerk 对象保存为 ContactService 实例的私有属性 _book，供后续方法调用使用。
        使用时，Service 收到请求后，不自己处理数据，而是委托给 _book：
            service = ContactService(book,tracker,id_generator)  
            service._book.add_contact(...)   # 内部通过 _book 调用 Domain 层方法
        """
        self._book = contact_book
        self._tracker = tracker
        self._id_generator = id_generator

    def add_contact(self, name: str, phone: str) -> Contact:
        """
        用例：添加联系人

        职责：
            1. 创建 Contact 对象，Contact 自己验证数据
            2. 调用 ContactBook.add_contact()， ContactBook检查集合规则，加入通讯录
            3. 返回创建的联系人
        """
        # 1. 生成 ID —— 独立于领域翻译
        try:
            contact_id = self._id_generator.generate()
        except ContactIdGenerationError as e:
            raise ContactServiceInternalError(
                "添加联系人时无法生成 ID"
            ) from e

        # 2. 领域操作 —— 翻译领域异常
        try:
            contact = Contact(contact_id, name, phone)
            self._book.add_contact(contact)

        except ContactValidationError as e:
            raise ContactInputError(str(e)) from e
        except DuplicatePhoneError as e:
            raise ContactDuplicateError(f"手机号 {phone} 已被占用") from e
        except DomainError as e:
            raise ContactServiceInternalError("添加联系人时发生系统错误") from e
        # 3. 标记脏数据 —— 独立于业务操作
        self._tracker.mark_dirty()   # ✅ 只标记 dirty，不直接保存

        return contact

    def delete_contact(self, contact_id: str) -> Contact:
        """
        用例：删除指定id的联系人。

        职责：
            1. 删除指定id的联系人
            2. 返回被删除的 Contact 对象
        """
        try:
            deleted_contact = self._book.remove_by_id(contact_id)       # Domain 返回被删除的 Contact
        except ContactIdNotFoundError as e:
            raise ContactNotFoundError(f"联系人 {contact_id} 不存在") from e
        except DomainError as e:
            # 兜底：任何未预料的 Domain 异常，都翻译成 Application 语义
            raise ContactServiceInternalError(f"删除联系人 {contact_id} 时发生系统错误") from e
        
        self._tracker.mark_dirty()
        return deleted_contact
        
    def get_contact(self, contact_id: str) -> Contact:
        """
        用例：查看联系人详情

        职责：
            1. 获取指定id的联系人
            2. 返回被删除的 Contact 对象
        """
        try:
            contact = self._book.get_by_id(contact_id)
        except ContactIdNotFoundError as e:
            raise ContactNotFoundError(f"联系人 {contact_id} 不存在") from e
        except DomainError as e:
            # 兜底：任何未预料的 Domain 异常，都翻译成 Application 语义
            raise ContactServiceInternalError(f"获取联系人 {contact_id} 时发生系统错误") from e
        
        return contact

    def search_contacts(self, keyword: str) -> list[Contact]:
        """
        用例：搜索联系人。
        """
        try:
            return self._book.search_by_name(keyword)

        except DomainError as e:
            raise ContactServiceInternalError(
                "搜索联系人时发生系统错误"
            ) from e

    def list_all_contacts(self) -> list[Contact]:
        """
        用例：列出所有联系人

        职责：
            1. 通过 list(self._book) 利用 __iter__() 协议创建新列表
                - 新列表中的 Contact 对象仍是原对象的引用
                - 但列表容器本身是新创建的，修改列表（增删元素）不会影响 ContactBook 内部状态
            2. 所有联系人的列表（新列表，独立于 ContactBook 内部存储）
            3. 2. 将 Domain 异常转换为 Application 语义
        """
        try:
            return list(self._book)

        except DomainError as e:
            raise ContactServiceInternalError(
                "获取联系人列表时发生系统错误"
            ) from e   # ← 利用 __iter__() 协议
        
    def change_phone(self, contact_id: str, new_phone: str) -> None:
        # 请求 ContactBook 完成手机号修改
        try:
            self._book.change_contact_phone(contact_id, new_phone)
        except ContactIdNotFoundError as e:
            raise ContactNotFoundError(f"联系人 {contact_id} 不存在") from e 
        except ContactValidationError as e:
            raise ContactInputError( f"联系人 {contact_id} 的手机号 {new_phone} 校验失败：{e}") from e
        except DuplicatePhoneError as e:
            raise ContactDuplicateError(f"手机号 {new_phone} 已被占用") from e
        except DomainError as e:
            raise ContactServiceInternalError(f"修改联系人 {contact_id} 的手机号时发生系统错误") from e

        self._tracker.mark_dirty()