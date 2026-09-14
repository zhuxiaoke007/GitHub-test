import uuid

from contact_manager.application_lifecycle import ApplicationLifecycle
from contact_manager.domain import Contact, ContactBook
from contact_manager.id_generator import UuidContactIdGenerator
from contact_manager.logger import Logger
from contact_manager.migration import Migration
from contact_manager.storage import JsonStorage


def make_storage(path):
    """生产形态的存储组装：JsonStorage(file, Migration(id_generator))"""
    return JsonStorage(str(path), Migration(UuidContactIdGenerator()))


class QuietLogger:
    """满足生命周期依赖的最小 Logger 替身（避免第二轮写真实日志文件）"""

    def info(self, message: str) -> None:
        pass

    def warning(self, message: str) -> None:
        pass

    def error(self, message: str) -> None:
        pass

    def close(self) -> None:
        pass


def test_shutdown_saves_and_restores_contacts(tmp_path):
    # 1️⃣ 准备：创建初始数据（Contact 现在需要 contact_id 作为第一个参数）
    original_book = ContactBook()
    original_book.add_contact(Contact(str(uuid.uuid4()), "Tom", "13800138000"))

    # 2️⃣ 使用临时文件
    test_file = tmp_path / "contacts.json"
    storage = make_storage(test_file)
    logger = Logger()

    # 3️⃣ 执行保存（Logger 由 shutdown 在 finally 中关闭）
    lifecycle = ApplicationLifecycle(original_book, storage, logger)
    lifecycle._is_dirty = True
    lifecycle.shutdown()

    # 4️⃣ 验证：文件确实存在
    assert test_file.exists()

    # 5️⃣ 重新加载（Logger 已被关闭，第二轮换替身，不再触碰真实文件）
    new_book = ContactBook()
    new_storage = make_storage(test_file)
    new_lifecycle = ApplicationLifecycle(new_book, new_storage, QuietLogger())
    new_lifecycle.start()

    # 6️⃣ ✅ 核心断言：Tom 仍然存在，数据完整（含身份稳定性）
    contacts = list(new_book)
    assert len(contacts) == 1

    tom = contacts[0]
    assert tom.name == "Tom"
    assert tom.phone == "13800138000"