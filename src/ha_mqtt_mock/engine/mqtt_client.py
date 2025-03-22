"""MQTT客户端相关功能模块"""

import logging
from typing import Callable

import paho.mqtt.client as mqtt

from ha_mqtt_mock.config import MQTTConfig

logger = logging.getLogger(__name__)

def create_mqtt_client(mqtt_config: MQTTConfig) -> mqtt.Client:
    """
    创建MQTT客户端
    
    Args:
        mqtt_config: MQTT配置
        
    Returns:
        mqtt.Client: MQTT客户端实例
    """
    # 创建客户端
    client = mqtt.Client(client_id=mqtt_config.client_id)
    
    # 设置用户名和密码（如果提供）
    if mqtt_config.username:
        client.username_pw_set(username=mqtt_config.username, password=mqtt_config.password)
    
    # 连接回调
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"已连接到MQTT Broker: {mqtt_config.broker_address}:{mqtt_config.broker_port}")
        else:
            logger.error(f"连接MQTT Broker失败，返回码: {rc}")
    
    client.on_connect = on_connect
    
    return client

def setup_mqtt_client(mqtt_client: mqtt.Client, mqtt_config: MQTTConfig, 
                    on_message_callback: Callable) -> None:
    """
    设置MQTT客户端连接和回调
    
    Args:
        mqtt_client: MQTT客户端实例
        mqtt_config: MQTT配置
        on_message_callback: 消息回调函数
    """
    # 设置消息回调
    mqtt_client.on_message = on_message_callback
    
    # 连接MQTT代理
    mqtt_client.connect(mqtt_config.broker_address, mqtt_config.broker_port)
    
    # 启动MQTT循环
    mqtt_client.loop_start()

def disconnect_mqtt_client(mqtt_client: mqtt.Client) -> None:
    """
    断开MQTT客户端连接
    
    Args:
        mqtt_client: MQTT客户端实例
    """
    if mqtt_client._thread_terminate:
        return
        
    logger.debug("正在断开MQTT连接...")
    mqtt_client.disconnect()
    mqtt_client.loop_stop() 