"""热水器设备模型"""

import json
import random
from typing import Any, Dict, List, Optional

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class WaterHeater(MQTTDevice):
    """热水器设备模型类"""

    def __init__(
        self,
        object_id: str,
        name: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        初始化热水器设备
        
        Args:
            object_id: 设备唯一标识
            name: 设备显示名称
        """
        super().__init__(
            component="water_heater", object_id=object_id, name=name, state=state, *args, **kwargs
        )

        # 设置默认状态
        self.state = self.state or {
            "state": "OFF", 
            "mode": "eco", 
            "temperature": 50, 
            "current_temperature": 25
        }
        
        # 可用模式
        self.modes = ["eco", "performance", "away", "boost"]

    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取热水器设备的发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        payload = {
            "name": self.name,
            "unique_id": f"mock_water_heater_{self.object_id}",
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            
            # 电源状态
            "power_command_template": '{"state": "{{ value }}"}',
            "payload_on": "ON",
            "payload_off": "OFF",
            
            # 模式设置
            "mode_state_topic": self.state_topic,
            "mode_state_template": "{{ value_json.mode }}",
            "mode_command_topic": self.command_topic,
            "mode_command_template": '{"mode": "{{ value }}"}',
            "modes": self.modes,
            
            # 温度设置
            "temperature_state_topic": self.state_topic,
            "temperature_state_template": "{{ value_json.temperature }}",
            "temperature_command_topic": self.command_topic,
            "temperature_command_template": '{"temperature": {{ value }} }',
            "current_temperature_topic": self.state_topic,
            "current_temperature_template": "{{ value_json.current_temperature }}",
            
            # 温度范围
            "min_temp": 30,
            "max_temp": 80,
            "precision": 0.5,
        }

        payload["device"] = generate_device_info(self.name)
        return payload
        
    def update_state_mock(self) -> None:
        """模拟热水器状态变化"""
        # 只有当设备开启时才模拟温度变化
        if self.state.get("state") == "ON":
            target_temp = self.state.get("temperature", 50)
            current_temp = self.state.get("current_temperature", 25)
            
            # 模拟加热过程
            if current_temp < target_temp:
                # 根据不同模式有不同的加热速度
                heating_rate = 0.5  # 默认加热速率
                
                if self.state.get("mode") == "boost":
                    heating_rate = 1.5
                elif self.state.get("mode") == "eco":
                    heating_rate = 0.3
                
                new_temp = min(current_temp + heating_rate, target_temp)
                self.state["current_temperature"] = round(new_temp, 1)
            
            # 模拟热损失
            elif current_temp > target_temp + 0.5:
                self.state["current_temperature"] = round(current_temp - 0.2, 1) 