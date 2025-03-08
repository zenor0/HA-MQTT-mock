"""灯光设备模型"""

import random
from typing import Any, Dict, List, Optional

from ..utils.mqtt_helpers import generate_device_info
from .base import MQTTDevice

class Light(MQTTDevice):
    """灯光设备模型类"""
    
    def __init__(self, object_id: str, name: Optional[str] = None, 
                 effects: Optional[List[str]] = None) -> None:
        """
        初始化灯光设备
        
        Args:
            object_id: 设备唯一标识
            name: 设备显示名称
            effects: 灯光效果列表
        """
        super().__init__(component="light", object_id=object_id, name=name)
        
        # 设置默认效果列表
        self.effects = effects or ["rainbow", "colorloop", "night", "relax", "concentrate"]
        
        # 设置默认状态
        self.state = {
            "state": "OFF",
            "brightness": 255,
            "color_mode": "rgb",
            "color": {"r": 255, "g": 255, "b": 255},
            "effect": "none",
        }
    
    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取灯光设备的发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        return {
            "schema": "json",
            "name": self.name,
            "unique_id": f"mock_light_{self.object_id}",
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "brightness": True,
            "color_mode": True,
            "supported_color_modes": ["rgb"],
            "effect": True,
            "effect_list": self.effects,
            "optimistic": False,
            "qos": 0,
            "device": generate_device_info(self.name)
        }
    
    def update_state_mock(self) -> None:
        """模拟灯光状态变化"""
        # 随机切换状态
        if random.random() < 0.1:
            self.state["state"] = "ON" if self.state["state"] == "OFF" else "OFF"
        
        # 如果灯是开的，随机调整亮度和颜色
        if self.state["state"] == "ON":
            # 30%概率改变亮度
            if random.random() < 0.3:
                self.state["brightness"] = random.randint(10, 255)
            
            # 20%概率改变颜色
            if random.random() < 0.2:
                self.state["color"] = {
                    "r": random.randint(0, 255),
                    "g": random.randint(0, 255),
                    "b": random.randint(0, 255)
                }
            
            # 10%概率改变效果
            if random.random() < 0.1 and self.effects:
                self.state["effect"] = random.choice(self.effects) 