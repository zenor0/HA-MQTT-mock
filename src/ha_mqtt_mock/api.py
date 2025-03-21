"""FastAPI 应用程序模块，提供设备管理API"""

import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException, Path, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .device_config import DeviceConfig
from .mock import MockDeviceManager

logger = logging.getLogger(__name__)

# API 模型定义
class DeviceBase(BaseModel):
    """设备基础数据模型"""
    type: str = Field(..., description="设备类型，如light、sensor、binary_sensor")
    object_id: str = Field(..., description="设备唯一标识")
    name: Optional[str] = Field(None, description="设备名称，如不提供则使用object_id")
    sensor_type: Optional[str] = Field(None, description="传感器类型，仅对sensor和binary_sensor有效")

class DeviceCreate(DeviceBase):
    """设备创建数据模型"""
    pass

class DeviceUpdate(BaseModel):
    """设备更新数据模型"""
    type: Optional[str] = Field(None, description="设备类型，如light、sensor、binary_sensor")
    name: Optional[str] = Field(None, description="设备名称")
    sensor_type: Optional[str] = Field(None, description="传感器类型，仅对sensor和binary_sensor有效")

class DeviceResponse(DeviceBase):
    """设备响应数据模型"""
    state: Optional[Dict[str, Any]] = Field({}, description="设备当前状态")

class DeviceState(BaseModel):
    """设备状态数据模型"""
    state: Dict[str, Any] = Field(..., description="设备状态")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI生命周期管理器
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时的操作
    logger.info("API服务器正在启动...")
    try:
        yield
    finally:
        # 关闭时的操作
        logger.info("API服务器正在关闭...")

# 创建 FastAPI 应用
def create_app(device_config: DeviceConfig, device_manager: MockDeviceManager) -> FastAPI:
    """
    创建FastAPI应用实例
    
    Args:
        device_config: 设备配置管理器
        device_manager: 设备管理器
        
    Returns:
        FastAPI: FastAPI应用实例
    """
    app = FastAPI(
        title="HA-MQTT-Mock API",
        description="Home Assistant MQTT设备模拟器API",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 在请求中提供设备配置和设备管理器
    def get_device_config():
        return device_config
    
    def get_device_manager():
        return device_manager
    
    @app.get("/api/devices", response_model=List[DeviceResponse], tags=["设备"])
    async def list_devices(
        config: DeviceConfig = Depends(get_device_config),
        manager: MockDeviceManager = Depends(get_device_manager)
    ):
        """获取所有设备列表"""
        devices_data = config.get_all_devices()
        
        # 为每个设备添加当前状态
        for device_data in devices_data:
            device_id = device_data.get("object_id")
            device = manager.get_device(device_id)
            if device:
                device_data["state"] = device.state
            else:
                device_data["state"] = {}
        
        return devices_data
    
    @app.post("/api/devices", response_model=DeviceResponse, tags=["设备"])
    async def create_device(
        device: DeviceCreate,
        config: DeviceConfig = Depends(get_device_config),
        manager: MockDeviceManager = Depends(get_device_manager)
    ):
        """创建新设备"""
        device_data = device.dict(exclude_unset=True)
        
        # 添加设备到配置
        if not config.add_device(device_data):
            raise HTTPException(status_code=400, detail="创建设备失败")
        
        # 重新加载所有设备
        new_devices = config.create_devices()
        
        # 找到新创建的设备
        new_device = None
        for d in new_devices:
            if d.object_id == device.object_id:
                new_device = d
                break
        
        if not new_device:
            raise HTTPException(status_code=500, detail="创建设备后无法找到")
        
        # 添加到设备管理器
        manager.add_device(new_device)
        
        # 返回设备数据
        response_data = device_data.copy()
        response_data["state"] = new_device.state
        return response_data
    
    @app.get("/api/devices/{device_id}", response_model=DeviceResponse, tags=["设备"])
    async def get_device(
        device_id: str = Path(..., description="设备ID"),
        config: DeviceConfig = Depends(get_device_config),
        manager: MockDeviceManager = Depends(get_device_manager)
    ):
        """获取指定设备详情"""
        device_data = config.get_device(device_id)
        if not device_data:
            raise HTTPException(status_code=404, detail=f"设备 {device_id} 不存在")
        
        # 添加设备当前状态
        device = manager.get_device(device_id)
        if device:
            device_data["state"] = device.state
        else:
            device_data["state"] = {}
        
        return device_data
    
    @app.put("/api/devices/{device_id}", response_model=DeviceResponse, tags=["设备"])
    async def update_device(
        device_id: str = Path(..., description="设备ID"),
        device_update: DeviceUpdate = Body(...),
        config: DeviceConfig = Depends(get_device_config),
        manager: MockDeviceManager = Depends(get_device_manager)
    ):
        """更新设备配置"""
        # 获取现有设备
        existing_device = config.get_device(device_id)
        if not existing_device:
            raise HTTPException(status_code=404, detail=f"设备 {device_id} 不存在")
        
        # 准备更新数据
        update_data = {**existing_device}
        for key, value in device_update.dict(exclude_unset=True).items():
            if value is not None:
                update_data[key] = value
        
        # 更新设备配置
        if not config.update_device(device_id, update_data):
            raise HTTPException(status_code=400, detail="更新设备失败")
        
        # 从设备管理器中移除旧设备
        manager.remove_device(device_id)
        
        # 创建新设备实例
        new_devices = config.create_devices()
        
        # 找到新创建的设备并添加到管理器
        new_device = None
        for d in new_devices:
            if d.object_id == device_id:
                new_device = d
                manager.add_device(d)
                break
        
        if not new_device:
            raise HTTPException(status_code=500, detail="更新设备后无法找到")
        
        # 返回更新后的设备数据
        update_data["state"] = new_device.state
        return update_data
    
    @app.delete("/api/devices/{device_id}", tags=["设备"])
    async def delete_device(
        device_id: str = Path(..., description="设备ID"),
        config: DeviceConfig = Depends(get_device_config),
        manager: MockDeviceManager = Depends(get_device_manager)
    ):
        """删除设备"""
        # 获取现有设备
        existing_device = config.get_device(device_id)
        if not existing_device:
            raise HTTPException(status_code=404, detail=f"设备 {device_id} 不存在")
        
        # 从配置中移除设备
        if not config.remove_device(device_id):
            raise HTTPException(status_code=400, detail="从配置中删除设备失败")
        
        # 从设备管理器中移除设备
        if not manager.remove_device(device_id):
            logger.warning(f"从设备管理器中删除设备 {device_id} 失败")
        
        return {"status": "success", "message": f"设备 {device_id} 已删除"}
    
    @app.put("/api/devices/{device_id}/state", response_model=DeviceState, tags=["设备状态"])
    async def update_device_state(
        device_id: str = Path(..., description="设备ID"),
        state_update: DeviceState = Body(...),
        manager: MockDeviceManager = Depends(get_device_manager)
    ):
        """更新设备状态"""
        # 获取设备
        device = manager.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"设备 {device_id} 不存在")
        
        # 更新状态
        device.state.update(state_update.state)
        
        # 返回更新后的状态
        return {"state": device.state}
    
    @app.get("/api/devices/{device_id}/state", response_model=DeviceState, tags=["设备状态"])
    async def get_device_state(
        device_id: str = Path(..., description="设备ID"),
        manager: MockDeviceManager = Depends(get_device_manager)
    ):
        """获取设备状态"""
        # 获取设备
        device = manager.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"设备 {device_id} 不存在")
        
        # 返回状态
        return {"state": device.state}
    
    @app.post("/api/reload", tags=["系统"])
    async def reload_devices(
        config: DeviceConfig = Depends(get_device_config),
        manager: MockDeviceManager = Depends(get_device_manager)
    ):
        """重新加载设备配置"""
        # 加载配置
        config.load()
        
        # 清除现有设备
        manager.devices.clear()
        manager.command_device_mapping.clear()
        
        # 创建设备实例
        devices = config.create_devices()
        
        # 添加设备到管理器
        for device in devices:
            manager.add_device(device)
        
        return {
            "status": "success", 
            "message": f"已重新加载 {len(devices)} 个设备"
        }
    
    return app 