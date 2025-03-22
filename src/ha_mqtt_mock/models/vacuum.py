"""吸尘器设备模型"""

import random
from typing import Any, Dict, Optional, List

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class Vacuum(MQTTDevice):
    """吸尘器设备模型类"""

    def __init__(
        self,
        object_id: str,
        name: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        初始化吸尘器设备
        
        Args:
            object_id: 设备唯一标识
            name: 设备显示名称
        """
        super().__init__(
            component="vacuum", object_id=object_id, name=name, state=state, *args, **kwargs
        )

        # 设置默认状态
        self.state = self.state or {
            "state": "idle", 
            "fan_speed": "medium", 
            "battery_level": 100
        }

    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取吸尘器设备的发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        payload = {
            "name": self.name,
            "unique_id": f"mock_vacuum_{self.object_id}",
            "schema": "state",
            "supported_features": [
                "start",
                "pause",
                "stop",
                "return_home",
                "battery",
                "status",
                "locate",
                "clean_spot",
                "fan_speed",
                "send_command",
            ],
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "fan_speed_list": ["off", "low", "medium", "high", "max"],
            "send_command_topic": self.command_topic
        }

        payload["device"] = generate_device_info(self.name)
        return payload

    def update_state(self, client, payload: Dict[str, Any]) -> bool:
        """
        更新吸尘器设备状态
        
        Args:
            client: MQTT客户端对象
            payload: 状态更新负载
            
        Returns:
            bool: 更新是否成功
        """
        # 处理命令
        if "command" in payload:
            command = payload.pop("command")
            
            # 设置风扇速度
            if command in ["off", "low", "medium", "high", "max"]:
                payload["fan_speed"] = command

            # 状态控制
            elif command == "start":
                payload["state"] = "cleaning"
            elif command == "pause":
                payload["state"] = "paused"
            elif command == "stop":
                payload["state"] = "idle"
            elif command == "return_to_base":
                payload["state"] = "returning"
            elif command == "locate":
                payload["state"] = "idle"
            elif command == "clean_spot":
                payload["state"] = "cleaning"
            
        # 有一定概率发生错误
        error_rate = 0.05
        if random.random() < error_rate:
            payload["state"] = "error"
            
        # 模拟电池消耗
        if "battery_level" in self.state and self.state["state"] != "docked":
            battery_level = self.state["battery_level"]
            if battery_level > 5:
                payload["battery_level"] = battery_level - 1
                
        return super().update_state(client, payload)
        
    def update_state_mock(self) -> None:
        """模拟吸尘器状态变化"""
        # 随机电池电量变化
        if self.state["state"] not in ["docked", "returning"]:
            battery_level = self.state["battery_level"]
            if battery_level > 10:
                self.state["battery_level"] = battery_level - random.randint(1, 3)
            else:
                # 电量低时自动返回充电
                self.state["state"] = "returning" 