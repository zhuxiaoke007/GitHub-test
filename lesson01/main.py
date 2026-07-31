contacts = []

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
    person = [name, phone]
    return person

def add_contact(contacts, person):
    contacts.append(person)

def show_contacts(contacts):
    if not contacts:
        print("通讯录为空")
        return
    for person in contacts:
        print("姓名：", person[0])
        print("电话：", person[1])
        print("----------------")

def delete_contact(contacts):
    if not contacts:
        print("通讯录为空")
        return
    show_contacts(contacts)
    number = input("请输入编号：") 
    number = int(number)
    if 1 <= number <= len(contacts):
        contacts.pop(number - 1)
        print("删除成功")
    else:
        print("编号不存在")


while True:
    show_menu()

    choice = get_choice()

    if choice == "0":
        break
    elif choice == "1":
        person = input_contact()
        add_contact(contacts, person)
    elif choice == "2":
        show_contacts(contacts)
    elif choice == "3":
        delete_contact(contacts)

print("退出程序")