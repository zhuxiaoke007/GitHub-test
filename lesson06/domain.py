"""
通讯录核心模块 - 定义联系人数据结构和通讯录管理功能

本模块包含两个核心类：
1. Contact: 表示单个联系人，包含姓名和电话
2. ContactBook: 管理多个联系人，提供增删改查等功能
"""
class ContactValidationError(Exception):
    pass

class DuplicateContactError(Exception):
    pass

class Contact:
    """
    联系人类 - 表示单个联系人的数据
    
    职责：
    1. 存储联系人的姓名和电话
    2. 验证数据的合法性(姓名非空,电话11位数字)
    3. 支持数据转换（to_dict / from_dict）
    4. 通过属性（@property）提供只读访问
    
    数据验证规则：
        - 姓名：不能为空字符串
        - 电话：必须为11位数字（0-9）
    
    封装设计：
        - _name 和 _phone 是私有属性（以下划线开头）
        - 通过 @property 提供只读访问
        - 通过 change_name() 和 change_phone() 提供修改方法（带验证）
    """    
    def __init__(self, name, phone):
        """
        初始化联系人对象
        
        参数：
            name: str，联系人姓名
            phone: str，联系人电话（11位数字）
        
        工作流程：
            1. 验证姓名是否合法
            2. 验证电话是否合法
            3. 将验证通过的数据存储到内部属性
        
        可能抛出的异常：
            ContactValidationError: 姓名或电话格式不合法
        """
        # 调用静态方法验证数据   
        Contact.validate_name(name)
        Contact.validate_phone(phone)
        # 将姓名保存到内部属性 _name
        # 将电话保存到内部属性 _phone
        # 在Contact对象中，数据存储为字符串，例如 Contact("Tom", "13800000001")
        self._name = name
        self._phone = phone

    @staticmethod
    def validate_name(name):
        """
        静态方法：验证姓名是否合法
        
        参数：
            name: str，待验证的姓名
        
        可能抛出的异常：
            ContactValidationError: 姓名为空字符串
        
        设计说明：
            使用 @staticmethod 装饰器，表示这是静态方法
            不依赖实例，可以在类上直接调用：Contact.validate_name("张三")
        """
        if name == "":
            raise ContactValidationError("姓名不能为空")

    @staticmethod
    def validate_phone(phone):
        """
        静态方法：验证电话是否合法
        
        参数：
            phone: str，待验证的电话号码
        
        验证规则：
            1. 必须全部是数字（isdigit()）
            2. 长度必须为11位
        
        可能抛出的异常：
            违反业务规则 → 抛出领域异常 ContactValidationError
        
        注意：
            电话号码使用字符串类型，因为不涉及数学运算
            且以0开头的号码如果转为整数会丢失前导0
        """
        # isdigit() 检查是否所有字符都是数字
        # len() 检查长度是否为11
        if not phone.isdigit() or len(phone) != 11:
            raise ContactValidationError("电话号码必须是 11 位数字")

    def change_name(self, new_name):
        """
        修改联系人姓名
        
        参数：
            new_name: str，新的姓名
        
        工作流程：
            1. 验证新姓名是否合法
            2. 更新内部属性
        
        可能抛出的异常：
            ContactValidationError: 新姓名为空
        """
        Contact.validate_name(new_name)                 # 验证新姓名
        self._name = new_name                           # 更新私有属性

    def change_phone(self, new_phone):
        """
        修改联系人电话
        
        参数：
            new_phone: str，新的电话号码
        
        工作流程：
            1. 验证新电话是否合法
            2. 更新内部属性
        
        可能抛出的异常：
            ContactValidationError: 新电话格式不合法
        """
        Contact.validate_phone(new_phone)               # 验证新电话
        self._phone = new_phone                         # 更新私有属性
    
    # 装饰器，它的作用是把方法name()"伪装"成属性name
    @property
    def name(self):                                #name 是一个 property 对象，它有 getter（读取方法），它没有 setter（写入方法）
        """
        属性方法：读取联系人姓名
        
        使用 @property 装饰器将方法变为只读属性
        调用方式：contact.name（不需要括号）
        
        作用：
            1. 提供对私有属性 _name 的只读访问
            2. 不允许外部直接修改（没有 setter 方法）
        
        返回值：
            str，联系人的姓名
        """
        return self._name
    
    @property
    def phone(self):
        """
        属性方法：读取联系人电话
        
        使用 @property 装饰器将方法变为只读属性
        调用方式：contact.phone（不需要括号）
        
        返回值：
            str，联系人的电话号码
        """
        return self._phone

    #类方法，将dict转换为单个联系人，返回Contatc实例
    @classmethod
    def from_dict(cls, data):                       # data 参数必须是单个字典，不能是整个列表。使用时应首先遍历列表，每次传入一个字典
        """
        类方法：从字典创建 Contact 对象
        
        参数：
            data: dict，包含联系人数据的字典
                  必须包含 "name" 和 "phone" 键
                  例如：{"name": "张三", "phone": "13800138000"}
        
        返回值：
            Contact 实例
        
        使用 @classmethod 装饰器，第一个参数是 cls（类本身）
        而不是 self（实例）
        
        用途：
            从文件加载数据时，将字典转换为 Contact 对象
        
        可能抛出的异常：
            KeyError: 字典中缺少 "name" 或 "phone" 键
            ContactValidationError: 数据格式不合法（由 __init__ 抛出）
        """
        # 从字典中提取数据
        name = data["name"]
        phone = data["phone"]
        # 调用类构造函数创建新实例
        return cls(name, phone)   
    
    #实例方法，将单个联系人实例转换为dict，返回dict
    def to_dict(self):
        """
        实例方法：将 Contact 对象转换为字典
        
        返回值：
            dict，包含联系人数据的字典
            格式：{"name": "张三", "phone": "13800138000"}
        
        用途：
            保存数据到文件时，将 Contact 对象转换为可序列化的字典
        """
        return{
            "name": self.name,                        # 通过属性读取姓名
            "phone": self.phone                       # 通过属性读取电话
            }

class ContactBook:
    """
    通讯录类 - 管理所有联系人的容器
    
    职责：
    1. 存储联系人列表(_contacts)
    2. 提供添加、删除、查询等操作方法
        ├── add_contact(contact)
        ├── get(index)
        ├── remove(index)
        ├── delete_by_name(name)
        ├── search_by_name(name)
        ├── __len__()
        ├── __iter__()
        ├── to_data()
        ├── from_data(data)
        ├── _is_phone_used_by_other()
        └── change_contact_phone()
    
    内部数据结构：
        _contacts: list[Contact] - 联系人对象列表
    """
    def __init__(self):
        """
        初始化通讯录对象
        创建空的联系人列表
        """
        self._contacts : list[Contact] = []    # 内部联系人列表，存储 Contact 对象

    #给ContactBook类创建一个查询_contacts列表的长度的方法
    def __len__(self):
        """
        特殊方法：返回通讯录中的联系人数量
        作用：支持 len(contact_book) 语法
        返回值: int, 联系人的总数
        """
        return len(self._contacts)
    
    #给ContactBook类创建一个遍历方法，返回一个迭代器iterator
    def __iter__(self):
        """
        特殊方法：返回一个迭代器
        作用：支持 for contact in contact_book 遍历语法
        返回值：迭代器对象，用于遍历 _contacts 列表
        
        通过实现 __iter__()，这个类的实例就可以在 for 循环中使用
        这是 Python 的"迭代器协议"
        """
        return iter(self._contacts)     #它实际上定义了一个能力契约：“ContactBook 是一个可以被遍历的对象

    def add_contact(self, contact: "Contact") -> None:   
        """
        将一个联系人加入ContactBook
        
        参数：
            contact: 待添加的 Contact 对象
        
        工作流程：
            1. 检查电话号码是否已存在（不允许重复）
            2. 将新联系人添加到列表中
        
        可能抛出的异常：
            DuplicateContactError: 当手机号已存在时抛出
        
        设计说明：
            调用方负责创建 Contact 对象，此方法只负责存储
        """
        # 第1步：遍历检查电话号码是否已存在
        for existing in self._contacts:
            if existing.phone == contact.phone:
                raise DuplicateContactError(f"Phone number {contact.phone} already exists")
        # 第2步：将新联系人添加到列表中
        self._contacts.append(contact)

    def get(self, index: int) -> "Contact":
        """
        根据索引获取指定联系人
        
        返回值: Contact 对象
        
        注意：
            如果索引超出范围，会抛出 IndexError
        """
        if index < 0 or index >= len(self._contacts):
            raise IndexError(f"Index {index} out of range")
        return self._contacts[index]
    
    def remove(self, index: int) -> "Contact":
        """
        根据索引删除指定联系人

        返回值：被删除的 Contact 对象
        
        注意：
            使用 pop() 方法删除并返回被删除的元素, 索引超出范围时由 list.pop() 自动抛出IndexError
        """
        if index < 0 or index >= len(self._contacts):
            raise IndexError(f"Index {index} out of range")
        return self._contacts.pop(index)
        
    def delete_by_name(self, name):
        """
        根据姓名删除所有匹配的联系人
        
        返回值：被删除的联系人列表
        
        工作流程：
            1. 从列表末尾向前遍历（从最后一个元素到第一个）
            2. 如果匹配姓名，删除该元素
            3. 返回被删除的联系人列表
        """
        deleted = []                                            # 初始化被删除的联系人列表
        for i in range(len(self._contacts) - 1, -1, -1):        #从最后一个索引开始，递减到 0. range(起始, 终止, 步长) 这里步长为 -1 表示递减
            # 检查当前元素的姓名是否匹配
            if self._contacts[i].name == name:
                deleted.append(self.remove(i))                   # 调用 remove 删除
        # # 添加返回值：被删除的联系人列表,如果没有删除任何联系人，返回空列表[]
        return deleted

    def search_by_name(self, keyword: str) -> list[Contact]:
        """
        按关键字搜索联系人（不区分大小写，包含匹配）

        Returns:
            匹配的联系人列表（新列表，元素为原 Contact 对象引用）
            如果关键字为空，返回空列表
        """
        # 边界情况：空关键字
        if not keyword or not keyword.strip():
            return []

        # 标准化关键字（小写，去除首尾空格）
        keyword_lower = keyword.strip().lower()

        # 创建新列表，存放匹配的联系人
        result = []
        for contact in self._contacts:
            if keyword_lower in contact.name.lower():
                result.append(contact)

        return result

    
    #验证临时联系人集合中号码是否重复
    @staticmethod
    def _validate_no_duplicate_phone(contacts):
        """
        静态私有方法：检查联系人集合中是否有重复的电话号码
        
        参数：
            contacts: list[Contact]，要检查的联系人列表
        
        可能抛出的异常：
            ValueError: 发现重复的电话号码
        
        设计说明：
            1. 使用 @staticmethod 装饰器，表示这是一个静态方法
               不需要 self 参数，也不依赖实例状态
            2. 方法名以下划线开头(_validate...)，表示这是内部方法
               不应该被外部直接调用
            3. 使用集合(set)来检测重复，时间复杂度 O(n)
        """
        seen = set()                                              # 创建一个空集合，用于存储已经见过的电话号码
        for contact in contacts:                                  # 如果电话号码已经在集合中，说明重复了
            if contact.phone in seen:
                raise ValueError(f"重复电话号码：{contact.phone}")
            seen.add(contact.phone)                                # 将当前号码加入集合

    #将所有联系人转成dict
    def to_data(self)-> list[dict]:
        """
        将通讯录中的所有联系人转换为字典列表（用于持久化）
        
        返回值：
            list[dict]，每个字典包含一个联系人的数据
            格式：[{"name": "张三", "phone": "13800138000"}, ...]
        
        注意：
            列表中的字典是独立副本，修改字典不会影响原始的 Contact 对象
        """                         
        result = []                        # 1. 先初始化空列表
        for item in self._contacts:        # 2. 遍历每个联系人
            result.append(item.to_dict())  # 3. 调用 to_dict() 转换并添加到列表
        return result                      # 4. 返回结果

    #将dict加载到联系人列表中
    def from_data(self, data: list[dict])-> None:
        """
        从字典列表恢复数据到当前通讯录实例（清空现有数据后加载）
        
        参数：
            data: list[dict]，包含联系人数据的字典列表
        
        工作流程（保证原子性）：
            1. 构建临时列表（不修改原有数据）
            2. 验证临时列表中的数据是否合法
            3. 如果全部验证通过，一次性替换原有数据
        
        原子性保证：
            如果在验证过程中发现错误, _contacts 保持原样不变
            只有全部验证通过才会更新，避免数据处于不一致状态
        
        可能抛出的异常：
            ValueError: 数据格式不合法或存在重复电话号码
            KeyError: 字典中缺少 "name" 或 "phone" 键
        """
        # 第1步：构建临时列表
        # 将字典转换为 Contact 对象，存入临时列表
        # 如果字典格式有问题，这里会抛出异常
        temp_contacts = []
        for item in data:
            contact = Contact.from_dict(item)                     # 从字典创建 Contact 对象
            temp_contacts.append(contact)                         # 添加到临时列表
        
        # 2. 验证临时列表（不修改原有数据）,检查是否有重复的电话号码
        self._validate_no_duplicate_phone(temp_contacts)
        
        # 3. 全部成功，原子性更新,用临时列表替换原有的 _contacts 列表
        self._contacts = temp_contacts

    def _is_phone_used_by_other(self, contact: Contact, phone: str) -> bool:
        """检查指定电话是否被其他联系人使用"""
        for existing_contact in self._contacts:
            if existing_contact is not contact and existing_contact.phone == phone:
                return True
        return False

    def change_contact_phone(self, contact: Contact, new_phone: str) -> None:
        # 维护集合唯一性规则
        if self._is_phone_used_by_other(contact, new_phone):
            raise DuplicateContactError(f"号码 {new_phone} 已被其他联系人使用")
        
        # 委托给 Contact 修改自身
        contact.change_phone(new_phone)
    
"""
核心设计模式说明：
封装：使用 _name、_phone 等私有属性，通过方法进行访问和修改
数据验证：在数据进入系统时就进行验证（构造函数、setter方法），保证数据始终合法
原子性操作：from_data() 方法使用临时列表，全部验证通过后才更新，避免数据处于不一致状态
协议一致性：实现了 __len__ 和 __iter__ 特殊方法，使类可以像列表一样使用
"""