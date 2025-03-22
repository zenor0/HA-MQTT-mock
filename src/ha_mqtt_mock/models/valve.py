"""阀门设备模型"""

import json
import random
from typing import Any, Dict, Optional

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class Valve(MQTTDevice):
    """阀门设备模型类"""

    def __init__(
        self,
        object_id: str,
        name: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        初始化阀门设备
        
        Args:
            object_id: 设备唯一标识
            name: 设备显示名称
        """
        super().__init__(
            component="valve", object_id=object_id, name=name, state=state, *args, **kwargs
        )

        # 设置默认状态
        self.state = self.state or {
            "state": "closed", 
            "position": 0,
            "current_position": 0
        }

    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取阀门设备的发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        payload = {
            "name": self.name,
            "unique_id": f"mock_valve_{self.object_id}",
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "command_template": '{"position": {{ value }}}',
            "position_topic": self.state_topic,
            "position_template": "{{ value_json.current_position }}",
            "state_topic": self.state_topic,
            "state_template": "{{ value_json.state }}",
            "reports_position": True,
            "payload_open": "OPEN",
            "payload_close": "CLOSE",
            "payload_stop": "STOP"
        }

        payload["device"] = generate_device_info(self.name)
        return payload

    def update_state(self, client, payload: Dict[str, Any]) -> bool:
        """
        更新阀门设备状态
        
        Args:
            client: MQTT客户端对象
            payload: 状态更新负载
            
        Returns:
            bool: 更新是否成功
        """
        # 处理命令
        if "position" in payload:
            position = int(payload["position"])
            payload["position"] = position
            
            # 设置目标位置
            current_position = self.state.get("current_position", 0)
            
            # 设置状态
            if position > 0:
                if position > current_position:
                    payload["state"] = "opening"
                elif position < current_position:
                    payload["state"] = "closing"
                else:
                    payload["state"] = "open"
            else:
                payload["state"] = "closed"
        
        # 处理命令
        elif "command" in payload:
            if payload["command"] == "OPEN":
                payload["state"] = "opening"
                payload["position"] = 100
            elif payload["command"] == "CLOSE":
                payload["state"] = "closing"
                payload["position"] = 0
            elif payload["command"] == "STOP":
                if self.state.get("state") == "opening":
                    payload["state"] = "open"
                elif self.state.get("state") == "closing":
                    payload["state"] = "closed"
                
        return super().update_state(client, payload)
        
    def update_state_mock(self) -> None:
        """模拟阀门状态变化"""
        # 模拟阀门位置变化
        if self.state.get("state") in ["opening", "closing"]:
            target_position = self.state.get("position", 0)
            current_position = self.state.get("current_position", 0)
            
            # 根据方向调整当前位置
            if self.state.get("state") == "opening" and current_position < target_position:
                new_position = min(current_position + random.randint(5, 10), target_position)
                self.state["current_position"] = new_position
                
                # 如果达到目标位置，更新状态
                if new_position == target_position:
                    self.state["state"] = "open"
                    
            elif self.state.get("state") == "closing" and current_position > target_position:
                new_position = max(current_position - random.randint(5, 10), target_position)
                self.state["current_position"] = new_position
                
                # 如果达到目标位置，更新状态
                if new_position == target_position:
                    self.state["state"] = "closed" 