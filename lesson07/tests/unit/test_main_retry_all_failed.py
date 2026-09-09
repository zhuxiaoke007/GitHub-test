from unittest.mock import patch, call
from contact_manager.logger import Logger

def test_main_retry_all_failed():
    logger = Logger()
    
    with patch.object(logger, '_write_main') as mock_write_main:
        # 设置 Mock 连续三次返回 False
        mock_write_main.side_effect = [False, False, False]
        
        result = logger._write_main_with_retry("hello")
        
        # 验证返回值
        assert result is False
        
        # 验证调用次数
        assert mock_write_main.call_count == 3
        
        # 验证三次调用参数都是 "hello"
        expected_calls = [
            call("hello"),
            call("hello"),
            call("hello"),
        ]
        assert mock_write_main.call_args_list == expected_calls