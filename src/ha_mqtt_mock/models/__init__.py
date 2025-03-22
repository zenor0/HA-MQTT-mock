"""设备模型模块"""
from typing import List, Dict

from .base import MQTTDevice
from .light import Light
from .sensor import Sensor, BinarySensor
from .switch import Switch
from .fan import Fan
from .climate import Climate
from .humidifier import Humidifier
from .button import Button
from .lock import Lock
from .vacuum import Vacuum
from .water_heater import WaterHeater
from .valve import Valve
from .lawn_mower import LawnMower
from .cover import Cover
from .alarm import Alarm

# 导出所有模型类
__all__ = [
    'MQTTDevice',
    'Light',
    'Sensor',
    'BinarySensor',
    'Switch',
    'Fan',
    'Climate',
    'Humidifier',
    'Button',
    'Lock',
    'Vacuum',
    'WaterHeater',
    'Valve',
    'LawnMower',
    'Cover',
    'Alarm',
]
DEVICE_TYPE_MAP = {
    "light": Light,
    "sensor": Sensor,
    "binary_sensor": BinarySensor,
    "switch": Switch,
    "fan": Fan,
    "climate": Climate,
    "humidifier": Humidifier,
    "button": Button,
    "lock": Lock,
    "vacuum": Vacuum,
    "water_heater": WaterHeater,
    "valve": Valve,
    "lawn_mower": LawnMower,
    "cover": Cover,
    "alarm": Alarm,
}

"""示例设备数据生成模块"""


def create_sample_devices() -> List[Dict]:
    """
    创建示例设备配置列表（仅用于初始化空配置）
    
    Returns:
        List[Dict]: 示例设备配置列表
    """
    return [
        {
            "type": "light",
            "object_id": "rgb_light",
            "name": "客厅灯光"
        },
        {
            "type": "light",
            "object_id": "rgb_light_bedroom",
            "name": "卧室灯光"
        },
        {
            "type": "sensor",
            "object_id": "temp_sensor",
            "name": "温度传感器",
            "sensor_type": "temperature"
        },
        {
            "type": "sensor",
            "object_id": "humidity_sensor",
            "name": "湿度传感器",
            "sensor_type": "humidity"
        },
        {
            "type": "sensor",
            "object_id": "pressure_sensor",
            "name": "压力传感器",
            "sensor_type": "pressure"
        },
        {
            "type": "binary_sensor",
            "object_id": "motion_sensor",
            "name": "人体感应",
            "sensor_type": "motion"
        },
        {
            "type": "binary_sensor",
            "object_id": "door_sensor",
            "name": "门窗感应",
            "sensor_type": "door"
        }
    ] 