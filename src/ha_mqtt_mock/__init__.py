"""
Home Assistant MQTT模拟器

这个包提供了用于模拟各种Home Assistant MQTT设备的功能
"""

__version__ = "0.2.0"

from .cli import run, main
from .engine import DeviceConfig, MockDeviceManager, create_mqtt_client, setup_mqtt_client, disconnect_mqtt_client
from .engine import AppService
from .models import MQTTDevice, Light, Sensor, BinarySensor, Switch, Fan, Climate, Humidifier, Button, Lock, Vacuum, WaterHeater, Valve, LawnMower, Cover, Alarm
from .models import create_sample_devices

