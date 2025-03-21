"""日志配置模块"""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

def setup_logging(log_level: str = "INFO", enable_rich: bool = True, log_file: Optional[str] = None) -> None:
    """
    设置日志配置
    
    Args:
        log_level: 日志级别
        enable_rich: 是否启用rich格式化
        log_file: 日志文件路径
    """
    # 创建rich控制台
    console = Console(force_terminal=enable_rich)
    
    # 配置日志处理器
    handlers = []
    
    # 添加rich处理器（如果启用）
    if enable_rich:
        rich_handler = RichHandler(
            console=console,
            show_path=False,
            enable_link_path=True,
            markup=True,
            rich_tracebacks=True
        )
        rich_handler.setLevel(log_level)
        handlers.append(rich_handler)
    else:
        # 添加标准流处理器
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        handlers.append(stream_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=handlers
    )
    
    # 设置uvicorn和fastapi日志配置
    configure_uvicorn_logging(enable_rich)

def configure_uvicorn_logging(enable_rich: bool = True) -> None:
    """
    配置uvicorn日志以使用rich格式化器
    
    Args:
        enable_rich: 是否启用rich格式化
    """
    if enable_rich:
        # 配置uvicorn的日志处理器
        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = False  # 防止日志传播到根日志记录器
        
        # 创建rich处理器
        rich_handler = RichHandler(
            show_path=False,
            enable_link_path=True,
            markup=True,
            rich_tracebacks=True
        )
        uvicorn_logger.addHandler(rich_handler)
        
        # 配置uvicorn的访问日志
        uvicorn_access_logger = logging.getLogger("uvicorn.access")
        uvicorn_access_logger.handlers.clear()
        uvicorn_access_logger.propagate = False  # 防止日志传播到根日志记录器
        uvicorn_access_logger.addHandler(rich_handler)
        
        # 配置FastAPI日志
        fastapi_logger = logging.getLogger("fastapi")
        fastapi_logger.handlers.clear()
        fastapi_logger.propagate = False  # 防止日志传播到根日志记录器
        fastapi_logger.addHandler(rich_handler)

    # 设置第三方日志级别
    logging.getLogger("paho.mqtt").setLevel(logging.WARNING) 