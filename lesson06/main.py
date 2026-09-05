"""
通讯录应用程序 - 主入口

本文件负责：
    1. 组装所有组件（依赖注入）
    2. 控制应用程序的生命周期（启动 → 运行 → 退出）
    3. 拥有主循环，作为外层协调者
    4. 调用 Service 执行业务操作，成功后调用 Lifecycle.mark_dirty()

依赖关系：
    main.py
        ├── ContactBook（领域层 - 数据容器）← 仅作为组装依赖（传递给 Service 和 Lifecycle）
        ├── Storage（基础设施层 - 文件读写）← 仅作为组装依赖（传递给 Lifecycle）
        ├── ContactService（应用层 - 业务用例）← 主要依赖
        ├── ApplicationLifecycle（应用层 - 生命周期控制）← 主要依赖
        └── ui（表现层 - 命令行界面函数）← 依赖

数据流向：
    用户输入 → Service → ContactBook（修改内存）
                         ↓
                    Lifecycle.mark_dirty()（标记脏）
                         ↓
                    退出时 Lifecycle.shutdown()（保存到文件）
"""
# ========== 导入依赖 ==========
import ui
from application_lifecycle import ApplicationLifecycle  # 应用层：生命周期
from contact_service import ContactNotFoundError, ContactService  # 应用层：业务用例
from domain import (  # 领域层：业务异常
    ContactBook,  # 领域层：联系人容器
    ContactValidationError,
    DuplicateContactError,
)
from storage import (  # 基础设施层：文件存储
    JsonStorage,  # 导入JSON文件存储类
    StorageDataCorruptedError,  # 导入"存储数据损坏"异常类
    StorageError,  # 导入"存储操作失败"通用异常类
)


# main.py
def main():
    """
    应用程序主函数

    执行流程：
        第 1 步：组装所有组件（依赖注入）
        第 2 步：启动应用程序（加载数据）
        第 3 步：进入主循环（获取用户命令 → 执行 → 标记脏）
        第 4 步：退出应用程序（保存数据）
    """
    # ==================== 第1步：组装所有组件（依赖注入） ====================
    book = ContactBook()                        # 创建领域层组件（领域层数据容器）：作为所有组件共享的唯一实例
    storage = JsonStorage("contacts.json")      # 创建基础设施层组件（文件存储），负责从文件读取数据和将数据写入文件, 它需要知道文件路径（contacts.json）
    service = ContactService(book)              # 创建应用层组件 - 业务服务, 负责负责处理用户的业务请求,它需要依赖 ContactBook 来操作数据
    lifecycle = ApplicationLifecycle(book, storage)   # 创建应用层组件 - 生命周期控制器, 负责控制程序的启动、运行和退出,它需要依赖 ContactBook（获取数据）和 Storage（读写文件）

    # ========== 第2步：启动应用程序（加载数据） ==========
    # 调用 start() 方法：
    #     - Storage.load() 从文件读取数据
    #     - ContactBook.from_data() 将数据加载到内存
    #     如果文件不存在或数据格式错误，应该抛出异常
    try:
        lifecycle.start()
        print("通讯录已加载")
    except StorageDataCorruptedError as e:    # 如果文件存在但内容损坏（如JSON格式错误），会触发这个异常
        print(f"数据损坏：{e}")
        return                         # 直接退出程序，因为数据无法恢复
    except StorageError as e:
        print(f"存储操作失败：{e}")
        return

    # ========== 第 3 步：进入主循环（处理用户命令） ==========
    while True:
        # ----- 调用UI显示菜单和获取用户命令-----）
        command = ui.get_command()           # 等待用户输入，返回的是字符串（如 "1", "2", "3", "0"）

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
                service.add_contact(name, phone)
                lifecycle.mark_dirty()          # main 标记脏
                print("添加成功")
            except ContactValidationError as e:
                print(f"输入错误：{e}")
            except DuplicateContactError as e:
                print(f"添加失败：{e}")
           
        # ---------- 选项2：查看联系人 ----------
        elif command == "2":                          # 这里使用 elif 而不是 if，因为选择了"2"就不会再检查后续条件
            contacts = service.list_all_contacts()
            ui.show_contacts(contacts)    
            # 不调用 mark_dirty() —— 没有修改数据

        # ---------- 选项3：删除联系人 ----------
        elif command == "3":
            # 第1步：先显示所有联系人，让用户知道有哪些联系人可以删除
            contacts = service.list_all_contacts()
            ui.show_contacts(contacts)

            # 第2步：提示用户输入要删除的联系人编号
            number = input("请输入编号：")

            # 第3步：验证输入是否为数字
            # isdigit() 方法检查字符串是否只包含数字字符（如 "1", "23", "456"）
            if not number.isdigit():
                print("请输入数字")
                continue                                   # 回到循环开始，重新显示菜单，不执行后续的删除操作

            # 第4步：将字符串转换为整数（因为列表索引必须是整数）
            # 用户看到的是从1开始的编号（第1个、第2个...）
            # 但列表的索引是从0开始的（第0个、第1个...）
            position = int(number)                         # 作为索引使用，需要将字符串转换为整数（关键步骤）

            # 第5步：检查编号是否在有效范围内
            # 编号必须 >= 1 且 <= 通讯录的总人数
            if position < 1 or position > len(contacts):
                print("编号无效")
                continue
            # 第6步：执行删除操作
            try:
                deleted = service.delete_contact(position)
                lifecycle.mark_dirty()                           # main 标记脏
                print(f"删除成功：{deleted.name}")
            # main.py 不直接处理 Domain / Infrastructure 的底层实现异常；它处理 Application API 向上暴露的语义异常。
            except ContactNotFoundError as e:
                print(f"删除失败：{e}")
        
        # ---------- 选项4：修改联系人 ----------
        elif command == "4":
            # 第1步：显示所有联系人，让用户选择要修改的联系人
            contacts = service.list_all_contacts()
            ui.show_contacts(contacts)
            
            # 第2步：UI 获取 position
            number = input("请输入要修改的联系人编号：")
            
            # 第3步：UI 做基本输入检查
            if not number.isdigit():
                print("请输入数字")
                continue
            
            position = int(number)
            
            # 检查编号是否在有效范围内
            if position < 1 or position > len(contacts):
                print("编号无效")
                continue
            
            # 第4步：UI 获取 new_phone
            new_phone = input("请输入新电话号码：")
            
            # 第5步：调用 service.change_phone(position, new_phone)
            try:
                # 第6-8步：Service 内部处理（Domain 验证、Contact 修改）
                service.change_phone(position, new_phone)
                
                # 第9步：修改成功返回后
                # 第10步：main 调用 lifecycle.mark_dirty()
                lifecycle.mark_dirty()
                
                # 第11步：UI 提示修改成功
                print("修改成功")
                
                # 第12步：UI 重新显示联系人列表
                updated_contacts = service.list_all_contacts()
                ui.show_contacts(updated_contacts)
                
            # 捕获 UI 需要处理的异常（Service 抛出的业务异常）
            except ContactNotFoundError as e:
                print(f"修改失败：{e}")
            except ContactValidationError as e:
                print(f"输入错误：{e}")
            except DuplicateContactError as e:
                print(f"修改失败：{e}")

                # ---------- 无效选项 ----------
        else:
            print("无效选项，请重新选择")
    
    # ========== 第 4 步：退出应用程序（保存数据） ==========
    try:
        lifecycle.shutdown()
        print("已退出")
    except StorageError as e:
        print(f"保存失败，数据可能丢失：{e}")      # 程序依然退出，但不打印"已退出", 因为保存失败意味着退出过程不完美

if __name__ == "__main__":
    main()