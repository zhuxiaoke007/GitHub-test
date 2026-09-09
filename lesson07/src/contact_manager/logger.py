# infrastructure/logger.py
"""
日志记录模块 - 提供简单的文件日志功能
"""
import os

class Logger:
    """
    极简文件日志记录器
    
    职责：
        1. 将日志消息写入: 主日志 → 备用日志 → 控制台
        2. 支持 INFO、WARNING、ERROR 三个级别
    
    使用示例：
        logger = Logger()
        logger.info("应用程序启动")
        logger.warning("联系人目录文件未找到")
        logger.error("日志写入失败")
    """
    
    def __init__(self):
        """初始化日志记录器（降级安全）"""
        self._main_file = None      # 主日志文件句柄
        self._fallback_file = None  # 备用日志文件句柄
        self._main_log = "logs/app.log"
        self._fallback_log = "logs/fallback.log"

        # 尝试创建 logs 目录
        try:
            os.makedirs("logs", exist_ok=True)
        except Exception:
            # 目录创建失败，降级
            print("警告：无法创建 logs 目录，日志将只输出到控制台")
            return                  #回到 main.py 中创建 Logger 的地方 logger = Logger()  ← ① 创建 Logger 实例
        
        # 尝试打开主日志文件
        try:
            self._main_file = open(self._main_log, "a", encoding="utf-8")
        except Exception as e:
            print(f"警告：无法打开主日志文件（{e}）")
            self._main_file = None              # ← 失败后保持"无文件"状态
    
    def _write_log(self, level: str, message: str) -> None:    # 假设调用：logger.info("添加联系人成功")
        """
        写入日志（主日志 → 备用日志 → 控制台）

        职责：
        1. 编排三层降级策略
        2. 主日志带重试（3次）
        3. 备用日志不带重试
        4. 全部失败 → 控制台兜底
        """
        log_line = f"[{level}] {message}\n"      #组装日志行 计算结果：log_line = "[INFO] 添加联系人成功\n

        # 1️⃣ 主日志（带重试，最多3次）
        if self._write_main_with_retry(log_line):
            return  # 主日志成功，结束

        # 2️⃣ 主日志全部失败 → 尝试备用日志（1次）
        if self._write_fallback(log_line):
            return  # 备用成功，结束

        # 3️⃣ 主日志和备用日志都失败 → 输出到控制台
        print(log_line.strip()) 

    def _write_main_with_retry(self, log_line: str) -> bool:
        """
        尝试写入主日志，失败时重试
        
        Returns:
            bool: True 写入成功，False 全部失败
        """
        max_retries = 3
        
        for _ in range(max_retries):
            # 尝试写入一次
            # _write_main() 内部已经处理了：
            #   - 写入失败 → close() + = None → 返回 False
            if self._write_main(log_line):
                return True  # 成功，结束
            # 失败 → 继续下一次循环
            # 不需要再次 close()，_write_main() 已经做了
        
        return False  # 所有尝试失败，返回 False
    
    def _write_main(self, log_line: str) -> bool:
        """
        尝试向主日志写入一次（不重试）
        
        Returns:
            bool: True 写入成功，False 写入失败
        """
        # 1️⃣ 确保有可用句柄
        if self._main_file is None:
            try:
                self._main_file = open(self._main_log, "a", encoding="utf-8")
            except Exception:
                return False
        
        # 2️⃣ 尝试写入一次
        try:
            self._main_file.write(log_line)     #将日志行写入文件缓冲区（内存）
            self._main_file.flush()             #将缓冲区中的数据立即写入磁盘
            return True                           # 主日志成功，直接返回
        except Exception:
            # 3️⃣ 写入失败 → 关闭并清除引用
            if self._main_file is not None:
                try:
                    self._main_file.close()
                except Exception:
                    pass
                self._main_file = None
            return False

    def _write_fallback(self, log_line: str) -> bool:
        """尝试向备用日志写入一次

        Returns:
            bool: True 写入成功，False 写入失败
        """
        try:
            # 按需打开备用文件
            if self._fallback_file is None:
                self._fallback_file = open(self._fallback_log, "a", encoding="utf-8")
            # 写入（无论文件是刚打开还是已经存在）
            self._fallback_file.write(log_line)
            self._fallback_file.flush()
            return True
        except Exception:
            # 先尝试关闭文件（先释放资源）
            if self._fallback_file is not None:
                try:
                    self._fallback_file.close()
                except Exception:
                    pass  # 关闭失败也忽略
            # 再清除资源引用
            self._fallback_file = None
            return False
    
    def info(self, message: str) -> None:
        self._write_log("INFO", message)
    
    def warning(self, message: str) -> None:
        self._write_log("WARNING", message)
    
    def error(self, message: str) -> None:
        self._write_log("ERROR", message)
    
    def close(self) -> None:
        """关闭所有日志文件"""
        if self._main_file is not None:
            try:
                self._main_file.close()
            except Exception:
                pass
            self._main_file = None
        
        if self._fallback_file is not None:
            try:
                self._fallback_file.close()
            except Exception:
                pass
            self._fallback_file = None

