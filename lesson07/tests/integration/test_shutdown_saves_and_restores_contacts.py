import json
import pytest
from contact_manager.domain import Contact, ContactBook
from contact_manager.storage import JsonStorage
from contact_manager.application_lifecycle import ApplicationLifecycle
from contact_manager.logger import Logger


def test_shutdown_saves_and_restores_contacts(tmp_path):
    # 1️⃣ 准备：创建初始数据
    original_book = ContactBook()
    original_book.add_contact(Contact("Tom", "13800138000"))
    
    # 2️⃣ 使用临时文件
    test_file = tmp_path / "contacts.json"
    storage = JsonStorage(str(test_file))
    logger = Logger()
    
    # 3️⃣ 执行保存
    lifecycle = ApplicationLifecycle(original_book, storage, logger)
    lifecycle._is_dirty = True
    lifecycle.shutdown()
    
    # 4️⃣ 验证：文件确实存在
    assert test_file.exists()
    
    # 5️⃣ 重新加载
    new_book = ContactBook()
    new_storage = JsonStorage(str(test_file))
    new_lifecycle = ApplicationLifecycle(new_book, new_storage, logger)
    new_lifecycle.start()
    
    # 6️⃣ ✅ 核心断言：Tom 仍然存在，数据完整
    contacts = list(new_book)
    assert len(contacts) == 1
    
    tom = contacts[0]
    assert tom.name == "Tom"
    assert tom.phone == "13800138000"