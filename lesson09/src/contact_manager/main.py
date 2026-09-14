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
# 这是整个程序的「组装层」（composition root），也是唯一允许「同时知道所有具体实现」的地方。
# 前面几轮反复说「具体实现由组装层注入」——main.py 就是那个组装层。
# 前面的 protocols.py 定义了"端口"（DirtyTracker、ContactIdGenerator），main() 就是决定"每个端口用哪个具体实现"的地方。
# 其它组件（ContactService、Migration、JsonStorage）都只依赖协议/抽象，唯独这里必须认识每一个具体类，因为它的职责就是「把拼图拼起来」。

# 什么叫"组装层"（composition root）
# 组装层是整个程序里唯一一个允许同时认识所有具体类的地方。它的职责是：
# 创建具体实现（UuidContactIdGenerator、JsonStorage、ApplicationLifecycle、ContactService、ConsoleUI）。
# 按照每个组件声明的依赖，把它们注入进去。
# 不实现任何业务逻辑，只负责"接线"。

# ========== 导入依赖 ==========
from contact_manager.ui import ConsoleUI
# UI 层：负责和用户交互（读命令、显示结果）。
# 它只依赖 ContactService，不知道 Domain / Infrastructure 的存在。

from contact_manager.application_lifecycle import (
    ApplicationLifecycle,        # 生命周期控制器
    ApplicationStartupError,     # 启动失败异常
    ApplicationShutdownError     # 关闭（保存）失败异常
)
# 应用层：生命周期。负责 start（加载）和 shutdown（保存）。
# 它实现了 DirtyTracker 协议——这就是为什么它既能当生命周期控制器，
# 又能被 ContactService 当作「脏标记接收者」。

from contact_manager.contact_service import ContactService
# 应用层：业务用例入口。

from contact_manager.logger import Logger
# 日志组件。作为依赖传给 lifecycle。

from contact_manager.domain import ContactBook
# 领域层：联系人集合（聚合根）。

from contact_manager.storage import (
    JsonStorage,
)
# 基础设施层：JSON 文件存储的具体实现。
# 注意：main.py 直接 import 具体类，因为组装层要「选实现」。
# ContactService / Migration 都不会这样 import。

from contact_manager.id_generator import UuidContactIdGenerator
# 基础设施层：UUID 生成器的具体实现。

from contact_manager.migration import Migration
# 基础设施层：版本迁移器。


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
    id_generator = UuidContactIdGenerator()
    # 具体实现：UUID 生成器。
    # 这个对象同时会被注入给 Migration 和 ContactService，
    # 保证两处用的是同一个策略（当前都是 UUID）。

    migration = Migration(id_generator)
    # Migration 依赖一个 ContactIdGenerator。
    # 这里把具体实现 UuidContactIdGenerator 注入进去。
    # Migration 内部只知道 self._id_generator.generate()，
    # 不知道它是 UUID 还是别的。

    storage = JsonStorage("contacts.json", migration)   # type: ignore
    # 具体实现：JSON 文件存储。
    # 它需要两样东西：
    #   - 文件路径 "contacts.json"
    #   - 一个 Migration（load 时如果发现旧版本，用它来迁移）
    #
    # type: ignore 通常是因为 JsonStorage 的构造签名和这里传参
    # 在类型检查器看来略有出入（比如 Optional、Protocol 不匹配等），
    # 属于工程上的小妥协，不影响运行时。

    book = ContactBook()
    # 领域层：唯一的 ContactBook 实例。
    # 它是「共享状态」——lifecycle 和 service 都指向同一个 book，
    # 这样 UI 通过 service 改数据时，lifecycle 保存的是同一个 book。

    logger = Logger()
    # 日志。

    lifecycle = ApplicationLifecycle(book, storage, logger)
    # 生命周期控制器。
    # 它拿到：
    #   - book（要加载/保存哪个集合）
    #   - storage（怎么读/写）
    #   - logger（记日志）
    #
    # 它实现 DirtyTracker 协议，所以下面能当 tracker 传给 ContactService。

    service = ContactService(book, lifecycle, id_generator)
    # 业务服务。
    # 它拿到：
    #   - book        （领域操作对象）
    #   - lifecycle   （当作 DirtyTracker 用）
    #   - id_generator（生成 ID 的端口）
    #
    # 注意：这里把 lifecycle 传给了 service，
    # 但 ContactService 的构造函数签名要求 DirtyTracker（Protocol）。
    # 传进去的是 ApplicationLifecycle，它能被接受，
    # 是因为它「满足 DirtyTracker 协议」（有 mark_dirty()）。
    # 这正是 Protocol 结构化类型带来的好处：
    # 不需要让 ApplicationLifecycle 显式继承 DirtyTracker。

    ui = ConsoleUI(service)
    # UI 只拿到 service。
    # 它不知道 book、storage、migration、id_generator 的存在。
    

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
        # 启动失败就直接返回，不进入主循环。
        # 因为 book 没有加载成功，UI 再跑也没意义。

    # ========== 第 3 步：进入主循环（处理用户命令） ==========
    ui.run()
    # UI 阻塞在这里，直到用户选择退出。
    # 期间用户的所有操作都通过 service 完成，
    # service 在成功修改后调 lifecycle.mark_dirty()。
    
        # ========== 第 4 步：退出应用程序（保存数据） ==========
    try:
        lifecycle.shutdown()
        print("已退出")
    except ApplicationShutdownError as e:
        print(f"保存失败，数据可能丢失：{e}")
        # 程序依然退出，但不打印"已退出",
        # 因为保存失败意味着退出过程不完美

if __name__ == "__main__":
    main()