"""设备模型测试"""

import json
import pytest
from unittest.mock import MagicMock, patch

from ha_mqtt_mock.models import MQTTDevice, Light, Sensor, BinarySensor

class TestDevice(MQTTDevice):
    """用于测试的设备类"""
    
    def __init__(self, object_id="test_device", name=None):
        super().__init__(component="test", object_id=object_id, name=name)
        self.state = {"state": "OFF"}
    
    def _get_discovery_payload(self):
        return {
            "name": self.name,
            "unique_id": f"test_{self.object_id}",
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
        }

def test_mqtt_device_init():
    """测试MQTT设备初始化"""
    device = TestDevice(object_id="test1", name="Test Device")
    
    assert device.component == "test"
    assert device.object_id == "test1"
    assert device.name == "Test Device"
    assert device.state == {"state": "OFF"}
    assert device.base_topic == "homeassistant/test/test1"
    assert device.state_topic == "homeassistant/test/test1/state"
    assert device.command_topic == "homeassistant/test/test1/set"

def test_mqtt_device_publish_state():
    """测试MQTT设备状态发布"""
    device = TestDevice()
    mock_client = MagicMock()
    
    # 模拟publish方法返回值
    mock_result = MagicMock()
    mock_result.rc = 0
    mock_client.publish.return_value = mock_result
    
    # 发布状态
    result = device.publish_state(mock_client)
    
    # 验证结果
    assert result is True
    mock_client.publish.assert_called_once_with(
        device.state_topic,
        json.dumps(device.state),
        retain=False
    )

def test_light_device():
    """测试灯光设备"""
    light = Light(object_id="test_light", name="Test Light")
    
    # 验证初始状态
    assert light.component == "light"
    assert light.object_id == "test_light"
    assert light.name == "Test Light"
    assert light.state["state"] == "OFF"
    assert light.state["brightness"] == 255
    assert light.state["color_mode"] == "rgb"
    
    # 验证发现负载
    payload = light._get_discovery_payload()
    assert payload["name"] == "Test Light"
    assert payload["schema"] == "json"
    assert payload["brightness"] is True
    assert payload["effect"] is True
    assert "rainbow" in payload["effect_list"]

def test_sensor_device():
    """测试传感器设备"""
    sensor = Sensor(object_id="test_temp", name="Test Temperature", sensor_type="temperature")
    
    # 验证初始状态
    assert sensor.component == "sensor"
    assert sensor.object_id == "test_temp"
    assert sensor.name == "Test Temperature"
    assert "temperature" in sensor.state
    
    # 验证发现负载
    payload = sensor._get_discovery_payload()
    assert payload["name"] == "Test Temperature"
    assert payload["device_class"] == "temperature"
    assert payload["unit_of_measurement"] == "°C"

def test_binary_sensor_device():
    """测试二元传感器设备"""
    sensor = BinarySensor(object_id="test_motion", name="Test Motion", sensor_type="motion")
    
    # 验证初始状态
    assert sensor.component == "binary_sensor"
    assert sensor.object_id == "test_motion"
    assert sensor.name == "Test Motion"
    assert sensor.state["state"] == "clear"  # motion传感器的默认状态是clear
    
    # 验证发现负载
    payload = sensor._get_discovery_payload()
    assert payload["name"] == "Test Motion"
    assert payload["device_class"] == "motion"
    assert payload["payload_on"] == "motion"
    assert payload["payload_off"] == "clear" 