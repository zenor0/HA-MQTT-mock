"""基本设备模型模块"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ha_mqtt_mock.config import MQTTConfig
from ha_mqtt_mock.utils.mqtt_helpers import publish_discovery, publish_state

logger = logging.getLogger(__name__)

class MQTTDevice(ABC):
    """MQTT设备基类，所有设备模型都应该继承自这个类"""
    
    def __init__(self, component: str, object_id: str, name: Optional[str] = None, state: Optional[Dict[str, Any]] = None, *args, **kwargs) -> None:
        """
        初始化MQTT设备
        
        Args:
            component: 设备组件类型（如light, sensor等）
            object_id: 设备唯一标识
            name: 设备显示名称，如果不提供则使用object_id
        """
        self.component = component
        self.object_id = object_id
        self.name = name if name else object_id.replace("_", " ").title()
        self.state: Dict[str, Any] = state if state else {}
        
        # 获取配置实例
        config = MQTTConfig.get_instance()
        
        # 设置主题
        self.base_topic = f"{config.root_prefix}/{self.component}/{self.object_id}"
        self.state_topic = f"{self.base_topic}/state"
        self.command_topic = f"{self.base_topic}/set"
        self.discovery_topic = f"{self.base_topic}/config"
        
        # 设置发现负载
        self.discovery_payload = self._get_discovery_payload()
    
    @abstractmethod
    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取设备发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        pass
    
    def publish_discovery(self, client) -> None:
        """
        发布设备发现信息
        
        Args:
            client: MQTT客户端对象
        """
        try:
            publish_discovery(
                client, 
                self.component, 
                self.object_id, 
                self.discovery_payload, 
                retain=True
            )
        except Exception as e:
            logger.exception(f"发布{self.name}的发现信息时发生错误: {e}")
    
    def publish_state(self, client) -> bool:
        """
        发布设备状态信息
        
        Args:
            client: MQTT客户端对象
            
        Returns:
            bool: 发布是否成功
        """
        try:
            return publish_state(client, self.state_topic, self.state)
        except Exception as e:
            logger.exception(f"发布{self.name}的状态信息时发生错误: {e}")
            return False
    
    def update_state(self, client, payload: Dict[str, Any]) -> bool:
        """
        更新设备状态
        
        Args:
            client: MQTT客户端对象
            payload: 状态更新负载
            
        Returns:
            bool: 更新是否成功
        """
        try:
            self.state.update(payload)
            return self.publish_state(client)
        except Exception as e:
            logger.exception(f"更新{self.name}的状态时发生错误: {e}, payload: {payload}")
            return False
    
    def on_command(self, client, payload: Any) -> bool:
        """
        处理设备命令
        
        Args:
            client: MQTT客户端对象
            payload: 命令负载
            
        Returns:
            bool: 处理是否成功
        """
        if isinstance(payload, bytes):
            payload = payload.decode()
        
        # 检查payload是否是有效的JSON
        if payload and payload[0] == "{":
            try:
                parsed_payload = json.loads(payload)
                return self.update_state(client, parsed_payload)
            except json.JSONDecodeError:
                logger.error(f"解析{self.name}的JSON命令失败: {payload}")
                return False
        else:
            # 非JSON负载，尝试作为简单字符串处理
            logger.warning(f"{self.name}收到非JSON命令: {payload}")
            return self.update_state(client, {"state": payload})
    
    def update_state_mock(self) -> None:
        """
        模拟更新设备状态，子类可以重写这个方法来提供模拟行为
        """
        pass
    
    def dump_state(self) -> str:
        """
        获取状态的JSON字符串
        
        Returns:
            str: 状态的JSON字符串
        """
        return json.dumps(self.state) 