from unittest.mock import patch

from contact_manager.logger import Logger


def test_write_log_all_failed(capsys):
    logger = Logger()
    
    with patch.object(logger, '_write_main_with_retry') as mock_main:
        with patch.object(logger, '_write_fallback') as mock_fallback:
            # 设置都返回 False（全部失败）
            mock_main.return_value = False
            mock_fallback.return_value = False
            
            # 执行 _write_log
            logger._write_log("INFO", "hello")
            
            # 验证两个 Mock 各调用 1 次
            assert mock_main.call_count == 1
            assert mock_fallback.call_count == 1
            
            # 验证控制台输出
            captured = capsys.readouterr()
            assert captured.out == "[INFO] hello\n"