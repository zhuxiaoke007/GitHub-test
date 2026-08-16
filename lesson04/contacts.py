class ContactBook:
    #创建ContactBook类
    def __init__(self):
        self._contacts = []

    #查询_contacts列表的长度
    def __len__(self):
        return len(self._contacts)

    #添加一个新联系人
    def add_contact(self, contact):              
        for item in self._contacts:
            if contact.phone == item.phone:
                raise ValueError("联系人号码重复")
        self._contacts.append(contact)

    #根据index查询指定联系人
    def get_contact(self, index):
        return self._contacts[index]
    
    #给ContactBook类创建一个遍历方法，返回一个迭代器iterator
    def __iter__(self):
        return iter(self._contacts)

    #删除除指定联系人
    def delete_contact(self, index):
        self._contacts.pop(index)
        
    def delete_by_name(self, name):
        deleted_count = 0
        for i in range(len(self._contacts) - 1, -1, -1):
            if self._contacts[i].name == name:
                self.delete_contact(i)
                deleted_count += 1
        if deleted_count == 0:
            raise ValueError(f"联系人 '{name}' 不存在")
        return deleted_count  # ✅ 添加返回值
    
    #验证临时联系人集合中号码是否重复
    @staticmethod
    def _validate_no_duplicate_phone(contacts):
        """检查传入集合中是否有重复电话号码"""
        seen = set()
        for contact in contacts:
            if contact.phone in seen:
                raise ValueError(f"重复电话号码：{contact.phone}")
            seen.add(contact.phone)

    #将所有联系人转成dict
    def to_data(self):                         
        result = []                        # ✅ 1. 先初始化空列表
        for item in self._contacts:
            result.append(item.to_dict())  # ✅ 2. 调用每个联系人的 to_dict()
        return result                      # ✅ 3. 返回结果

    #将dict加载到联系人列表中
    def from_data(self, data):
        """从字典列表恢复联系人状态（原子性）"""
        # 1. 构建临时列表
        temp_contacts = []
        for item in data:
            contact = Contact.from_dict(item)
            temp_contacts.append(contact)
        
        # 2. 验证临时列表（不修改原有数据）
        self._validate_no_duplicate_phone(temp_contacts)
        
        # 3. 全部成功，原子性更新
        self._contacts = temp_contacts
      
    
class Contact:
    def __init__(self, name, phone):
        # 校验并保存
        Contact.validate_name(name)
        Contact.validate_phone(phone)
        # 将姓名保存到内部属性 _name
        # 将电话保存到内部属性 _phone
        self._name = name
        self._phone = phone

    @staticmethod
    def validate_name(name):
        if name == "":
            raise ValueError("姓名不能为空")

    @staticmethod
    def validate_phone(phone):
        if not phone.isdigit() or len(phone) != 11:
            raise ValueError("电话号码必须是 11 位数字")

    def change_name(self, new_name):
        Contact.validate_name(new_name)
        self._name = new_name

    def change_phone(self, new_phone):
        Contact.validate_phone(new_phone)
        self._phone = new_phone
    
    # 装饰器，它的作用是把方法name()"伪装"成属性name
    @property
    def name(self):
        """通过 name 属性读取姓名"""
        return self._name
    
    @property
    def phone(self):
        """通过 phone 属性读取号码"""
        return self._phone

     #类方法，将dict转换为单个联系人，返回Contatc实例
    @classmethod
    def from_dict(cls, data): 
        name = data["name"]
        phone = data["phone"]
        return cls(name, phone)
    
    #实例方法，将单个联系人实例转换为dict，返回dict
    def to_dict(self):
        return{
            "name": self.name,
            "phone": self.phone
            }