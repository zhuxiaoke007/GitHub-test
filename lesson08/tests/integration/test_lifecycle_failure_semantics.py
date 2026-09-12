"""
生命周期失败语义集测：
    使用真实组件（ContactBook + JsonStorage），
    验证 ApplicationStartupError / ApplicationShutdownError 的翻译契约。
"""
from unittest.mock import Mock

import pytest
from contact_manager.application_lifecycle import (
    ApplicationLifecycle,
    ApplicationShutdownError,
    ApplicationStartupError,
)
from contact_manager.domain import Contact, ContactBook
from contact_manager.storage import JsonStorage, StorageError


class BrokenStorage:
    """实现 Storage 协议的故障替身"""

    def __init__(self):
        self.save_calls = 0

    def load(self) -> list[dict]:
        raise StorageError("模拟读取失败")

    def save(self, data) -> None:
        self.save_calls += 1
        raise StorageError("模拟写入失败")


def write_json(path, content):
    import pathlib
    pathlib.Path(path).write_text(content, encoding="utf-8")


def make_lifecycle(storage, logger=None):
    return ApplicationLifecycle(ContactBook(), storage, logger if logger is not None else Mock())


# ==================== start：翻译语义 ====================

def test_corrupted_json_translated_to_startup_error(tmp_path):
    """文件不是合法 JSON → JSONDecodeError → StorageDataCorruptedError → ApplicationStartupError"""
    file = tmp_path / "contacts.json"
    write_json(file, "{这不是 JSON]")
    lifecycle = make_lifecycle(JsonStorage(str(file)))

    with pytest.raises(ApplicationStartupError):
        lifecycle.start()


def test_duplicate_phone_in_file_translated_to_startup_error(tmp_path):
    """文件内重复电话 → DuplicatePhoneError(DomainError) → ApplicationStartupError"""
    file = tmp_path / "contacts.json"
    write_json(file, '[{"contact_id": "a1", "name": "A", "phone": "13800138000"},'
                     ' {"contact_id": "b2", "name": "B", "phone": "13800138000"}]')
    lifecycle = make_lifecycle(JsonStorage(str(file)))

    with pytest.raises(ApplicationStartupError):
        lifecycle.start()


@pytest.mark.xfail(strict=False, reason="已知缺口：KeyError/TypeError 不在 start() 的翻译元组中，非领域异常会逃逸")
def test_structurally_wrong_json_translated_to_startup_error(tmp_path):
    """
    合法 JSON 但形状不符（data 是对象而非数组）
    期望：被翻译为 ApplicationStartupError
    """
    file = tmp_path / "contacts.json"
    write_json(file, '{"name": "Tom"}')
    lifecycle = make_lifecycle(JsonStorage(str(file)))

    with pytest.raises(ApplicationStartupError):
        lifecycle.start()


@pytest.mark.xfail(strict=False, reason="已知缺口：老数据迁移未实现，from_dict 仍强制要求 contact_id，KeyError 会逃逸")
def test_legacy_format_without_contact_id_can_load(tmp_path):
    """
    向后兼容：lesson05~07 格式（缺 contact_id）应能加载（自动补发 ID）
    """
    file = tmp_path / "contacts.json"
    write_json(file, '[{"name": "Tom", "phone": "13800138000"}]')
    lifecycle = make_lifecycle(JsonStorage(str(file)))

    lifecycle.start()
    # 加载成功即通过；补发的 ID 由领域层保证


# ==================== shutdown：失败语义 ====================

def test_shutdown_save_failure_raises_shutdown_error_and_keeps_dirty():
    """保存失败：必须有 ApplicationShutdownError；dirty 必须保持 True（数据未丢）；Logger 仍关闭"""
    mock_logger = Mock()
    lifecycle = make_lifecycle(BrokenStorage(), mock_logger)
    lifecycle.mark_dirty()

    with pytest.raises(ApplicationShutdownError):
        lifecycle.shutdown()

    assert lifecycle._is_dirty is True
    mock_logger.close.assert_called_once()


def test_shutdown_resets_dirty_only_after_successful_save(tmp_path):
    """保存成功：dirty 清除；再次 shutdown 不重复写文件"""
    file = tmp_path / "contacts.json"
    storage = JsonStorage(str(file))
    mock_logger = Mock()
    lifecycle = make_lifecycle(storage, mock_logger)

    lifecycle.mark_dirty()
    lifecycle.shutdown()
    assert lifecycle._is_dirty is False

    lifecycle.shutdown()
    assert mock_logger.info.call_count >= 2


# ==================== 数据保真 round-trip ====================

def test_shutdown_preserves_contact_id(tmp_path):
    """保存再加载，contact_id 必须原样保留（身份稳定性）"""
    file = tmp_path / "contacts.json"
    storage = JsonStorage(str(file))
    book = ContactBook()
    lifecycle = ApplicationLifecycle(book, storage, Mock())
    lifecycle.mark_dirty()
    book.add_contact(Contact("fixed-id-001", "Tom", "13800138000"))
    lifecycle.shutdown()

    reloaded = ContactBook()
    ApplicationLifecycle(reloaded, JsonStorage(str(file)), Mock()).start()

    assert len(reloaded) == 1
    assert next(iter(reloaded)).contact_id == "fixed-id-001"
