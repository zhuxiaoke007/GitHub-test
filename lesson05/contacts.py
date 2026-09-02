"""
通讯录核心模块 - 定义联系人数据结构和通讯录管理功能

本模块包含两个核心类：
1. Contact: 表示单个联系人，包含姓名和电话
2. ContactBook: 管理多个联系人，提供增删改查等功能
"""

class ContactBook:
    """
    通讯录类 - 管理所有联系人的容器
    
    职责：
    1. 存储联系人列表（_contacts）
    2. 提供添加、删除、查询等操作方法
    3. 支持数据导入导出（to_data / from_data）
    4. 跟踪数据是否被修改（is_dirty属性）
    
    内部数据结构：
        _contacts: list[Contact] - 联系人对象列表
        _saved_data: list[dict] - 上次保存时的数据快照，用于判断数据是否被修改
    """
    def __init__(self):
        """
        初始化通讯录对象
        创建空的联系人列表，并保存一个空快照用于脏标记判断
        """
        self._contacts = []    # 内部联系人列表，存储 Contact 对象
        self._saved_data= []   # 初始为空通讯录的快照（保存时的数据副本）

    #给ContactBook类创建一个查询_contacts列表的长度的方法
    def __len__(self):
        """
        特殊方法：返回通讯录中的联系人数量
        作用：支持 len(contact_book) 语法
        返回值：int，联系人的总数
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

    #添加一个新联系人
    def add_contact(self, name: str, phone: str):   
        """
        添加一个新联系人
        
        参数：
            name: str，联系人姓名
            phone: str，联系人电话（必须是11位数字）
        
        工作流程：
            1. 检查电话号码是否已存在（不允许重复）
            2. 创建 Contact 对象（会自动验证姓名和电话的合法性）
            3. 将新联系人添加到列表中
        
        可能抛出的异常：
            ValueError: 电话号码重复，或姓名/电话格式不合法
        
        设计说明：
            由 ContactBook 负责创建 Contact 对象，而不是在外部创建
            这样可以让 ContactBook 完全控制联系人的创建过程
        """
        # 第1步：检查电话号码是否已存在
        # 遍历现有的所有联系人，如果有相同号码则抛出异常
        for item in self._contacts:
            if item.phone == phone:
                raise ValueError("联系人号码重复")            #异常向上传播，返回到 main.py 中的调用点，寻找匹配的 except 块
        # 第2步：创建 Contact 对象（构造时会自动验证数据）
        contact = Contact(name, phone)
        # 第3步：将新联系人添加到列表中
        self._contacts.append(contact)

    #根据index查询指定联系人
    def get_contact(self, index):
        """
        根据索引获取指定联系人
        
        参数：
            index: int，联系人在列表中的位置（从0开始）
        
        返回值：
            Contact 对象
        
        注意：
            如果索引超出范围，会抛出 IndexError
            这个方法通常由 UI 层调用，用于显示或操作特定联系人
        """
        return self._contacts[index]
    
    #根据index删除指定联系人
    def delete_contact(self, index):
        """
        根据索引删除指定联系人
        
        参数：
            index: int，联系人在列表中的位置（从0开始）
        
        注意：
            使用 pop() 方法删除并返回被删除的元素
            如果索引超出范围，会抛出 IndexError
        """
        self._contacts.pop(index)                                # pop() 会移除列表中指定位置的元素
        
    #根据name删除指定联系人
    def delete_by_name(self, name):
        """
        根据姓名删除所有匹配的联系人
        
        参数：
            name: str，要删除的联系人姓名
        
        返回值：
            int，实际删除的联系人数量
        
        工作流程：
            1. 从列表末尾向前遍历（从最后一个元素到第一个）
            2. 如果匹配姓名，删除该元素
            3. 统计删除数量
        
        为什么从后往前遍历？
            如果从前往后删除，删除元素后列表长度会变化，导致索引错乱
            从后往前删除可以避免这个问题，因为删除后面的元素不影响前面的索引
        
        可能抛出的异常：
            ValueError: 没有找到任何匹配的联系人
        """
        deleted_count = 0                                       # 初始化计数器
        for i in range(len(self._contacts) - 1, -1, -1):        #从最后一个索引开始，递减到 0. range(起始, 终止, 步长) 这里步长为 -1 表示递减
            # 检查当前元素的姓名是否匹配
            if self._contacts[i].name == name:
                self.delete_contact(i)                           # 调用 delete_contact 删除
                deleted_count += 1
        # 如果没有删除任何联系人，抛出异常
        if deleted_count == 0:
            raise ValueError(f"联系人 '{name}' 不存在")
        return deleted_count                                    # 添加返回值：总计删除数量
    
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
            2. 方法名以下划线开头（_validate...），表示这是内部方法
               不应该被外部直接调用
            3. 使用集合（set）来检测重复，时间复杂度 O(n)
        """
        seen = set()                                              # 创建一个空集合，用于存储已经见过的电话号码
        for contact in contacts:                                  # 如果电话号码已经在集合中，说明重复了
            if contact.phone in seen:
                raise ValueError(f"重复电话号码：{contact.phone}")
            seen.add(contact.phone)                                # 将当前号码加入集合

    #将所有联系人转成dict
    def to_data(self):
        """
        将通讯录中的所有联系人转换为字典列表
        
        返回值：
            list[dict]，每个字典包含一个联系人的数据
            格式：[{"name": "张三", "phone": "13800138000"}, ...]
        
        用途：
            1. 保存数据到文件（序列化）
            2. 生成数据快照用于脏标记判断
        
        注意：
            列表中的字典是独立副本，修改字典不会影响原始的 Contact 对象
        """                         
        result = []                        # 1. 先初始化空列表
        for item in self._contacts:        # 2. 遍历每个联系人
            result.append(item.to_dict())  # 3. 调用 to_dict() 转换并添加到列表
        return result                      # 4. 返回结果

    #将dict加载到联系人列表中
    def from_data(self, data):
        """
        从字典列表恢复联系人数据
        
        参数：
            data: list[dict]，包含联系人数据的字典列表
        
        工作流程（保证原子性）：
            1. 构建临时列表（不修改原有数据）
            2. 验证临时列表中的数据是否合法
            3. 如果全部验证通过，一次性替换原有数据
            4. 更新数据快照
        
        原子性保证：
            如果在验证过程中发现错误，_contacts 保持原样不变
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

        # # 第4步：更新数据快照
        # 保存当前数据的副本，用于后续判断数据是否被修改
        # 注意：保存的是数据的值副本，而不是引用
        self._saved_data = self.to_data()  # 或直接 data（如果 data 不会被外部修改）
    
    @property
    def is_dirty(self):
        """
        属性方法：判断通讯录数据是否被修改过（是否"脏"）
        
        返回值：
            bool，True 表示数据已被修改，需要保存
                False 表示数据未修改，无需保存
        
        实现原理：
            比较当前数据（to_data()）和保存的快照（_saved_data）
            如果不相等，说明数据发生了变化
        
        使用场景：
            在程序退出时，根据这个属性决定是否需要保存数据
        """
        return self.to_data() != self._saved_data
    
    def mark_saved(self) -> None:
        """
        标记当前数据为已保存状态
        
        效果：
            在数据成功保存到存储（文件）后调用此方法 (也就是将当前联系人列表（_contacts）的数据副本保存到 _saved_data)
            作用是更新内部的快照（_saved_data）
            此后，is_dirty 会比较当前数据和这个快照，返回 False（表示数据已同步）
        
        设计说明：
            1. 这是一个"公开方法"（没有下划线前缀），允许外部调用
            2. 外部调用者（main.py）负责协调保存流程，但不直接操作私有属性
            3. ContactBook 自己维护 _saved_data，保持封装性
            4. 方法名使用"mark"（标记）而不是"set"（设置），更清晰地表达语义
            
        为什么不直接在 save() 方法里调用？
            因为 ContactBook 不知道 Storage 的存在（依赖倒置原则）
            保存逻辑由 main.py 协调，ContactBook 只负责更新自己的状态
        """
    # 获取当前所有联系人数据（列表形式）
    # to_data() 返回的是新创建的列表和字典，是数据的副本
    # 赋值给 _saved_data，保存当前状态的快照
        self._saved_data = self.to_data()
    
class Contact:
    """
    联系人类 - 表示单个联系人的数据
    
    职责：
    1. 存储联系人的姓名和电话
    2. 验证数据的合法性（姓名非空，电话11位数字）
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
            ValueError: 姓名或电话格式不合法
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
            ValueError: 姓名为空字符串
        
        设计说明：
            使用 @staticmethod 装饰器，表示这是静态方法
            不依赖实例，可以在类上直接调用：Contact.validate_name("张三")
        """
        if name == "":
            raise ValueError("姓名不能为空")

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
            ValueError: 电话号码格式不合法
        
        注意：
            电话号码使用字符串类型，因为不涉及数学运算
            且以0开头的号码如果转为整数会丢失前导0
        """
        # isdigit() 检查是否所有字符都是数字
        # len() 检查长度是否为11
        if not phone.isdigit() or len(phone) != 11:
            raise ValueError("电话号码必须是 11 位数字")

    def change_name(self, new_name):
        """
        修改联系人姓名
        
        参数：
            new_name: str，新的姓名
        
        工作流程：
            1. 验证新姓名是否合法
            2. 更新内部属性
        
        可能抛出的异常：
            ValueError: 新姓名为空
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
            ValueError: 新电话格式不合法
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
            ValueError: 数据格式不合法（由 __init__ 抛出）
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
    
"""
核心设计模式说明：
封装：使用 _name、_phone 等私有属性，通过方法进行访问和修改
数据验证：在数据进入系统时就进行验证（构造函数、setter方法），保证数据始终合法
脏标记模式：通过 _saved_data 快照和 is_dirty 属性，高效判断数据是否需要保存
原子性操作：from_data() 方法使用临时列表，全部验证通过后才更新，避免数据处于不一致状态
协议一致性：实现了 __len__ 和 __iter__ 特殊方法，使类可以像列表一样使用
"""