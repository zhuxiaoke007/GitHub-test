# protocols.py
from typing import Protocol

class DirtyTracker(Protocol):
    """
    标记数据已被修改（需要持久化）
    应用层定义的 Port，用于解耦 ContactService 与具体的脏数据管理实现。
    """
    def mark_dirty(self) -> None: ...

class ContactIdGenerationError(Exception):
    """
    ID 生成失败。

    这是 Port 契约的一部分：任何 ContactIdGenerator 实现都可能抛出它。
    Application 只需理解"端口没能给我 ID"，无需知道具体实现为何失败。
    """
    pass

class ContactIdGenerator(Protocol):
    """生成联系人 ID 的能力。"""
    def generate(self) -> str:
        ...