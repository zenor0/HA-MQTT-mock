"""传感器设备模型"""

import random
from typing import Any, Dict, Optional

from ..utils.mqtt_helpers import generate_device_info
from .base import MQTTDevice

class Sensor(MQTTDevice):
    """传感器设备模型类"""
    
    # 传感器类型
    SENSOR_TYPES = {
        "temperature": {
            "device_class": "temperature",
            "unit_of_measurement": "°C",
            "value_template": "{{ value_json.temperature }}",
            "state_class": "measurement",
            "mock_min": 18,
            "mock_max": 30,
            "mock_step": 0.5,
        },
        "humidity": {
            "device_class": "humidity",
            "unit_of_measurement": "%",
            "value_template": "{{ value_json.humidity }}",
            "state_class": "measurement",
            "mock_min": 30,
            "mock_max": 90,
            "mock_step": 1,
        },
        "pressure": {
            "device_class": "pressure",
            "unit_of_measurement": "hPa",
            "value_template": "{{ value_json.pressure }}",
            "state_class": "measurement",
            "mock_min": 980,
            "mock_max": 1020,
            "mock_step": 0.5,
        },
        "illuminance": {
            "device_class": "illuminance",
            "unit_of_measurement": "lx",
            "value_template": "{{ value_json.illuminance }}",
            "state_class": "measurement",
            "mock_min": 0,
            "mock_max": 10000,
            "mock_step": 50,
        },
        "co2": {
            "device_class": "carbon_dioxide",
            "unit_of_measurement": "ppm",
            "value_template": "{{ value_json.co2 }}",
            "state_class": "measurement",
            "mock_min": 400,
            "mock_max": 1500,
            "mock_step": 10,
        },
        "pm25": {
            "device_class": "pm25",
            "unit_of_measurement": "µg/m³",
            "value_template": "{{ value_json.pm25 }}",
            "state_class": "measurement",
            "mock_min": 0,
            "mock_max": 100,
            "mock_step": 1,
        },
        "pm10": {
            "device_class": "pm10",
            "unit_of_measurement": "µg/m³",
            "value_template": "{{ value_json.pm10 }}",
            "state_class": "measurement",
            "mock_min": 0,
            "mock_max": 150,
            "mock_step": 1,
        },
    }
    
    def __init__(self, object_id: str, name: Optional[str] = None, 
                 sensor_type: str = "temperature") -> None:
        """
        初始化传感器设备
        
        Args:
            object_id: 设备唯一标识
            name: 设备显示名称
            sensor_type: 传感器类型
        """
        super().__init__(component="sensor", object_id=object_id, name=name)
        
        # 设置传感器类型
        if sensor_type not in self.SENSOR_TYPES:
            raise ValueError(f"不支持的传感器类型: {sensor_type}")
        
        self.sensor_type = sensor_type
        self.sensor_config = self.SENSOR_TYPES[sensor_type]
        
        # 设置默认状态
        self.state = {
            self.sensor_type: self._get_random_value()
        }
    
    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取传感器设备的发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        payload = {
            "name": self.name,
            "unique_id": f"mock_sensor_{self.object_id}",
            "state_topic": self.state_topic,
            "device_class": self.sensor_config["device_class"],
            "unit_of_measurement": self.sensor_config["unit_of_measurement"],
            "value_template": self.sensor_config["value_template"],
            "state_class": self.sensor_config["state_class"],
            "device": generate_device_info(self.name)
        }
        return payload
    
    def _get_random_value(self) -> float:
        """
        生成随机传感器值
        
        Returns:
            float: 随机传感器值
        """
        min_value = self.sensor_config["mock_min"]
        max_value = self.sensor_config["mock_max"]
        step = self.sensor_config["mock_step"]
        
        # 生成范围内的随机值
        steps = int((max_value - min_value) / step)
        return min_value + random.randint(0, steps) * step
    
    def update_state_mock(self) -> None:
        """
        模拟传感器状态变化，生成趋势性变化的数据
        """
        current_value = self.state[self.sensor_type]
        step = self.sensor_config["mock_step"]
        min_value = self.sensor_config["mock_min"]
        max_value = self.sensor_config["mock_max"]
        
        # 80%可能性按小步改变，20%可能性大幅变化
        if random.random() < 0.8:
            # 小步改变，-1步到+1步
            change = random.uniform(-step, step)
        else:
            # 大幅变化，-5步到+5步
            change = random.uniform(-5 * step, 5 * step)
        
        # 计算新值并限制在范围内
        new_value = current_value + change
        new_value = max(min_value, min(max_value, new_value))
        
        # 更新状态
        self.state[self.sensor_type] = round(new_value, 2)

class BinarySensor(MQTTDevice):
    """二元传感器设备模型类"""
    
    # 二元传感器类型
    SENSOR_TYPES = {
        "motion": {
            "device_class": "motion",
            "payload_on": "motion",
            "payload_off": "clear",
        },
        "door": {
            "device_class": "door",
            "payload_on": "open",
            "payload_off": "closed",
        },
        "window": {
            "device_class": "window",
            "payload_on": "open",
            "payload_off": "closed",
        },
        "smoke": {
            "device_class": "smoke",
            "payload_on": "detected",
            "payload_off": "clear",
        },
    }
    
    def __init__(self, object_id: str, name: Optional[str] = None, 
                 sensor_type: str = "motion") -> None:
        """
        初始化二元传感器设备
        
        Args:
            object_id: 设备唯一标识
            name: 设备显示名称
            sensor_type: 传感器类型
        """
        super().__init__(component="binary_sensor", object_id=object_id, name=name)
        
        # 设置传感器类型
        if sensor_type not in self.SENSOR_TYPES:
            raise ValueError(f"不支持的二元传感器类型: {sensor_type}")
        
        self.sensor_type = sensor_type
        self.sensor_config = self.SENSOR_TYPES[sensor_type]
        
        # 设置默认状态
        self.state = {
            "state": self.sensor_config["payload_off"]
        }
    
    def _get_discovery_payload(self) -> Dict[str, Any]:
        """
        获取二元传感器设备的发现信息负载
        
        Returns:
            Dict[str, Any]: 发现信息负载字典
        """
        payload = {
            "name": self.name,
            "unique_id": f"mock_binary_sensor_{self.object_id}",
            "state_topic": self.state_topic,
            "device_class": self.sensor_config["device_class"],
            "payload_on": self.sensor_config["payload_on"],
            "payload_off": self.sensor_config["payload_off"],
            "value_template": "{{ value_json.state }}",
            "device": generate_device_info(self.name)
        }
        return payload
    
    def update_state_mock(self) -> None:
        """模拟二元传感器状态变化"""
        # 有10%概率改变状态
        if random.random() < 0.1:
            current_state = self.state["state"]
            if current_state == self.sensor_config["payload_off"]:
                self.state["state"] = self.sensor_config["payload_on"]
            else:
                self.state["state"] = self.sensor_config["payload_off"] 