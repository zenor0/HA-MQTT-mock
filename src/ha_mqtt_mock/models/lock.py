"""锁设备模型"""

import json
import random
from typing import Any, Dict, Optional

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class Lock(MQTTDevice):
    """锁设备模型类"""

    def __init__(
        self,
        object_id: str,
        name: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        初始化锁设备
        
        Args:
            object_id: 设备唯一标识
            name: 设备显示名称
        """
        super().__init__(
            component="lock", object_id=object_id, name=name, state=state, *args, **kwargs
        )

        # 设置默认状态
        self.state = self.state or {"state": "LOCKED"}

    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取锁设备的发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        payload = {
            "name": self.name,
            "unique_id": f"mock_lock_{self.object_id}",
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "command_template": '{ "action": "{{ value }}", "code":"{{ code }}" }',
            "payload_lock": "LOCK",
            "payload_unlock": "UNLOCK",
            "state_locked": "LOCKED",
            "state_unlocked": "UNLOCKED",
            "state_locking": "LOCKING",
            "state_unlocking": "UNLOCKING",
            "state_jammed": "JAMMED",
            "value_template": "{{ value_json.state }}",
        }

        payload["device"] = generate_device_info(self.name)
        return payload

    def update_state(self, client, payload: Dict[str, Any]) -> bool:
        """
        更新锁设备状态
        
        Args:
            client: MQTT客户端对象
            payload: 状态更新负载
            
        Returns:
            bool: 更新是否成功
        """
        # 处理动作命令
        if "action" in payload:
            if payload["action"] == "LOCK":
                payload["state"] = "LOCKED"
            elif payload["action"] == "UNLOCK":
                payload["state"] = "UNLOCKED"
            
            # 有一定概率会卡住
            jammed_rate = 0.1
            if payload["action"] in ["LOCK", "UNLOCK"] and random.random() < jammed_rate:
                payload["state"] = "JAMMED"
                
        return super().update_state(client, payload) 