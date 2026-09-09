from unittest.mock import Mock, patch
from contact_manager.logger import Logger

def test_write_fallback_write_fails():
    logger = Logger()
    
    # 1️⃣ 创建 mock_file，设置 write() 抛出异常
    mock_file = Mock()
    mock_file.write.side_effect = OSError("write failed")
    
    # 2️⃣ 让 logger._fallback_file 指向 mock_file
    logger._fallback_file = mock_file
    
    # 3️⃣ 执行 _write_fallback
    result = logger._write_fallback("[ERROR] test\n")
    
    # 4️⃣ 验证：返回 False
    assert result is False
    
    # 5️⃣ 验证：资源被清理（close 被调用，且被置为 None）
    mock_file.close.assert_called_once()
    assert logger._fallback_file is None