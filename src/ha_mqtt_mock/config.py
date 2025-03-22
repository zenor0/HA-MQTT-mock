"""MQTT配置模块"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

from dotenv import load_dotenv

import logging

logger = logging.getLogger(__name__)

# 首先尝试从当前目录加载.env文件
if Path('.env').exists():
    load_dotenv()
# 然后尝试从项目根目录加载.env文件
elif Path(Path.cwd().parent / '.env').exists():
    load_dotenv(Path.cwd().parent / '.env')
# 最后尝试从环境变量指定的配置文件加载
elif os.environ.get('ENV_FILE') and Path(os.environ.get('ENV_FILE')).exists():
    load_dotenv(os.environ.get('ENV_FILE'))

class Singleton(type):
    """单例元类"""
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

@dataclass
class MQTTConfig(metaclass=Singleton):
    """MQTT配置类（单例模式）"""
    broker_address: str = field(default_factory=lambda: os.environ.get("MQTT_BROKER_ADDRESS", "localhost"))
    broker_port: int = field(default_factory=lambda: int(os.environ.get("MQTT_BROKER_PORT", "1883")))
    username: Optional[str] = field(default_factory=lambda: os.environ.get("MQTT_USERNAME", None))
    password: Optional[str] = field(default_factory=lambda: os.environ.get("MQTT_PASSWORD", None))
    client_id: str = field(default_factory=lambda: os.environ.get("MQTT_CLIENT_ID", "mock_device_client"))
    root_prefix: str = field(default_factory=lambda: os.environ.get("MQTT_ROOT_PREFIX", "homeassistant"))
    
    def __post_init__(self):
        """验证配置"""
        logger.debug(f"MQTT配置: {self}")
        if not self.broker_address:
            raise ValueError("MQTT Broker地址不能为空")
        
        if not isinstance(self.broker_port, int) or self.broker_port <= 0:
            raise ValueError(f"无效的MQTT端口号: {self.broker_port}")
            
        # 如果提供了用户名但没有密码，发出警告
        if self.username and not self.password:
            import warnings
            warnings.warn("提供了MQTT用户名但没有密码")
    
    @classmethod
    def get_instance(cls) -> 'MQTTConfig':
        """
        获取配置实例
        
        Returns:
            MQTTConfig: 配置实例
        """
        return cls()
    
    def update(self, **kwargs):
        """
        更新配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # 更新后重新验证
        self.__post_init__()

# 创建默认配置实例
def create_default_config() -> MQTTConfig:
    """
    创建默认MQTT配置实例
    
    Returns:
        MQTTConfig: 默认配置实例
    """
    return MQTTConfig() 