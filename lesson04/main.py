import contacts
import storage

# 初始化
# 读取文件
data = storage.load_contacts()
# 创建通讯录对象
normal = contacts.ContactBook()
# 恢复对象状态
normal.from_data(data)

def show_menu():
    print("1 添加联系人")
    print("2 查看联系人")
    print("3 删除联系人")
    print("0 退出")

def get_choice():
    choice = input()
    return choice

def show_contacts(normal):
    if len(normal) == 0:
        print("通讯录为空")
        return
    print("当前联系人：")
    for contact in normal:
        print(contact.name, contact.phone)
    print("----------------")

# 主业务循环
while True:
    show_menu()

    choice = get_choice()

    if choice == "0":
        break

    elif choice == "1":
        name = input("姓名：")
        phone = input("电话：")

        try:
            person = contacts.Contact(name, phone)
            normal.add_contact(person)
        except ValueError as e:
            print(f"添加失败：{e}")
            continue

        print("添加成功")

    elif choice == "2":
        show_contacts(normal)
    
    elif choice == "3":
        show_contacts(normal)
        number = input("请输入编号：")
    
        if not number.isdigit():
            print("请输入数字")
            continue
    
        number = int(number)
    
        if number < 1 or number > len(normal):
            print("编号无效")
            continue

        normal.delete_contact(number - 1)
        print("删除成功")
   
# 退出处理
storage.save_contacts(normal.to_data())
print("退出程序")