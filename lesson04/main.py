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
    if len(normal) == 0:         # 检查特殊情况；len() 调用对象的 __len__() 方法，对于自定义类，需要先实现 __len__() 才支持 len()
        print("通讯录为空")
        return                   # ← 提前返回，不执行后续代码（return 用于提前结束函数执行）
    print("当前联系人：")
    for contact in normal:                    # ← 遍历每个联系人
        print(contact.name, contact.phone)    # ← 每次迭代执行
    print("----------------")                 # ← 函数执行到这里自动结束，不需要 return

# 主业务循环
while True:
    show_menu()

    choice = get_choice()                     # input 返回字符串

    if choice == "0":                         # 字符串比较，不需要转数字，因为不涉及数学运算
        break                                 # 立即退出循环

    elif choice == "1":
        name = input("姓名：")
        phone = input("电话：")

        try:
            # 尝试执行的代码（可能出错）
            person = contacts.Contact(name, phone)
            normal.add_contact(person)
        except ValueError as e:                  # as e	：将异常对象赋值给变量 e
            # 如果发生 ValueError，执行这里的代码
            print(f"添加失败：{e}")
            continue                        # 回到循环开始

        print("添加成功")

    elif choice == "2":                     # elif：执行然后跳过后续 elif，意图清晰
        show_contacts(normal)
    
    elif choice == "3":
        show_contacts(normal)
        number = input("请输入编号：")
    
        if not number.isdigit():
            print("请输入数字")
            continue
    
        number = int(number)                          # 作为索引使用，需要将字符串转换为整数（关键步骤）
    
        if number < 1 or number > len(normal):
            print("编号无效")
            continue

        normal.delete_contact(number - 1)
        print("删除成功")
   
# 退出处理
storage.save_contacts(normal.to_data())
print("退出程序")