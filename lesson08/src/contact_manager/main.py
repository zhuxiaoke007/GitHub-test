# main.py
"""
通讯录应用程序 - 主入口

职责：
    1. 组装所有组件（依赖注入）
    2. 控制应用程序生命周期
    3. 创建 Application / Domain / Infrastructure 组件
    4. 启动 UI
    5. 处理应用程序级别的启动、关闭异常
"""
# ========== 导入依赖 ==========
from contact_manager.ui import ConsoleUI
from contact_manager.application_lifecycle import ApplicationLifecycle, ApplicationStartupError, ApplicationShutdownError  # 应用层：生命周期
from contact_manager.contact_service import ContactService  # 应用层：业务用例
from contact_manager.logger import Logger
from contact_manager.domain import ContactBook
from contact_manager.storage import (  # 基础设施层：文件存储
    JsonStorage,  # 导入JSON文件存储类
)
from contact_manager.id_generator import UuidContactIdGenerator


# main.py
def main():
    """
    应用程序主函数

    执行流程：
        第 1 步：组装所有组件（依赖注入）
        第 2 步：启动应用程序（加载数据）
        第 3 步：进入主循环（获取用户命令 → 执行）
        第 4 步：退出应用程序（保存数据）
    """
    # ==================== 第1步：组装所有组件（依赖注入） ====================
    storage = JsonStorage("contacts.json")      # 创建基础设施层组件（文件存储），负责从文件读取数据和将数据写入文件, 它需要知道文件路径（contacts.json）
    book = ContactBook()                        # 创建领域层组件（领域层数据容器）：作为所有组件共享的唯一实例
    logger = Logger()
    
    # ApplicationLifecycle 实现了 DirtyTracker Protocol
    lifecycle = ApplicationLifecycle(book, storage, logger)   # 创建应用层组件 - 生命周期控制器, 负责控制程序的启动、运行和退出,它需要依赖 ContactBook（获取数据）和 Storage（读写文件）

    id_generator = UuidContactIdGenerator()

    # lifecycle 作为 DirtyTracker 传入
    service = ContactService(book, lifecycle, id_generator)     # 创建应用层组件 - 业务服务, 负责负责处理用户的业务请求,它需要依赖 ContactBook 来操作数据
    
    ui = ConsoleUI(service)
    

    # ========== 第2步：启动应用程序（加载数据） ==========
    # 调用 start() 方法：
    #     - Storage.load() 从文件读取数据
    #     - ContactBook.from_data() 将数据加载到内存
    #     如果文件不存在或数据格式错误，应该抛出异常
    try:
        lifecycle.start()
        print("通讯录已加载")
    except ApplicationStartupError as e:
        print(f"启动失败：{e}")
        return

    # ========== 第 3 步：进入主循环（处理用户命令） ==========
    
    ui.run()
    
    # ========== 第 4 步：退出应用程序（保存数据） ==========
    try:
        lifecycle.shutdown()
        print("已退出")
    except ApplicationShutdownError as e:
        print(f"保存失败，数据可能丢失：{e}")      # 程序依然退出，但不打印"已退出", 因为保存失败意味着退出过程不完美

if __name__ == "__main__":
    main()