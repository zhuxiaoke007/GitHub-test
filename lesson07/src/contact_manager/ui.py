def show_menu():
    """
    显示主菜单选项
    功能：在控制台打印出所有可用的操作选项，供用户选择
    参数：无
    返回值：无（只负责打印信息）
    """
    print("1 添加联系人")
    print("2 查看联系人")
    print("3 删除联系人")
    print("4 修改联系人")
    print("0 退出")

def show_contacts(contacts):
    """
    显示当前通讯录中的所有联系人
    功能：遍历联系人列表，打印每个联系人的姓名和电话
    参数：
        contacts: list[Contact]，联系人列表（来自 service.list_all_contacts()，是独立的新列表）
    返回值：无（只负责打印信息）
    
    特殊情况处理：
        如果通讯录为空（没有任何联系人），打印提示信息后提前返回
    """
    # 检查列表是否为空
    # main.py 传入的是 list[Contact]（service.list_all_contacts() 返回的新列表），不是 ContactBook 本身
    if len(contacts) == 0:                    # 检查特殊情况
        print("通讯录为空")
        return                                # ← 提前返回，不执行后续代码（return 用于提前结束函数执行）

    print("当前联系人：")
    # 遍历列表中的每一个联系人
    # enumerate(contacts, start=1) 同时给出序号和元素，序号从 1 开始
    for number, contact in enumerate(contacts, start=1):
        # contact 是 Contact 类的实例对象
        # 通过 .name 和 .phone 属性获取联系人的姓名和电话
        print(f"{number}. {contact.name} - {contact.phone}")     # ← 每次迭代执行
    print("----------------")                                              # ← 函数执行到这里自动结束，不需要 return

def get_command():
    """
    显示主菜单选项
    获取用户输入的选择

    功能：等待用户从键盘输入内容，并返回输入的结果
    参数：无
    返回值：用户输入的字符串（例如："1"、"2"、"3"、"0"）
    注意：这里不验证输入是否合法，只负责接收，验证在 run() 函数中进行

    Returns:
        用户输入的原始字符串，如 "1"、"2"、"3"、"0"
    """
    show_menu()
    choice = input()                    # input() 会等待用户按回车，返回用户输入的内容（字符串类型）
    return choice                       # 将用户输入的内容返回给调用者



   