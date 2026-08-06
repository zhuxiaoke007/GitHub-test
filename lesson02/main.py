import contacts
import storage

# 初始化
data = storage.load_contacts()
contacts.set_contacts(data)

def show_menu():
    print("1 添加联系人")
    print("2 查看联系人")
    print("3 删除联系人")
    print("0 退出")

def get_choice():
    choice = input()
    return choice

def input_contact():
    name = input("姓名：")
    phone = input("电话：")
    person = {
    "name": name,
    "phone": phone
    }
    return person

# 主业务循环
while True:
    show_menu()

    choice = get_choice()

    if choice == "0":
        break
    elif choice == "1":
        person = input_contact()
        contacts.add_contact(person)
    elif choice == "2":
        contacts.show_contacts()
    elif choice == "3":
        contacts.show_contacts()
        number = input("请输入编号：") 
        number = int(number)
        contacts.delete_contact(number)
# 退出处理
storage.save_contacts(contacts.get_all_contacts())
print("退出程序")