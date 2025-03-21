"""MQTT设备模拟器模块"""

import asyncio
import logging
from typing import Dict, List, Optional, Union

from .models.base import MQTTDevice

logger = logging.getLogger(__name__)

class MockDeviceManager:
    """MQTT设备模拟器管理类"""
    
    def __init__(self) -> None:
        """初始化设备模拟器管理器"""
        self.devices: List[MQTTDevice] = []
        self.command_device_mapping: Dict[str, MQTTDevice] = {}
        self.is_running = False
        self.mock_task = None  # 用于存储模拟任务的引用
    
    def add_device(self, device: MQTTDevice) -> None:
        """
        添加设备到模拟器
        
        Args:
            device: MQTT设备实例
        """
        self.devices.append(device)
        self.command_device_mapping[device.command_topic] = device
        logger.info(f"添加设备 '{device.name}' (ID: {device.object_id})")
    
    def add_devices(self, devices: List[MQTTDevice]) -> None:
        """
        批量添加设备到模拟器
        
        Args:
            devices: MQTT设备实例列表
        """
        for device in devices:
            self.add_device(device)
    
    def get_device(self, object_id: str) -> Optional[MQTTDevice]:
        """
        通过对象ID获取设备
        
        Args:
            object_id: 设备对象ID
            
        Returns:
            Optional[MQTTDevice]: 找到的设备实例，如果没找到则返回None
        """
        for device in self.devices:
            if device.object_id == object_id:
                return device
        return None
    
    def remove_device(self, object_id: str) -> bool:
        """
        通过对象ID移除设备
        
        Args:
            object_id: 设备对象ID
            
        Returns:
            bool: 如果成功移除设备则返回True，否则返回False
        """
        device = self.get_device(object_id)
        if device:
            self.devices.remove(device)
            self.command_device_mapping.pop(device.command_topic, None)
            logger.info(f"移除设备 '{device.name}' (ID: {device.object_id})")
            return True
        return False
    
    def publish_all_discoveries(self, client) -> None:
        """
        发布所有设备的发现信息
        
        Args:
            client: MQTT客户端实例
        """
        for device in self.devices:
            device.publish_discovery(client)
            logger.debug(f"已发布设备 '{device.name}' 的发现信息")
    
    def publish_all_states(self, client) -> None:
        """
        发布所有设备的状态信息
        
        Args:
            client: MQTT客户端实例
        """
        for device in self.devices:
            device.publish_state(client)
            logger.debug(f"已发布设备 '{device.name}' 的状态信息")
    
    def subscribe_all_commands(self, client) -> None:
        """
        订阅所有设备的命令主题
        
        Args:
            client: MQTT客户端实例
        """
        for device in self.devices:
            client.subscribe(device.command_topic)
            logger.debug(f"已订阅设备 '{device.name}' 的命令主题")
    
    def on_message(self, client, userdata, message) -> None:
        """
        处理接收到的MQTT消息
        
        Args:
            client: MQTT客户端实例
            userdata: 用户数据
            message: MQTT消息
        """
        topic = message.topic
        payload = message.payload
        
        device = self.command_device_mapping.get(topic)
        if device:
            logger.debug(f"接收到设备 '{device.name}' 的命令: {payload}")
            device.on_command(client, payload)
        else:
            logger.warning(f"收到未知主题的消息: {topic}")

    async def mock_devices(self, client, interval: int = 10) -> None:
        """
        模拟设备状态变化
        
        Args:
            client: MQTT客户端实例
            interval: 模拟间隔（秒）
        """
        self.is_running = True
        logger.info(f"开始模拟 {len(self.devices)} 个设备的状态变化，间隔 {interval} 秒")
        
        try:
            while self.is_running:
                for device in self.devices:
                    # 检查设备是否有模拟方法
                    if hasattr(device, "update_state_mock"):
                        device.update_state_mock()
                        device.publish_state(client)
                        logger.debug(f"已更新并发布设备 '{device.name}' 的模拟状态")
                
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("设备模拟任务已取消")
            self.is_running = False
            # 重新抛出，让调用者知道任务已取消
            raise
        except Exception as e:
            logger.exception(f"设备模拟过程中发生错误: {e}")
            self.is_running = False
            # 重新抛出异常，让调用者处理
            raise
    
    def stop_mock(self) -> None:
        """停止模拟设备状态变化"""
        self.is_running = False
        logger.info("已停止设备模拟") 