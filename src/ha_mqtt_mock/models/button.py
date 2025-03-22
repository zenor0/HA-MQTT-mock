"""按钮设备模型"""

import json
from typing import Any, Dict, Optional

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class Button(MQTTDevice):
    """按钮设备模型类"""

    def __init__(
        self,
        object_id: str,
        name: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        初始化按钮设备
        
        Args:
            object_id: 设备唯一标识
            name: 设备显示名称
        """
        super().__init__(
            component="button", object_id=object_id, name=name, state=state, *args, **kwargs
        )

    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取按钮设备的发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        payload = {
            "name": self.name,
            "unique_id": f"mock_button_{self.object_id}",
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "payload_press": "PRESS",
        }

        payload["device"] = generate_device_info(self.name)
        return payload 