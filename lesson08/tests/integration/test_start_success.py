from unittest.mock import Mock

from contact_manager.application_lifecycle import ApplicationLifecycle

"""
准备协作者
    ↓
控制 Storage.load() 返回值
    ↓
执行 lifecycle.start()
    ↓
验证：
    Storage.load()       → 1 次
    Logger.info()        → 正确消息
    ContactBook.from_data() → 正确数据
"""

def test_start_success():
    # 1️⃣ 创建 Mock 对象
    mock_book = Mock()
    mock_storage = Mock()
    mock_logger = Mock()
    
    # 2️⃣ 准备数据
    expected_data = [{"name": "Tom", "phone": "12345678901"}]
    mock_storage.load.return_value = expected_data
    
    # 3️⃣ 执行 start()
    lifecycle = ApplicationLifecycle(mock_book, mock_storage, mock_logger)
    lifecycle.start()
    
    # 4️⃣ 验证：从 Storage 获取数据
    mock_storage.load.assert_called_once()
    
    # 5️⃣ 验证：记录成功日志
    mock_logger.info.assert_called_once_with("数据加载成功")
    
    # 6️⃣ 验证：将数据正确交给 ContactBook
    mock_book.from_data.assert_called_once_with(expected_data)