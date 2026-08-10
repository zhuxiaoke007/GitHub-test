class ContactBook:
    #创建ContactBook类
    def __init__(self):
        self.contacts = []

    #增加联系人
    def add_contact(self, person):              
        self.contacts.append(person)

    #删除除联系人
    def delete_contact(self, number):           
        if not self.contacts:
            print("通讯录为空")
            return
        if 1 <= number <= len(self.contacts):
            self.contacts.pop(number - 1)
            print("删除成功")
        else:
            print("编号不存在")

    #显示联系人
    def show_contacts(self):                     
        if not self.contacts:
            print("通讯录为空")
            return False
        for person in self.contacts:
            print("姓名：", person.name)
            print("电话：", person.phone)
            print("----------------")

    #将所有联系人转成dict
    def to_data(self):                         
        result = []                        # ✅ 1. 先初始化空列表
        for item in self.contacts:
            result.append(item.to_dict())  # ✅ 2. 调用每个联系人的 to_dict()
        return result                  # ✅ 3. 返回结果
    
    #将dict加载到联系人列表中
    def from_data(self, data):               
        self.contacts.clear()
        for item in data:
            person = Contact.from_dict(item)
            self.contacts.append(person)
        print("已加载联系人")

class Contact:
    #创建Contact类
    def __init__(self, name, phone):       
        self.name = name
        self.phone = phone

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
       