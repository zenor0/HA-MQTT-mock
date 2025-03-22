"""报警控制面板设备模型"""

import json
import random
from typing import Any, Dict, List, Optional

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class Alarm(MQTTDevice):
    """报警控制面板设备模型类"""

    def __init__(
        self,
        object_id: str,
        name: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        code: str = "1234",
        *args,
        **kwargs,
    ) -> None:
        """
        初始化报警控制面板设备
        
        Args:
            object_id: 设备唯一标识
            name: 设备显示名称
            code: 解除警报的安全码
        """
        super().__init__(
            component="alarm_control_panel", object_id=object_id, name=name, state=state, *args, **kwargs
        )

        # 设置默认状态
        self.state = self.state or {"state": "disarmed"}
        self.code = code

    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取报警控制面板设备的发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        payload = {
            "name": self.name,
            "unique_id": f"mock_alarm_{self.object_id}",
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "value_template": "{{ value_json.state }}",
            "code_format": "number",
            "code_arm_required": True,
            "command_template": '{ "action": "{{ action }}", "code":"{{ code }}" }',
            "supported_features": ["arm_home", "arm_away", "arm_night", "arm_custom_bypass", "trigger"],
            "payload_arm_away": "ARM_AWAY",
            "payload_arm_home": "ARM_HOME",
            "payload_arm_night": "ARM_NIGHT",
            "payload_arm_custom_bypass": "ARM_CUSTOM_BYPASS",
            "payload_disarm": "DISARM",
            "payload_trigger": "TRIGGER"
        }

        payload["device"] = generate_device_info(self.name)
        return payload

    def update_state(self, client, payload: Dict[str, Any]) -> bool:
        """
        更新报警控制面板设备状态
        
        Args:
            client: MQTT客户端对象
            payload: 状态更新负载
            
        Returns:
            bool: 更新是否成功
        """
        # 处理动作命令
        if "action" in payload:
            action = payload["action"]
            code = payload.get("code")
            
            # 处理各种警戒模式
            if action == "ARM_HOME":
                # 先转到准备状态
                payload["state"] = "arming"
                super().update_state(client, payload)
                
                # 延迟后设置为最终状态
                payload["state"] = "armed_home"
            elif action == "ARM_AWAY":
                payload["state"] = "arming"
                super().update_state(client, payload)
                
                payload["state"] = "armed_away"
            elif action == "ARM_NIGHT":
                payload["state"] = "arming"
                super().update_state(client, payload)
                
                payload["state"] = "armed_night"
            elif action == "ARM_CUSTOM_BYPASS":
                payload["state"] = "arming"
                super().update_state(client, payload)
                
                payload["state"] = "armed_custom_bypass"
            elif action == "TRIGGER":
                payload["state"] = "triggered"
            elif action == "DISARM":
                # 验证密码
                if code == self.code:
                    payload["state"] = "disarmed"
                else:
                    payload["state"] = "invalid_code"
                    # 如果是在触发状态下输入错误密码，可能会继续触发
                    if self.state.get("state") == "triggered" and random.random() < 0.7:
                        payload["state"] = "triggered"
                    return super().update_state(client, payload)
                  
        return super().update_state(client, payload)
        
    def update_state_mock(self) -> None:
        """模拟报警控制面板状态变化"""
        current_state = self.state.get("state", "disarmed")
        
        # 如果处于警戒状态，有小概率触发报警
        if current_state in ["armed_home", "armed_away", "armed_night", "armed_custom_bypass"]:
            if random.random() < 0.02:  # 2%的概率触发报警
                self.state["state"] = "triggered"
                
        # 如果处于触发状态，有小概率自动恢复到之前的警戒状态
        elif current_state == "triggered":
            if random.random() < 0.01:  # 1%的概率自动恢复
                previous_states = {
                    "armed_home": 0.25,
                    "armed_away": 0.25,
                    "armed_night": 0.25,
                    "armed_custom_bypass": 0.25
                }
                
                # 根据权重随机选择一个状态
                r = random.random()
                cumulative = 0
                for state, weight in previous_states.items():
                    cumulative += weight
                    if r <= cumulative:
                        self.state["state"] = state
                        break 