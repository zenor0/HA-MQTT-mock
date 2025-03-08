import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class MQTTConfig:
    broker_address: str = os.environ.get("MQTT_BROKER_ADDRESS", "localhost")
    broker_port: int = int(os.environ.get("MQTT_BROKER_PORT", "1883"))
    username: Optional[str] = os.environ.get("MQTT_USERNAME", None)
    password: Optional[str] = os.environ.get("MQTT_PASSWORD", None)
    client_id: str = os.environ.get("MQTT_CLIENT_ID", "mock_device_client")
    root_prefix: str = os.environ.get("MQTT_ROOT_PREFIX", "homeassistant")
    
    def __post_init__(self):
        """验证配置"""
        if not self.broker_address:
            raise ValueError("MQTT Broker地址不能为空")
        
        if not isinstance(self.broker_port, int) or self.broker_port <= 0:
            raise ValueError(f"无效的MQTT端口号: {self.broker_port}")
            
        # 如果提供了用户名但没有密码，发出警告
        if self.username and not self.password:
            import warnings
            warnings.warn("提供了MQTT用户名但没有密码")

# 默认配置实例
config = MQTTConfig() 