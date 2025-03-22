"""命令行参数处理模块"""

import argparse
import asyncio
import logging
import sys
from typing import List, Optional

from . import __version__
from .config import MQTTConfig, create_default_config
from .engine import AppService
from .utils.logging import setup_logging

logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    解析命令行参数
    
    Args:
        args: 命令行参数列表
        
    Returns:
        argparse.Namespace: 解析后的参数
    """
    # 创建默认MQTT配置
    mqtt_config = create_default_config()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description=f"Home Assistant MQTT模拟器 v{__version__}")
    parser.add_argument("-b", "--broker", help="MQTT服务器地址", default=mqtt_config.broker_address)
    parser.add_argument("-p", "--port", type=int, help="MQTT服务器端口", default=mqtt_config.broker_port)
    parser.add_argument("-u", "--username", help="MQTT用户名", default=mqtt_config.username)
    parser.add_argument("--password", help="MQTT密码", default=mqtt_config.password)
    parser.add_argument("-i", "--interval", type=int, help="模拟更新间隔（秒）", default=10)
    parser.add_argument("-v", "--verbose", action="store_true", help="启用详细日志")
    parser.add_argument("--no-rich", action="store_true", help="禁用富文本日志格式")
    parser.add_argument("--log-file", help="日志文件路径")
    parser.add_argument("--config-file", help="设备配置文件路径", default="devices.json")
    parser.add_argument("--api-host", help="API服务器主机地址", default="127.0.0.1")
    parser.add_argument("--api-port", type=int, help="API服务器端口", default=8080)
    parser.add_argument("--disable-api", action="store_true", help="禁用API服务器")

    return parser.parse_args(args)

async def main(args: Optional[List[str]] = None) -> int:
    """
    主函数
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    # 解析命令行参数
    parsed_args = parse_args(args)
    
    # 设置日志
    log_level = "DEBUG" if parsed_args.verbose else "INFO"
    setup_logging(log_level=log_level, enable_rich=not parsed_args.no_rich, log_file=parsed_args.log_file)
    
    # 创建MQTT配置
    mqtt_config = create_default_config()
    mqtt_config.update(
        broker_address=parsed_args.broker,
        broker_port=parsed_args.port,
        username=parsed_args.username,
        password=parsed_args.password,
    )
    logger.debug(f"MQTT配置: {mqtt_config}")
    
    # 创建应用服务
    service = AppService(
        mqtt_config=mqtt_config,
        config_file=parsed_args.config_file,
        mock_interval=parsed_args.interval,
        api_host=parsed_args.api_host,
        api_port=parsed_args.api_port,
        enable_api=not parsed_args.disable_api
    )
    
    try:
        # 获取事件循环
        loop = asyncio.get_running_loop()
        
        # 设置信号处理器
        service.setup_signal_handlers(loop)
        
        # 初始化服务
        if not await service.initialize():
            return 1
        
        # 启动服务
        await service.start()
        
        return 0
        
    except Exception as e:
        logger.exception(f"运行时发生错误: {e}")
        return 1
    finally:
        # 确保服务被关闭
        await service.shutdown()
        logger.info("程序已完全关闭")

def run():
    """命令行入口点"""
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        # 这里可能捕获到asyncio.run()本身的中断
        logger.info("程序已通过键盘中断退出")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"程序出现未处理异常: {e}")
        sys.exit(1) 