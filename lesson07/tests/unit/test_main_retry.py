from unittest.mock import patch, call
from contact_manager.logger import Logger

def test_main_retry_success():
    logger = Logger()

    # with ... as ...	Python 上下文管理器，进入时创建，退出时自动清理
    # 临时替换 logger 对象的 _write_main 方法为 Mock 对象。
    # 给这个 Mock 起名为 mock_write_main，方便后续操作
    with patch.object(logger, '_write_main') as mock_write_main:  
        # .side_effect:Mock 的一个属性, 设置 Mock 的返回值序列：第一次调用返回 False，第二次调用返回 True, 
        # 第三次调用抛出 StopIteration（因为列表用完了）
        mock_write_main.side_effect = [False, True]
        
        # Act: 调用 _write_main_with_retry
        result = logger._write_main_with_retry("hello")

        # ① 验证返回值
        # assert 条件表达式
        # 如果条件为 True → 继续执行
        # 如果条件为 False → 抛出 AssertionError
        assert result is True
        
        # ② 验证调用次数
        assert mock_write_main.call_count == 2
        
        # ③ 验证完整调用序列
        expected_calls = [
            call("hello"),
            call("hello"),
        ]
        assert mock_write_main.call_args_list == expected_calls