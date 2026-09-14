# contact_service.py

# ContactService 的「职责边界」：
#   1. 对外提供用例入口 → 它是 UI/CLI 唯一能调用的业务接口，
#      每个方法对应一个「用户想做的事」。
#   2. 协调 Domain + 翻译异常 → 它自己不实现业务规则，
#      而是把请求转成 Domain 调用，再把 Domain 的异常
#      翻译成 Application 语义（DomainError → ContactServiceError）。
#   3. 成功修改后通知 DirtyTracker → 它不负责保存，
#      只负责「告诉持久化层：数据变了」。保存策略由 tracker 决定。
#   4. 不暴露技术细节（如 index）→ UI 只看到 name/phone/contact_id，
#      看不到 ContactBook 内部的索引结构。这是分层的关键：
#      Domain 的实现细节不能泄漏到 Application 之上。

from contact_manager.domain import (
    Contact,                    # 领域实体
    ContactBook,                # 领域聚合根（联系人集合）
    DomainError,                # 领域异常基类（兜底用）
    ContactValidationError,     # 字段校验失败
    ContactIdNotFoundError,     # ID 找不到
    ContactConflictError,       # 冲突（当前未直接用到，但保留）
    DuplicateContactIdError,    # ID 重复（当前未直接用到）
    DuplicatePhoneError         # 手机号重复
)
# 从 Domain 导入「需要翻译的异常」和「需要操作的对象」。
#
# 注意导入的异常都是「具体的」，除了 DomainError 作为兜底。
# 这样 ContactService 能对每一类领域失败给出精确的 Application 语义，
# 而不是所有异常都变成同一个错误。

from contact_manager.protocols import (
    DirtyTracker,               # 端口：标记脏数据
    ContactIdGenerator,         # 端口：生成 ID
    ContactIdGenerationError    # 端口契约：ID 生成失败
)
# 从 protocols 导入「端口」，而不是具体实现。
#
# 这是依赖倒置：ContactService 依赖抽象（Protocol），
# 具体实现（UuidContactIdGenerator、JsonDirtyTracker 等）
# 由组装层注入。ContactService 不知道也不关心它们是什么。

class ContactServiceError(Exception):
    """Service 层异常的基类"""
    pass
# 所有 Application 层异常的根。
# 好处：UI 层可以只 catch ContactServiceError 一种类型，
# 就能覆盖所有「业务用例失败」的情况，不用逐个列举。

class ContactNotFoundError(ContactServiceError):
    """联系人不存在"""
    pass
# 对应 Domain 的 ContactIdNotFoundError。

class ContactInputError(ContactServiceError):
    """用户提供的数据无法通过输入/业务验证"""
    pass
# 对应 Domain 的 ContactValidationError。

class ContactDuplicateError(ContactServiceError):
    """用户请求造成了联系人唯一性冲突"""
    pass
# 对应 Domain 的 DuplicatePhoneError。

class ContactServiceInternalError(ContactServiceError):
    """用户无法修复的系统内部错误"""
    pass
# 兜底：用户没法通过「改输入」解决的错误（ID 生成失败、未知 Domain 异常）。
# 和前面三个的区别：前三个是「用户能理解的业务失败」，这个是「系统出问题了」，UI 通常显示「请稍后重试」之类。

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
        把外部传入的 contact_book、tracker 对象保存为 ContactService 实例的私有属性 _book，供后续方法调用使用。
        使用时，Service 收到请求后，不自己处理数据，而是委托给 _book：
            service = ContactService(book,tracker,id_generator)  
            service._book.add_contact(...)   # 内部通过 _book 调用 Domain 层方法
        """
        # 依赖注入的含义：
        #   ContactService 不自己 new ContactBook()、不自己 new UuidGenerator()，
        #   而是由外部（组装层）构造好、传进来。
        #
        # 为什么这样做？
        #   1. 可测试：测试时传一个假的 tracker、假的 id_generator。
        #   2. 可替换：换持久化策略、换 ID 策略，不用改 ContactService。
        #   3. 依赖抽象：参数类型是 Protocol（DirtyTracker、ContactIdGenerator），不是具体类。

        self._book = contact_book
        # 领域聚合根。ContactService 通过它操作联系人集合。
        # 下划线前缀 = 私有，UI 层不应该直接访问 service._book。

        self._tracker = tracker
        # 脏标记端口。业务状态改变后调 mark_dirty()，
        # 具体「怎么标记、什么时候保存」由注入的实现决定。

        self._id_generator = id_generator
        # ID 生成端口。add_contact 时用它生成新 ID。
        # 同样是 Protocol 类型，不绑死具体实现。

    def add_contact(self, name: str, phone: str) -> Contact:
        """
        用例：添加联系人

        职责：
            1. 创建 Contact 对象，Contact 自己验证数据
            2. 调用 ContactBook.add_contact()， ContactBook检查集合规则，加入通讯录
            3. 返回创建的联系人
        """
        # ── 步骤 1：生成 ID ──
        # 注意：ID 生成是「应用层职责」，不是 Domain 职责。
        # Contact 只接收 ID，不负责生成 ID。
        # 生成器是注入的端口，所以具体策略（UUID/序列号）与 ContactService 无关。
        try:
            contact_id = self._id_generator.generate()
        except ContactIdGenerationError as e:
            # 端口失败 → 翻译成 Application 语义的「内部错误」。
            # 用户无法修复「ID 生成器坏了」，所以归入 InternalError。
            raise ContactServiceInternalError(
                "添加联系人时无法生成 ID"
            ) from e

        # ── 步骤 2：领域操作 + 异常翻译 ──
        # 这里体现 ContactService 的核心职责：
        # 把「Domain 的技术性失败」翻译成「Application 的业务语义失败」。
        try:
            contact = Contact(contact_id, name, phone)
            # Contact 构造函数内部做字段校验（name/phone 是否合法）。
            # 校验失败会抛 ContactValidationError。

            self._book.add_contact(contact)
            # ContactBook 检查集合级规则（如手机号是否重复）。
            # 冲突会抛 DuplicatePhoneError。

        except ContactValidationError as e:
            # 字段非法 → 用户输入有问题 → ContactInputError
            raise ContactInputError(str(e)) from e
        except DuplicatePhoneError as e:
            # 手机号冲突 → 业务冲突 → ContactDuplicateError
            # 这里重新组织了消息，让它更贴近用户视角。
            raise ContactDuplicateError(f"手机号 {phone} 已被占用") from e
        except DomainError as e:
            # 兜底：任何未预料的 Domain 异常
            # 都翻译成「系统内部错误」，而不是泄漏原始异常给 UI。
            raise ContactServiceInternalError("添加联系人时发生系统错误") from e

        # ── 步骤 3：标记脏数据 ──
        # 注意位置：在「业务操作成功之后」。
        # 如果前面任何一步抛异常，就不会执行到这里，也就不会误标记。
        #
        # 为什么是「标记」而不是「保存」？
        #   保存策略（立刻存/延迟存/批量存）是持久化层的决策，
        #   Application 只负责说「我改了数据」，不决定何时落盘。
        self._tracker.mark_dirty()   # ✅ 只标记 dirty，不直接保存

        return contact
        # 返回创建的 Contact，让 UI 能拿到 ID 等信息。

    def delete_contact(self, contact_id: str) -> Contact:
        """
        用例：删除指定id的联系人。

        职责：
            1. 删除指定id的联系人
            2. 返回被删除的 Contact 对象
        """
        # 返回被删除对象，而不是 None：
        # UI 可能想显示「已删除 Tom」之类的反馈，需要知道删的是谁。

        try:
            deleted_contact = self._book.remove_by_id(contact_id)
            # Domain 的 remove_by_id 负责：
            #   - 检查 ID 存在性（不存在抛 ContactIdNotFoundError）
            #   - 从集合中移除
            #   - 返回被移除的 Contact

        except ContactIdNotFoundError as e:
            # Domain 的技术性「找不到 ID」 → Application 的「联系人不存在」
            raise ContactNotFoundError(f"联系人 {contact_id} 不存在") from e
        except DomainError as e:
            # 兜底
            raise ContactServiceInternalError(f"删除联系人 {contact_id} 时发生系统错误") from e
        
        self._tracker.mark_dirty()
        # 只有删除成功才走到这里，标记脏数据。
        return deleted_contact
        
    def get_contact(self, contact_id: str) -> Contact:
        """
        用例：查看联系人详情

        职责：
            1. 获取指定id的联系人
            2. 返回查到的 Contact 对象
        """
        try:
            contact = self._book.get_by_id(contact_id)

        except ContactIdNotFoundError as e:
            raise ContactNotFoundError(f"联系人 {contact_id} 不存在") from e
        except DomainError as e:
            raise ContactServiceInternalError(f"获取联系人 {contact_id} 时发生系统错误") from e
        
        return contact

    def search_contacts(self, keyword: str) -> list[Contact]:
        """
        用例：搜索联系人。
        """

        try:
            return self._book.search_by_name(keyword)
            # Domain 负责搜索逻辑（匹配规则、大小写处理等）。
            # ContactService 只是转发 + 异常翻译。

        except DomainError as e:
            # 这里没有「NotFound」分支——搜索无结果通常返回空列表，
            # 不是异常。所以只兜底 DomainError。
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
            3. 将 Domain 异常转换为 Application 语义
        """
        # `list(self._book)` 的意图：
        #   ContactBook 实现了 __iter__，所以能被 list() 消费。
        #   返回的 list 是「新容器」，但里面的 Contact 是原对象引用。
        #
        #   为什么不在 Application 层直接返回 ContactBook 本身？
        #     那会把内部存储暴露给 UI，UI 可能意外修改它。
        try:
            return list(self._book)

        except DomainError as e:
            raise ContactServiceInternalError(
                "获取联系人列表时发生系统错误"
            ) from e
        
    def change_phone(self, contact_id: str, new_phone: str) -> None:
        # 返回 None：调用方不需要拿到 Contact 本身，
        # 修改是否成功由「有没有抛异常」表达。

        # 请求 ContactBook 完成手机号修改
        try:
            self._book.change_contact_phone(contact_id, new_phone)
            # Domain 负责：
            #   - 找联系人（可能抛 ContactIdNotFoundError）
            #   - 校验新手机号（可能抛 ContactValidationError）
            #   - 检查唯一性（可能抛 DuplicatePhoneError）

        except ContactIdNotFoundError as e:
            raise ContactNotFoundError(f"联系人 {contact_id} 不存在") from e 
        except ContactValidationError as e:
            # 这里把 contact_id 和 new_phone 都放进消息里，
            # 因为「修改手机号」失败时，两个信息都有助于用户定位问题。
            raise ContactInputError(
                f"联系人 {contact_id} 的手机号 {new_phone} 校验失败：{e}"
            ) from e
        except DuplicatePhoneError as e:
            raise ContactDuplicateError(f"手机号 {new_phone} 已被占用") from e
        except DomainError as e:
            raise ContactServiceInternalError(
                f"修改联系人 {contact_id} 的手机号时发生系统错误"
            ) from e

        self._tracker.mark_dirty()