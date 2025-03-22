"""窗帘/卷帘设备模型"""

import random
from typing import Any, Dict, Optional

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class Cover(MQTTDevice):
    """窗帘/卷帘设备模型类"""

    def __init__(
        self,
        object_id: str,
        name: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        has_tilt: bool = True,
        *args,
        **kwargs,
    ) -> None:
        """
        初始化窗帘/卷帘设备
        
        Args:
            object_id: 设备唯一标识
            name: 设备显示名称
            has_tilt: 是否支持倾斜控制
        """
        super().__init__(
            component="cover", object_id=object_id, name=name, state=state, *args, **kwargs
        )

        # 设置默认状态
        self.state = self.state or {
            "state": "closed",
            "position": 0,
            "current_position": 0,
            "tilt": 0
        }
        
        self.has_tilt = has_tilt

    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取窗帘/卷帘设备的发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        payload = {
            "name": self.name,
            "unique_id": f"mock_cover_{self.object_id}",
            "state_topic": self.state_topic,
            "state_template": "{{ value_json.state }}",
            "command_topic": self.command_topic,
            "command_template": '{"action": "{{ value }}"}',
            
            # 位置控制
            "position_topic": self.state_topic,
            "position_template": "{{ value_json.current_position }}",
            "set_position_topic": self.command_topic,
            "set_position_template": '{"position": {{ value }}}',
            
            # 打开/关闭/停止命令
            "payload_open": "OPEN",
            "payload_close": "CLOSE",
            "payload_stop": "STOP"
        }
        
        # 如果支持倾斜控制，添加相关配置
        if self.has_tilt:
            payload.update({
                "tilt_command_topic": self.command_topic,
                "tilt_command_template": '{"tilt": {{ value }}}',
                "tilt_status_topic": self.state_topic,
                "tilt_status_template": "{{ value_json.tilt }}"
            })

        payload["device"] = generate_device_info(self.name)
        return payload

    def update_state(self, client, payload: Dict[str, Any]) -> bool:
        """
        更新窗帘/卷帘设备状态
        
        Args:
            client: MQTT客户端对象
            payload: 状态更新负载
            
        Returns:
            bool: 更新是否成功
        """
        # 处理位置命令
        if "position" in payload:
            position = int(payload["position"])
            payload["position"] = position
            current_position = self.state.get("current_position", 0)
            
            # 设置状态
            if position > current_position:
                payload["state"] = "opening"
            elif position < current_position:
                payload["state"] = "closing"
            else:
                payload["state"] = "open" if position > 0 else "closed"
                
        # 处理动作命令
        elif "action" in payload:
            if payload["action"] == "OPEN":
                payload["state"] = "opening"
                payload["position"] = 100
            elif payload["action"] == "CLOSE":
                payload["state"] = "closing"
                payload["position"] = 0
            elif payload["action"] == "STOP":
                # 停止当前动作，保持当前位置
                if self.state.get("state") in ["opening", "closing"]:
                    current_position = self.state.get("current_position", 0)
                    payload["state"] = "open" if current_position > 0 else "closed"
                    payload["position"] = current_position
                    
        # 处理倾斜命令
        elif "tilt" in payload and self.has_tilt:
            tilt = int(payload["tilt"])
            payload["tilt"] = max(0, min(100, tilt))  # 确保在0-100范围内
                
        return super().update_state(client, payload)
        
    def update_state_mock(self) -> None:
        """模拟窗帘/卷帘状态变化"""
        # 模拟位置变化
        if self.state.get("state") in ["opening", "closing"]:
            target_position = self.state.get("position", 0)
            current_position = self.state.get("current_position", 0)
            
            # 根据方向调整当前位置
            if self.state.get("state") == "opening" and current_position < target_position:
                new_position = min(current_position + random.randint(5, 15), target_position)
                self.state["current_position"] = new_position
                
                # 如果达到目标位置，更新状态
                if new_position == target_position:
                    self.state["state"] = "open" if new_position > 0 else "closed"
                    
            elif self.state.get("state") == "closing" and current_position > target_position:
                new_position = max(current_position - random.randint(5, 15), target_position)
                self.state["current_position"] = new_position
                
                # 如果达到目标位置，更新状态
                if new_position == target_position:
                    self.state["state"] = "open" if new_position > 0 else "closed" 