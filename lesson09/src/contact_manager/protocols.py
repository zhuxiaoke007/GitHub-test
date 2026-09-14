# protocols.py
# 这个模块定义「端口」（Port）——应用核心对外部世界的能力要求。
# Protocol 是「结构化类型」：一个类只要方法签名匹配，就自动满足协议，

from typing import Protocol

class DirtyTracker(Protocol):
    """
    标记数据已被修改（需要持久化）
    应用层定义的 Port，用于解耦 ContactService 与具体的脏数据管理实现。
    """
    # 这个协议抽象的是「脏标记」能力：
    #   ContactService 在修改数据后，只要调一下 mark_dirty()，
    #   不需要知道具体是「立刻存盘」「等会儿批量存」还是「记在内存里」。
    #
    # 为什么放在 protocols 里？
    #   因为 ContactService 属于应用层，它不应该直接依赖某个具体的
    #   持久化实现（JsonStorage、SqliteStorage 等）。
    #   它依赖的是「有一个东西能帮我标记脏数据」这个抽象。
    #
    # 谁来提供具体实现？
    #   组装层（composition root）决定注入哪个实现。
    #   ContactService 只看到协议，看不到实现。

    def mark_dirty(self) -> None: ...
    # 唯一方法：通知「数据已经被改动，需要持久化」。
    #
    # 没有返回值，因为调用方不关心「你怎么标记的」，
    # 它只关心「这个通知已经发出」。
    #
    # 末尾的 `...` 是 Protocol 方法的占位符，表示「只有签名，没有实现」。
    # 实际实现由满足该协议的类提供。

class ContactIdGenerationError(Exception):
    """
    ID 生成失败。

    这是 Port 契约的一部分：任何 ContactIdGenerator 实现都可能抛出它。
    Application 只需理解"端口没能给我 ID"，无需知道具体实现为何失败。
    """
    # 注意：异常也是「契约的一部分」。
    #
    # 为什么异常要和协议放在一起？
    #   因为「可能失败」是这个抽象本身的属性，不是某个实现的细节。
    #   如果异常定义在某个具体实现里（比如 UuidContactIdGenerator 里），
    #   那么：
    #     - 另一个实现（比如 SeqContactIdGenerator）就得依赖那个实现文件才能抛同样的异常，耦合错乱。
    #     - 调用方（Migration）要捕获异常时，得去 import 具体实现，违反分层。
    #   把异常放在协议旁边，等于声明：
    #     「任何 ContactIdGenerator 实现失败时都抛这个」，
    #     调用方只需 import protocols，不依赖任何具体实现。

    pass
    # 异常类不需要额外方法，pass 即可。

class ContactIdGenerator(Protocol):
    """生成联系人 ID 的能力。"""
    # 这个协议抽象的是「生成一个联系人 ID」的能力。
    #
    # 谁使用它？
    #   Migration 通过构造函数接收一个 ContactIdGenerator，
    #   需要补 ID 时调 generate()，不知道具体是 UUID 还是别的策略。
    #
    # 谁实现它？
    #   UuidContactIdGenerator（生产）、SeqContactIdGenerator（测试）等。
    #   它们只需方法签名匹配，就自动满足这个协议。

    def generate(self) -> str:
        # 唯一方法：生成并返回一个联系人 ID（字符串）。
        #
        # 返回 str 而不是 uuid.UUID：
        #   下游要把 ID 写进 JSON / SQLite，字符串最通用。
        #   而且协议层不该绑死某个具体的 ID 类型。
        #
        # 失败时应该抛 ContactIdGenerationError（见上）。
        # 这是契约的一部分，虽然签名里看不到，但文档和异常定义都指明了。
        ...