"""割草机设备模型"""

import random
from typing import Any, Dict, Optional

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class LawnMower(MQTTDevice):
    """割草机设备模型类"""

    def __init__(
        self,
        object_id: str,
        name: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        初始化割草机设备
        
        Args:
            object_id: 设备唯一标识
            name: 设备显示名称
        """
        super().__init__(
            component="lawn_mower", object_id=object_id, name=name, state=state, *args, **kwargs
        )

        # 设置默认状态
        self.state = self.state or {
            "state": "docked",
            "battery_level": 100,
            "error": ""
        }

    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取割草机设备的发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        payload = {
            "name": self.name,
            "unique_id": f"mock_lawn_mower_{self.object_id}",
            
            # 状态
            "activity_state_topic": self.state_topic,
            "activity_value_template": "{{ value_json.state }}",
            
            # 错误信息
            "problem_value_template": "{{ value_json.error }}",
            
            # 命令
            "command_topic": self.command_topic,
            "dock_command_topic": self.command_topic,
            "dock_command_template": '{"activity": "dock"}',
            "pause_command_topic": self.command_topic,
            "pause_command_template": '{"activity": "pause"}',
            "start_mowing_command_topic": self.command_topic,
            "start_mowing_command_template": '{"activity": "start_mowing"}'
        }

        payload["device"] = generate_device_info(self.name)
        return payload

    def update_state(self, client, payload: Dict[str, Any]) -> bool:
        """
        更新割草机设备状态
        
        Args:
            client: MQTT客户端对象
            payload: 状态更新负载
            
        Returns:
            bool: 更新是否成功
        """
        # 处理活动命令
        if "activity" in payload:
            if payload["activity"] == "start_mowing":
                payload["state"] = "mowing"
                payload["error"] = ""
            elif payload["activity"] == "pause":
                payload["state"] = "paused"
                payload["error"] = ""
            elif payload["activity"] == "dock":
                payload["state"] = "docked"
                payload["error"] = ""
            
            # 有一定概率出现错误
            error_rate = 0.1
            if random.random() < error_rate:
                payload["state"] = "error"
                errors = [
                    "卡住了", 
                    "电池过低", 
                    "刀片卡住", 
                    "无法回到充电站", 
                    "传感器故障"
                ]
                payload["error"] = random.choice(errors)
                
        return super().update_state(client, payload)
        
    def update_state_mock(self) -> None:
        """模拟割草机状态变化"""
        # 模拟电池电量变化
        if self.state["state"] == "mowing":
            battery_level = self.state.get("battery_level", 100)
            if battery_level > 10:
                self.state["battery_level"] = battery_level - random.randint(1, 3)
            else:
                # 电量低时自动返回充电站
                self.state["state"] = "docked"
                
        # 当设备处于充电状态时，增加电池电量
        elif self.state["state"] == "docked":
            battery_level = self.state.get("battery_level", 0)
            if battery_level < 100:
                self.state["battery_level"] = min(battery_level + random.randint(1, 5), 100)
                
        # 随机出现错误
        if self.state["state"] not in ["error", "docked"] and random.random() < 0.02:
            self.state["state"] = "error"
            errors = [
                "卡住了", 
                "电池过低", 
                "刀片卡住", 
                "无法回到充电站", 
                "传感器故障"
            ]
            self.state["error"] = random.choice(errors) 