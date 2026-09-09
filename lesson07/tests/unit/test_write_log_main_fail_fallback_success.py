from unittest.mock import patch, call
from contact_manager.logger import Logger

def test_write_log_main_fail_fallback_success():
    logger = Logger()

    with patch.object(logger, '_write_main_with_retry') as mock_main:
        with patch.object(logger, '_write_fallback') as mock_fallback:
            # 设置返回值
            mock_main.return_value = False      # 主日志失败
            mock_fallback.return_value = True   # 备用日志成功

            # 执行 _write_log
            logger._write_log("INFO", "hello")

            # 验证 _write_main_with_retry 调用 1 次
            assert mock_main.call_count == 1
            mock_main.assert_called_with("[INFO] hello\n")

            # 验证 _write_fallback 调用 1 次
            assert mock_fallback.call_count == 1
            mock_fallback.assert_called_with("[INFO] hello\n")