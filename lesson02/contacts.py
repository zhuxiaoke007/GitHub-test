contacts = []

def set_contacts(data):
    """设置联系人数据"""
    contacts.clear()
    contacts.extend(data)
    print("已加载联系人")

def add_contact(person):
    contacts.append(person)

def show_contacts():
    if not contacts:
        print("通讯录为空")
        return False
    for person in contacts:
        print("姓名：", person["name"])
        print("电话：", person["phone"])
        print("----------------")

def delete_contact(number):
    if not contacts:
        print("通讯录为空")
        return
    if 1 <= number <= len(contacts):
        contacts.pop(number - 1)
        print("删除成功")
    else:
        print("编号不存在")

def get_all_contacts():
    return contacts