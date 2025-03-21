"""主程序入口模块"""

import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import List, Optional, Dict

import paho.mqtt.client as mqtt
import uvicorn
from fastapi import FastAPI

from . import __version__
from .api import create_app
from ha_mqtt_mock.config import MQTTConfig, create_default_config
from ha_mqtt_mock.device_config import DeviceConfig
from ha_mqtt_mock.mock import MockDeviceManager
from ha_mqtt_mock.models import Light, Sensor, BinarySensor
from ha_mqtt_mock.utils.logging import setup_logging

logger = logging.getLogger(__name__)

def create_sample_devices() -> List[Dict]:
    """
    创建示例设备配置列表（仅用于初始化空配置）
    
    Returns:
        List[Dict]: 示例设备配置列表
    """
    return [
        {
            "type": "light",
            "object_id": "rgb_light",
            "name": "客厅灯光"
        },
        {
            "type": "light",
            "object_id": "rgb_light_bedroom",
            "name": "卧室灯光"
        },
        {
            "type": "sensor",
            "object_id": "temp_sensor",
            "name": "温度传感器",
            "sensor_type": "temperature"
        },
        {
            "type": "sensor",
            "object_id": "humidity_sensor",
            "name": "湿度传感器",
            "sensor_type": "humidity"
        },
        {
            "type": "sensor",
            "object_id": "pressure_sensor",
            "name": "压力传感器",
            "sensor_type": "pressure"
        },
        {
            "type": "binary_sensor",
            "object_id": "motion_sensor",
            "name": "人体感应",
            "sensor_type": "motion"
        },
        {
            "type": "binary_sensor",
            "object_id": "door_sensor",
            "name": "门窗感应",
            "sensor_type": "door"
        }
    ]

def create_mqtt_client(mqtt_config: MQTTConfig) -> mqtt.Client:
    """
    创建MQTT客户端
    
    Args:
        mqtt_config: MQTT配置
        
    Returns:
        mqtt.Client: MQTT客户端实例
    """
    # 创建客户端
    client = mqtt.Client(client_id=mqtt_config.client_id)
    
    # 设置用户名和密码（如果提供）
    if mqtt_config.username:
        client.username_pw_set(username=mqtt_config.username, password=mqtt_config.password)
    
    # 连接回调
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"已连接到MQTT Broker: {mqtt_config.broker_address}:{mqtt_config.broker_port}")
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
    
    parsed_args = parser.parse_args(args)
    
    # 设置日志
    log_level = "DEBUG" if parsed_args.verbose else "INFO"
    setup_logging(log_level=log_level, enable_rich=not parsed_args.no_rich, log_file=parsed_args.log_file)
    
    # 更新MQTT配置
    mqtt_config.update(
        broker_address=parsed_args.broker,
        broker_port=parsed_args.port,
        username=parsed_args.username,
        password=parsed_args.password,
    )
    
    # 创建MQTT客户端
    mqtt_client = create_mqtt_client(mqtt_config)
    
    # 创建设备配置管理器
    device_config = DeviceConfig(config_file=parsed_args.config_file)
    
    # 加载设备配置
    devices_data = device_config.load()
    
    # 如果没有设备配置，创建示例设备
    if not devices_data:
        logger.info("没有找到设备配置，创建示例设备")
        sample_devices = create_sample_devices()
        device_config.save(sample_devices)
    
    # 创建设备实例
    device_instances = device_config.create_devices()
    
    # 创建设备管理器
    device_manager = MockDeviceManager()
    
    # 处理消息回调
    mqtt_client.on_message = device_manager.on_message
    
    # 添加设备到管理器
    device_manager.add_devices(device_instances)
    
    # 处理中断信号
    loop = asyncio.get_running_loop()
    mock_task = None
    api_server = None
    api_app = None
    
    # 创建一个异步事件，用于协调优雅退出
    shutdown_event = asyncio.Event()
    
    # 如果启用API服务器，创建FastAPI应用
    if not parsed_args.disable_api:
        api_app = create_app(device_config, device_manager)
        
        # 配置Uvicorn服务器
        uvicorn_config = uvicorn.Config(
            app=api_app,
            host=parsed_args.api_host,
            port=parsed_args.api_port,
            log_level=log_level.lower(),
            timeout_graceful_shutdown=5,  # 设置优雅关闭超时时间
            timeout_keep_alive=5,  # 设置保持连接超时时间
            log_config=None,  # 禁用uvicorn默认日志配置
        )
        api_server = uvicorn.Server(uvicorn_config)
    
    async def start_api_server():
        """启动API服务器"""
        if api_server:
            logger.info(f"启动API服务器 - http://{parsed_args.api_host}:{parsed_args.api_port}")
            await api_server.serve()
    
    async def graceful_shutdown():
        """优雅退出的异步处理函数"""
        logger.info("收到中断信号，正在优雅关闭...")
        
        # 设置关闭事件
        shutdown_event.set()
        
        # 停止API服务器（如果存在）
        if api_server:
            logger.debug("正在关闭API服务器...")
            api_server.should_exit = True
            try:
                await asyncio.wait_for(api_server.shutdown(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("API服务器关闭超时")
            except Exception as e:
                logger.warning(f"API服务器关闭时发生错误: {e}")
        
        # 取消模拟任务（如果存在）
        if mock_task and not mock_task.done():
            logger.debug("正在取消模拟任务...")
            mock_task.cancel()
            try:
                await mock_task
            except asyncio.CancelledError:
                pass
        
        # 停止设备模拟
        device_manager.stop_mock()
        
        # 断开MQTT连接
        logger.debug("正在断开MQTT连接...")
        mqtt_client.disconnect()
        mqtt_client.loop_stop()

    def signal_handler():
        """处理中断信号的回调函数"""
        if not shutdown_event.is_set():  # 防止重复触发
            # 创建一个关闭任务，不阻塞信号处理器
            asyncio.create_task(graceful_shutdown())
    
    # 注册信号处理器
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
        
        # 创建并跟踪模拟任务
        mock_task = asyncio.create_task(device_manager.mock_devices(mqtt_client, interval=parsed_args.interval))
        
        # 如果启用API服务器，创建API服务器任务
        api_task = None
        if api_server:
            api_task = asyncio.create_task(start_api_server())
        
        # 创建任务列表
        tasks = [mock_task]
        if api_task:
            tasks.append(api_task)
        
        # 等待任务完成或关闭事件
        try:
            await asyncio.wait(
                tasks + [asyncio.create_task(shutdown_event.wait())],
                return_when=asyncio.FIRST_COMPLETED
            )
        except asyncio.CancelledError:
            # 如果主任务被取消，确保优雅关闭
            await graceful_shutdown()
        
        return 0
        
    except Exception as e:
        logger.exception(f"运行时发生错误: {e}")
        return 1
    finally:
        # 确保资源被清理
        if not mqtt_client._thread_terminate:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
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

if __name__ == "__main__":
    run()