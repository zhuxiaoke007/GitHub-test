#ui.py

from contact_manager.contact_service import (
    ContactService,
    ContactNotFoundError,
    ContactInputError,
    ContactDuplicateError,
    ContactServiceInternalError,
)

def show_menu():
    """
    显示主菜单选项
    功能：在控制台打印出所有可用的操作选项，供用户选择
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
    返回值：用户输入的字符串（例如："1"、"2"、"3"、"0"）
    注意：这里不验证输入是否合法，只负责接收，验证在 run() 函数中进行

    Returns:
        用户输入的原始字符串，如 "1"、"2"、"3"、"0"
    """
    show_menu()
    choice = input()                    # input() 会等待用户按回车，返回用户输入的内容（字符串类型）
    return choice                       # 将用户输入的内容返回给调用者

class ConsoleUI:
    def __init__(self, service: ContactService):
        self._service = service

    def run(self):
        while True:
        # ----- 调用UI显示菜单和获取用户命令-----）
            command = get_command()           # 等待用户输入，返回的是字符串（如 "1", "2", "3", "0"）

            if not command:
                continue
        
            # ----- 根据用户选择执行对应操作 -----
            # ---------- 选项0：退出程序 ----------
            if command == "0":                           # 字符串比较，不需要转数字，因为不涉及数学运算
                print("正在退出...")
                break                                    # break 会立即跳出 while 循环，结束程序

            # ---------- 选项1：添加联系人 ----------
            elif command == "1":
                # 提示用户输入联系人的姓名和电话
                name = input("姓名：")
                phone = input("电话：")

                try:
                    # 尝试执行添加操作（可能因为数据不合法而抛出异常）
                    # add_contact() 方法会验证姓名是否为空、电话格式是否正确等
                    self._service.add_contact(name, phone)
                    print("添加成功")
                except ContactInputError as e:
                    print(f"输入错误：{e}")
                except ContactDuplicateError as e:
                    print(f"添加失败：{e}")
                except ContactServiceInternalError as e:
                    print(f"系统错误：{e}")
            
            # ---------- 选项2：查看联系人 ----------
            elif command == "2":                          # 这里使用 elif 而不是 if，因为选择了"2"就不会再检查后续条件
                contacts = self._service.list_all_contacts()
                show_contacts(contacts)    

            # ---------- 选项3：删除联系人 ----------
            elif command == "3":
                # 第1步：先显示所有联系人，让用户知道有哪些联系人可以删除
                # 这里拿到的是 list_all_contacts() 返回的【快照】（新列表）。
                # 列表容器是新的，但里面的 Contact 对象仍是 ContactBook 内对象的引用。
                # 之所以要保留这份快照：用户看到的编号，就是基于这份快照的显示顺序。
                contacts = self._service.list_all_contacts()
                show_contacts(contacts)

                # 第2步：提示用户输入要删除的联系人编号
                number = input("请输入编号：")

                # 第3步：验证输入形态
                # isdigit() 只检查字符串是否【全为数字字符】（如 "1"、"23"）。
                # 注意：它不处理负数、空格、符号，也不代表编号一定在有效范围内——
                if not number.isdigit():
                    print("请输入数字")
                    continue                                   # 回到循环开始，重新显示菜单，不执行后续的删除操作

                # 第4步：把字符串编号转成整数（因为列表索引必须是整数）
                # 用户看到的是从1开始的编号（第1个、第2个...）
                # 但列表的索引是从0开始的（第0个、第1个...）
                position = int(number)

                # 第5步：检查编号是否在有效范围内
                # 编号必须 >= 1 且 <= 通讯录的总人数
                if position < 1 or position > len(contacts):
                    print("编号无效")
                    continue

                # 第6步：根据用户输入的显示编号，找到对应的联系人（1-based 编号 → 0-based 索引）。
                # 这是表现层翻译（presentation-layer translation）：
                # 编号是 UI 自己产生的显示概念，只有 UI 知道它对应快照里的哪个元素。
                # 翻译后我们只取 contact_id（业务标识）交给 Service，
                # 绝不把 position 这个 UI 概念传给 Service
                contact = contacts[position - 1]
                
                # 第7步：执行删除
                # 只传 contact_id，Service 完全不知道“编号”的存在。删除是基于【身份】而非【位置】
                try:
                    deleted = self._service.delete_contact(contact.contact_id)
                    print(f"删除成功：{deleted.name}")

                # 异常处理分层：
                # UI 只处理 Application 层向上暴露的【语义异常】，
                # 不直接处理 Domain 异常（如 ContactIdNotFoundError）
                # 或 Infrastructure 异常（如 ContactIdGenerationError）。
                # 那些底层异常已由 Service 翻译成 Application 语义（ContactNotFoundError）
                except ContactNotFoundError as e:
                    print(f"删除失败：{e}")
                except ContactServiceInternalError as e:
                    print(f"系统错误：{e}")
            
            # ---------- 选项4：修改联系人 ----------
            elif command == "4":
                contacts = self._service.list_all_contacts()
                show_contacts(contacts)

                number = input("请输入编号：")

                if not number.isdigit():
                    print("请输入数字")
                    continue 

                position = int(number)

                if position < 1 or position > len(contacts):
                    print("编号无效")
                    continue

                contact = contacts[position - 1]
                
                # 获取 new_phone
                new_phone = input("请输入新电话号码：")
                
                # 调用 service.change_phone(position, new_phone)
                try:
                    # Service 内部处理（Domain 验证、Contact 修改）
                    self._service.change_phone(contact.contact_id, new_phone)
                    
                    # UI 提示修改成功
                    print("修改成功")
                    
                    # 重新显示联系人列表
                    updated_contacts = self._service.list_all_contacts()
                    show_contacts(updated_contacts)
                    
                # 捕获 UI 需要处理的异常（Service 抛出的业务异常）
                except ContactNotFoundError as e:
                    print(f"修改失败：{e}")
                except ContactInputError as e:
                    print(f"输入错误：{e}")
                except ContactDuplicateError as e:
                    print(f"修改失败：{e}")
                except ContactServiceInternalError as e:
                    print(f"系统错误：{e}")

                    # ---------- 无效选项 ----------
            else:
                print("无效选项，请重新选择")