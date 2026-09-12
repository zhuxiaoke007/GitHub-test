import pytest
from contact_manager.contact_service import (
    ContactDuplicateError,
    ContactInputError,
    ContactNotFoundError,
    ContactService,
)


class FakeDirtyTracker:
    """实现 DirtyTracker Protocol 的测试替身，记录 mark_dirty 调用次数"""

    def __init__(self):
        self.calls = 0

    def mark_dirty(self) -> None:
        self.calls += 1


def make_service():
    """构造真实协作组件：真 ContactBook + 测试替身 Tracker + 真 UUID 生成器"""
    from contact_manager.domain import ContactBook
    from contact_manager.id_generator import UuidContactIdGenerator
    return ContactService(ContactBook(), FakeDirtyTracker(), UuidContactIdGenerator())


def tracker_of(service):
    return service._tracker


# ==================== add_contact ====================

def test_add_contact_success_adds_and_marks_dirty():
    service = make_service()

    contact = service.add_contact("Alice", "13800138000")

    assert contact.name == "Alice"
    assert contact.phone == "13800138000"
    assert contact.contact_id != ""
    assert len(list(service.list_all_contacts())) == 1
    assert tracker_of(service).calls == 1


def test_add_contact_invalid_phone_raises_input_error_and_not_dirty():
    service = make_service()

    with pytest.raises(ContactInputError):
        service.add_contact("Alice", "12345")

    assert tracker_of(service).calls == 0


def test_add_contact_empty_name_raises_input_error():
    service = make_service()

    with pytest.raises(ContactInputError):
        service.add_contact("", "13800138000")

    assert tracker_of(service).calls == 0


def test_add_contact_duplicate_phone_raises_duplicate_error():
    service = make_service()
    service.add_contact("Alice", "13800138000")
    calls_before = tracker_of(service).calls

    with pytest.raises(ContactDuplicateError):
        service.add_contact("Bob", "13800138000")

    assert tracker_of(service).calls == calls_before


# ==================== delete_contact ====================

def test_delete_contact_success_removes_and_marks_dirty():
    service = make_service()
    contact = service.add_contact("Alice", "13800138000")

    deleted = service.delete_contact(contact.contact_id)

    assert deleted.contact_id == contact.contact_id
    assert len(list(service.list_all_contacts())) == 0
    assert tracker_of(service).calls == 2


def test_delete_contact_unknown_id_raises_not_found():
    service = make_service()
    service.add_contact("Alice", "13800138000")
    calls_before = tracker_of(service).calls

    with pytest.raises(ContactNotFoundError):
        service.delete_contact("no-such-id")

    assert tracker_of(service).calls == calls_before


def test_delete_twice_second_raises_not_found():
    service = make_service()
    contact = service.add_contact("Alice", "13800138000")
    service.delete_contact(contact.contact_id)
    calls_before = tracker_of(service).calls

    with pytest.raises(ContactNotFoundError):
        service.delete_contact(contact.contact_id)

    assert tracker_of(service).calls == calls_before


# ==================== get_contact / list ====================

def test_get_contact_existing_returns_contact():
    service = make_service()
    created = service.add_contact("Alice", "13800138000")

    found = service.get_contact(created.contact_id)

    assert found is created


def test_get_contact_unknown_id_raises_not_found():
    service = make_service()

    with pytest.raises(ContactNotFoundError):
        service.get_contact("missing-id")


def test_list_all_contacts_is_snapshot():
    """返回列表必须是独立副本：清空返回值不影响 ContactBook 内部状态"""
    service = make_service()
    service.add_contact("Alice", "13800138000")

    listing = service.list_all_contacts()
    listing.clear()

    assert len(service.list_all_contacts()) == 1


# ==================== change_phone ====================

def test_change_phone_success_updates_and_marks_dirty():
    service = make_service()
    created = service.add_contact("Alice", "13800138000")
    calls_before = tracker_of(service).calls

    service.change_phone(created.contact_id, "13900139000")

    assert created.phone == "13900139000"
    assert tracker_of(service).calls == calls_before + 1


def test_change_phone_duplicate_raises_duplicate_error_and_not_dirty():
    service = make_service()
    first = service.add_contact("Alice", "13800138000")
    second = service.add_contact("Bob", "13900139000")
    calls_before = tracker_of(service).calls

    with pytest.raises(ContactDuplicateError):
        service.change_phone(second.contact_id, first.phone)

    assert second.phone == "13900139000"
    assert tracker_of(service).calls == calls_before


def test_change_phone_invalid_format_raises_input_error():
    service = make_service()
    created = service.add_contact("Alice", "13800138000")
    calls_before = tracker_of(service).calls

    with pytest.raises(ContactInputError):
        service.change_phone(created.contact_id, "abc123")

    assert created.phone == "13800138000"
    assert tracker_of(service).calls == calls_before


# ==================== 排他性检查 ====================

def test_duplicate_phone_error_not_swallowed_by_input_error():
    """重复号码必须命中 ContactDuplicateError，而不是宽松的输入错误"""
    from contact_manager.contact_service import ContactDuplicateError
    service = make_service()
    service.add_contact("Alice", "13800138000")

    with pytest.raises(ContactDuplicateError):
        service.add_contact("Bob", "13800138000")


def test_delete_unknown_raises_not_found_type():
    from contact_manager.contact_service import ContactNotFoundError
    service = make_service()

    with pytest.raises(ContactNotFoundError):
        service.delete_contact("ghost-id")
