import logging
import sys
from typing import Optional

def setup_logging(log_level: str = "INFO", enable_rich: bool = True, log_file: Optional[str] = None) -> None:
    """
    设置日志系统
    
    Args:
        log_level: 日志级别，默认为INFO
        enable_rich: 是否启用rich格式化输出
        log_file: 日志文件路径，如果不指定则只输出到控制台
    """
    # 设置日志级别
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"无效的日志级别: {log_level}")
    
    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # 移除已有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 添加控制台处理器
    if enable_rich:
        try:
            from rich.logging import RichHandler
            console_handler = RichHandler(rich_tracebacks=True)
        except ImportError:
            console_handler = logging.StreamHandler(sys.stdout)
            console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            console_handler.setFormatter(logging.Formatter(console_format))
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        console_handler.setFormatter(logging.Formatter(console_format))
    
    logger.addHandler(console_handler)
    
    # 添加文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        file_handler.setFormatter(logging.Formatter(file_format))
        logger.addHandler(file_handler)
    
    # 设置第三方日志级别
    logging.getLogger("paho.mqtt").setLevel(logging.WARNING) 