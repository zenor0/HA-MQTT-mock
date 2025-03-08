"""配置模块测试"""

import os
import pytest
from ha_mqtt_mock.config import MQTTConfig

def test_mqtt_config_defaults():
    """测试MQTT配置默认值"""
    config = MQTTConfig()
    assert config.broker_address == "localhost"
    assert config.broker_port == 1883
    assert config.username is None
    assert config.password is None
    assert config.client_id == "mock_device_client"
    assert config.root_prefix == "homeassistant"

def test_mqtt_config_env_vars():
    """测试MQTT配置环境变量"""
    # 设置环境变量
    os.environ["MQTT_BROKER_ADDRESS"] = "test.mosquitto.org"
    os.environ["MQTT_BROKER_PORT"] = "1884"
    os.environ["MQTT_USERNAME"] = "testuser"
    os.environ["MQTT_PASSWORD"] = "testpass"
    os.environ["MQTT_CLIENT_ID"] = "test_client"
    os.environ["MQTT_ROOT_PREFIX"] = "test_prefix"
    
    # 创建配置
    config = MQTTConfig()
    
    # 验证配置
    assert config.broker_address == "test.mosquitto.org"
    assert config.broker_port == 1884
    assert config.username == "testuser"
    assert config.password == "testpass"
    assert config.client_id == "test_client"
    assert config.root_prefix == "test_prefix"
    
    # 清理环境变量
    for var in ["MQTT_BROKER_ADDRESS", "MQTT_BROKER_PORT", "MQTT_USERNAME", 
                "MQTT_PASSWORD", "MQTT_CLIENT_ID", "MQTT_ROOT_PREFIX"]:
        os.environ.pop(var, None)

def test_mqtt_config_validation():
    """测试MQTT配置验证"""
    # 测试无效的端口
    with pytest.raises(ValueError):
        MQTTConfig(broker_port=-1)
    
    # 测试空地址
    with pytest.raises(ValueError):
        MQTTConfig(broker_address="") 