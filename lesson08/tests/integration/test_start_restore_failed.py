from unittest.mock import Mock

import pytest
from contact_manager.application_lifecycle import ApplicationLifecycle


def test_start_restore_failed():
    # 1️⃣ 创建 Mock 对象
    mock_book = Mock()
    mock_storage = Mock()
    mock_logger = Mock()
    
    # 2️⃣ 准备数据
    expected_data = [{"name": "Tom", "phone": "12345678901"}]
    mock_storage.load.return_value = expected_data
    
    # 3️⃣ 设置 from_data() 抛出 ValueError
    mock_book.from_data.side_effect = ValueError("数据非法")
    
    # 4️⃣ 创建 ApplicationLifecycle
    lifecycle = ApplicationLifecycle(mock_book, mock_storage, mock_logger)
    
    # 5️⃣ 验证 ValueError 被传播
    with pytest.raises(ValueError):
        lifecycle.start()
    
    # 6️⃣ 验证 logger.info() 没有被调用
    mock_logger.info.assert_not_called()