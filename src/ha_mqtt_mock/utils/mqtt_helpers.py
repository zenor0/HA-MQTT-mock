import json
import logging
from typing import Any, Dict, Optional

from ..config import config

logger = logging.getLogger(__name__)

def publish_discovery(client, component: str, object_id: str, payload: Dict[str, Any], retain: bool = True) -> None:
    """
    发布MQTT设备发现信息到Home Assistant
    
    Args:
        client: MQTT客户端对象
        component: 组件类型（如light, sensor等）
        object_id: 设备唯一标识
        payload: 发现信息负载
        retain: 是否保留消息
    """
    topic = f"{config.root_prefix}/{component}/{object_id}/config"
    try:
        result = client.publish(
            topic,
            json.dumps(payload),
            retain=retain,
        )
        if result.rc != 0:
            logger.error(f"发布发现信息失败: {result.rc}，主题: {topic}")
        else:
            logger.debug(f"成功发布发现信息到主题: {topic}")
    except Exception as e:
        logger.exception(f"发布发现信息时发生错误: {e}")

def publish_state(client, topic: str, state: Dict[str, Any], retain: bool = False) -> bool:
    """
    发布设备状态信息
    
    Args:
        client: MQTT客户端对象
        topic: MQTT主题
        state: 状态信息字典
        retain: 是否保留消息
        
    Returns:
        bool: 发布是否成功
    """
    try:
        result = client.publish(
            topic,
            json.dumps(state),
            retain=retain,
        )
        if result.rc != 0:
            logger.error(f"发布状态信息失败: {result.rc}，主题: {topic}")
            return False
        else:
            logger.debug(f"成功发布状态到主题: {topic}")
            return True
    except Exception as e:
        logger.exception(f"发布状态信息时发生错误: {e}")
        return False

def generate_device_info(name: str, manufacturer: str = "zenor0's Corp", model: str = "Mock Device", sw_version: str = "1.0.0") -> Dict[str, str]:
    """
    生成设备信息字典
    
    Args:
        name: 设备名称
        manufacturer: 制造商
        model: 设备型号
        sw_version: 软件版本
        
    Returns:
        Dict[str, str]: 设备信息字典
    """
    return {
        "name": name,
        "identifiers": f"zenor0_mock_{name.lower().replace(' ', '_')}",
        "manufacturer": manufacturer,
        "model": model,
        "sw_version": sw_version,
    } 