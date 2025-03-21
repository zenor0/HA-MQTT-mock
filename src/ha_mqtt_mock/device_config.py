"""设备配置管理模块

该模块负责从JSON文件加载和保存设备配置
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type

from .models.base import MQTTDevice
from .models import Light, Sensor, BinarySensor

logger = logging.getLogger(__name__)

# 设备类型映射
DEVICE_TYPE_MAP = {
    "light": Light,
    "sensor": Sensor,
    "binary_sensor": BinarySensor,
}

class DeviceConfig:
    """设备配置管理类"""
    
    def __init__(self, config_file: Union[str, Path] = "devices.json") -> None:
        """
        初始化设备配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self.devices_data: List[Dict[str, Any]] = []
        
    def load(self) -> List[Dict[str, Any]]:
        """
        从配置文件加载设备列表
        
        Returns:
            List[Dict[str, Any]]: 设备配置数据列表
        """
        if not self.config_file.exists():
            logger.warning(f"配置文件 {self.config_file} 不存在，将创建空配置")
            self.devices_data = []
            return self.devices_data
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.devices_data = json.load(f)
            logger.info(f"从 {self.config_file} 加载了 {len(self.devices_data)} 个设备配置")
            return self.devices_data
        except json.JSONDecodeError:
            logger.error(f"配置文件 {self.config_file} 格式无效")
            self.devices_data = []
            return self.devices_data
        except Exception as e:
            logger.exception(f"加载配置文件时发生错误: {e}")
            self.devices_data = []
            return self.devices_data
    
    def save(self, devices_data: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        保存设备配置到文件
        
        Args:
            devices_data: 要保存的设备配置数据，若不提供则使用当前加载的数据
            
        Returns:
            bool: 保存是否成功
        """
        if devices_data is not None:
            self.devices_data = devices_data
        
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.devices_data, f, ensure_ascii=False, indent=2)
            logger.info(f"保存了 {len(self.devices_data)} 个设备配置到 {self.config_file}")
            return True
        except Exception as e:
            logger.exception(f"保存配置文件时发生错误: {e}")
            return False
    
    def create_devices(self) -> List[MQTTDevice]:
        """
        根据配置创建设备实例
        
        Returns:
            List[MQTTDevice]: 设备实例列表
        """
        devices = []
        
        for device_data in self.devices_data:
            device_type = device_data.get("type")
            if device_type not in DEVICE_TYPE_MAP:
                logger.warning(f"未知设备类型 '{device_type}'，跳过")
                continue
            
            # 获取设备类
            device_class = DEVICE_TYPE_MAP[device_type]
            
            # 提取设备参数
            device_params = {k: v for k, v in device_data.items() if k not in ["type"]}
            
            try:
                # 创建设备实例
                device = device_class(**device_params)
                devices.append(device)
                logger.debug(f"创建了设备 '{device.name}' (ID: {device.object_id})")
            except Exception as e:
                logger.exception(f"创建设备失败: {e}, 设备数据: {device_data}")
        
        logger.info(f"共创建了 {len(devices)} 个设备实例")
        return devices
    
    def add_device(self, device_data: Dict[str, Any]) -> bool:
        """
        添加设备配置
        
        Args:
            device_data: 设备配置数据
            
        Returns:
            bool: 添加是否成功
        """
        # 验证设备数据
        if "type" not in device_data or "object_id" not in device_data:
            logger.error("设备数据缺少必需字段 'type' 或 'object_id'")
            return False
        
        # 检查设备类型是否有效
        if device_data["type"] not in DEVICE_TYPE_MAP:
            logger.error(f"未知设备类型 '{device_data['type']}'")
            return False
        
        # 检查ID是否已存在
        object_id = device_data["object_id"]
        for existing_device in self.devices_data:
            if existing_device.get("object_id") == object_id:
                logger.warning(f"设备ID '{object_id}' 已存在，更新现有设备")
                existing_device.update(device_data)
                return self.save()
        
        # 添加新设备
        self.devices_data.append(device_data)
        return self.save()
    
    def update_device(self, object_id: str, device_data: Dict[str, Any]) -> bool:
        """
        更新设备配置
        
        Args:
            object_id: 设备对象ID
            device_data: 更新后的设备配置数据
            
        Returns:
            bool: 更新是否成功
        """
        for i, device in enumerate(self.devices_data):
            if device.get("object_id") == object_id:
                # 保留原始类型，除非显式提供
                if "type" not in device_data:
                    device_data["type"] = device.get("type")
                
                # 更新设备数据
                self.devices_data[i] = device_data
                logger.info(f"更新了设备 ID: {object_id}")
                return self.save()
        
        logger.warning(f"未找到要更新的设备: {object_id}")
        return False
    
    def remove_device(self, object_id: str) -> bool:
        """
        移除设备配置
        
        Args:
            object_id: 设备对象ID
            
        Returns:
            bool: 移除是否成功
        """
        for i, device in enumerate(self.devices_data):
            if device.get("object_id") == object_id:
                self.devices_data.pop(i)
                logger.info(f"移除了设备 ID: {object_id}")
                return self.save()
        
        logger.warning(f"未找到要移除的设备: {object_id}")
        return False
    
    def get_device(self, object_id: str) -> Optional[Dict[str, Any]]:
        """
        获取设备配置
        
        Args:
            object_id: 设备对象ID
            
        Returns:
            Optional[Dict[str, Any]]: 设备配置数据，如果未找到则返回None
        """
        for device in self.devices_data:
            if device.get("object_id") == object_id:
                return device
        return None
    
    def get_all_devices(self) -> List[Dict[str, Any]]:
        """
        获取所有设备配置
        
        Returns:
            List[Dict[str, Any]]: 所有设备配置数据
        """
        return self.devices_data 