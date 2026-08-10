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

# 主业务循环
while True:
    show_menu()

    choice = get_choice()

    if choice == "0":
        break
    elif choice == "1":
        name = input("姓名：")
        phone = input("电话：")
        person = contacts.Contact(name, phone)
        normal.add_contact(person)
    elif choice == "2":
        normal.show_contacts()
    elif choice == "3":
        normal.show_contacts()
        number = input("请输入编号：") 
        try:
            number = int(number)
        except ValueError:
            print("请输入数字")
            continue
        normal.delete_contact(number)
# 退出处理
storage.save_contacts(normal.to_data())
print("退出程序")