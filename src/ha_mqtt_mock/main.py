"""主程序入口模块"""

import argparse
import asyncio
import logging
import signal
import sys
from typing import List, Optional

import paho.mqtt.client as mqtt

from . import __version__
from .config import MQTTConfig, config
from .mock import MockDeviceManager
from .models import Light, Sensor, BinarySensor
from .utils.logging import setup_logging

logger = logging.getLogger(__name__)

def create_sample_devices() -> List:
    """
    创建示例设备列表
    
    Returns:
        List: 示例设备列表
    """
    return [
        Light(object_id='rgb_light', name="客厅灯光"),
        Light(object_id='rgb_light_bedroom', name="卧室灯光"),
        Sensor(object_id='temp_sensor', name="温度传感器", sensor_type="temperature"),
        Sensor(object_id='humidity_sensor', name="湿度传感器", sensor_type="humidity"),
        Sensor(object_id='pressure_sensor', name="压力传感器", sensor_type="pressure"),
        BinarySensor(object_id='motion_sensor', name="人体感应", sensor_type="motion"),
        BinarySensor(object_id='door_sensor', name="门窗感应", sensor_type="door"),
    ]

def create_mqtt_client(config: MQTTConfig) -> mqtt.Client:
    """
    创建MQTT客户端
    
    Args:
        config: MQTT配置
        
    Returns:
        mqtt.Client: MQTT客户端实例
    """
    # 创建客户端
    client = mqtt.Client(config.client_id)
    
    # 设置用户名和密码（如果提供）
    if config.username:
        client.username_pw_set(username=config.username, password=config.password)
    
    # 连接回调
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"已连接到MQTT Broker: {config.broker_address}:{config.broker_port}")
        else:
            logger.error(f"连接MQTT Broker失败，返回码: {rc}")
    
    client.on_connect = on_connect
    
    return client

async def main(args: Optional[List[str]] = None) -> int:
    """
    主函数
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description=f"Home Assistant MQTT模拟器 v{__version__}")
    parser.add_argument("-b", "--broker", help="MQTT服务器地址", default=config.broker_address)
    parser.add_argument("-p", "--port", type=int, help="MQTT服务器端口", default=config.broker_port)
    parser.add_argument("-u", "--username", help="MQTT用户名", default=config.username)
    parser.add_argument("--password", help="MQTT密码", default=config.password)
    parser.add_argument("-i", "--interval", type=int, help="模拟更新间隔（秒）", default=10)
    parser.add_argument("-v", "--verbose", action="store_true", help="启用详细日志")
    parser.add_argument("--no-rich", action="store_true", help="禁用富文本日志格式")
    parser.add_argument("--log-file", help="日志文件路径")
    
    parsed_args = parser.parse_args(args)
    
    # 设置日志
    log_level = "DEBUG" if parsed_args.verbose else "INFO"
    setup_logging(log_level=log_level, enable_rich=not parsed_args.no_rich, log_file=parsed_args.log_file)
    
    # 更新配置
    mqtt_config = MQTTConfig(
        broker_address=parsed_args.broker,
        broker_port=parsed_args.port,
        username=parsed_args.username,
        password=parsed_args.password,
    )
    
    # 创建MQTT客户端
    mqtt_client = create_mqtt_client(mqtt_config)
    
    # 创建设备管理器
    device_manager = MockDeviceManager()
    
    # 处理消息回调
    mqtt_client.on_message = device_manager.on_message
    
    # 添加示例设备
    device_manager.add_devices(create_sample_devices())
    
    # 处理中断信号
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        logger.info("收到中断信号，正在关闭...")
        device_manager.stop_mock()
        mqtt_client.disconnect()
        loop.stop()
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        # 连接MQTT代理
        mqtt_client.connect(mqtt_config.broker_address, mqtt_config.broker_port)
        
        # 启动MQTT循环
        mqtt_client.loop_start()
        
        # 发布设备发现信息
        device_manager.publish_all_discoveries(mqtt_client)
        
        # 发布初始状态
        device_manager.publish_all_states(mqtt_client)
        
        # 订阅命令主题
        device_manager.subscribe_all_commands(mqtt_client)
        
        # 启动模拟
        logger.info(f"HA-MQTT-mock v{__version__} 已启动")
        logger.info(f"已添加 {len(device_manager.devices)} 个设备")
        
        # 运行模拟任务
        await device_manager.mock_devices(mqtt_client, interval=parsed_args.interval)
        
        return 0
    except KeyboardInterrupt:
        logger.info("用户中断，正在关闭...")
        return 0
    except Exception as e:
        logger.exception(f"运行时发生错误: {e}")
        return 1
    finally:
        # 清理资源
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

def run():
    """命令行入口点"""
    sys.exit(asyncio.run(main()))