"""应用服务管理模块"""

import asyncio
import logging
import signal

import uvicorn

from ha_mqtt_mock import __version__
from ha_mqtt_mock.api import create_app
from ha_mqtt_mock.config import MQTTConfig
from ha_mqtt_mock.engine import DeviceConfig
from ha_mqtt_mock.engine import MockDeviceManager
from ha_mqtt_mock.engine import create_mqtt_client, setup_mqtt_client, disconnect_mqtt_client
from ha_mqtt_mock.models import create_sample_devices

logger = logging.getLogger(__name__)

class AppService:
    """应用服务类，管理应用的生命周期"""
    
    def __init__(self, 
                 mqtt_config: MQTTConfig,
                 config_file: str,
                 mock_interval: int = 10,
                 api_host: str = "127.0.0.1",
                 api_port: int = 8080,
                 enable_api: bool = True):
        """
        初始化应用服务
        
        Args:
            mqtt_config: MQTT配置
            config_file: 设备配置文件路径
            mock_interval: 模拟更新间隔（秒）
            api_host: API服务器主机地址
            api_port: API服务器端口
            enable_api: 是否启用API服务器
        """
        self.mqtt_config = mqtt_config
        self.config_file = config_file
        self.mock_interval = mock_interval
        self.api_host = api_host
        self.api_port = api_port
        self.enable_api = enable_api
        
        # 将在后续初始化
        self.mqtt_client = None
        self.device_config = None
        self.device_manager = None
        self.api_app = None
        self.api_server = None
        self.shutdown_event = None
        self.mock_task = None
        self.api_task = None

    async def initialize(self) -> bool:
        """
        初始化服务
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 创建设备配置管理器
            self.device_config = DeviceConfig(config_file=self.config_file)
            
            # 加载设备配置
            devices_data = self.device_config.load()
            
            # 如果没有设备配置，创建示例设备
            if not devices_data:
                logger.info("没有找到设备配置，创建示例设备")
                sample_devices = create_sample_devices()
                self.device_config.save(sample_devices)
            
            # 创建设备实例
            device_instances = self.device_config.create_devices()
            
            # 创建设备管理器
            self.device_manager = MockDeviceManager()
            
            # 添加设备到管理器
            self.device_manager.add_devices(device_instances)
            
            # 创建MQTT客户端
            self.mqtt_client = create_mqtt_client(self.mqtt_config)
            
            # 设置MQTT客户端
            setup_mqtt_client(
                self.mqtt_client, 
                self.mqtt_config, 
                self.device_manager.on_message
            )
            
            # 发布设备发现信息
            self.device_manager.publish_all_discoveries(self.mqtt_client)
            
            # 发布初始状态
            self.device_manager.publish_all_states(self.mqtt_client)
            
            # 订阅命令主题
            self.device_manager.subscribe_all_commands(self.mqtt_client)
            
            # 创建关闭事件
            self.shutdown_event = asyncio.Event()
            
            # 如果启用API服务器，创建FastAPI应用
            if self.enable_api:
                self.api_app = create_app(self.device_config, self.device_manager)
                
                # 配置Uvicorn服务器
                uvicorn_config = uvicorn.Config(
                    app=self.api_app,
                    host=self.api_host,
                    port=self.api_port,
                    log_level=logger.level,
                    timeout_graceful_shutdown=5,  # 设置优雅关闭超时时间
                    timeout_keep_alive=5,  # 设置保持连接超时时间
                    log_config=None,  # 禁用uvicorn默认日志配置
                )
                self.api_server = uvicorn.Server(uvicorn_config)
            
            return True
            
        except Exception as e:
            logger.exception(f"初始化服务失败: {e}")
            return False

    async def start(self) -> None:
        """启动服务"""
        logger.info(f"HA-MQTT-mock v{__version__} 已启动")
        logger.info(f"已添加 {len(self.device_manager.devices)} 个设备")
        
        # 创建并跟踪模拟任务
        self.mock_task = asyncio.create_task(
            self.device_manager.mock_devices(self.mqtt_client, interval=self.mock_interval)
        )
        
        # 如果启用API服务器，创建API服务器任务
        if self.api_server:
            logger.info(f"启动API服务器 - http://{self.api_host}:{self.api_port}")
            self.api_task = asyncio.create_task(self.api_server.serve())
        
        # 创建任务列表
        tasks = [self.mock_task]
        if self.api_task:
            tasks.append(self.api_task)
        
        # 等待任务完成或关闭事件
        await asyncio.wait(
            tasks + [asyncio.create_task(self.shutdown_event.wait())],
            return_when=asyncio.FIRST_COMPLETED
        )

    async def shutdown(self) -> None:
        """关闭服务"""
        if self.shutdown_event.is_set():
            return
            
        logger.info("正在优雅关闭...")
        
        # 设置关闭事件
        self.shutdown_event.set()
        
        # 停止API服务器（如果存在）
        if self.api_server:
            logger.debug("正在关闭API服务器...")
            self.api_server.should_exit = True
            try:
                await asyncio.wait_for(self.api_server.shutdown(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("API服务器关闭超时")
            except Exception as e:
                logger.warning(f"API服务器关闭时发生错误: {e}")
        
        # 取消模拟任务（如果存在）
        if self.mock_task and not self.mock_task.done():
            logger.debug("正在取消模拟任务...")
            self.mock_task.cancel()
            try:
                await self.mock_task
            except asyncio.CancelledError:
                pass
        
        # 停止设备模拟
        self.device_manager.stop_mock()
        
        # 断开MQTT连接
        disconnect_mqtt_client(self.mqtt_client)
        
        logger.info("服务已完全关闭")

    def setup_signal_handlers(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        设置信号处理器
        
        Args:
            loop: 事件循环
        """
        def signal_handler():
            """处理中断信号的回调函数"""
            if not self.shutdown_event.is_set():  # 防止重复触发
                # 创建一个关闭任务，不阻塞信号处理器
                asyncio.create_task(self.shutdown())
        
        # 注册信号处理器
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler) 