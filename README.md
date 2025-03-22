# Home Assistant MQTT 模拟器

一个用于模拟各种Home Assistant MQTT设备的工具，可用于测试和开发Home Assistant集成。

## 项目结构

重构后的项目结构如下：

```
src/ha_mqtt_mock/
├── __init__.py        # 包入口，导出主要功能
├── main.py            # 主程序入口
├── cli.py             # 命令行参数处理
├── service.py         # 应用服务管理
├── mqtt_client.py     # MQTT客户端功能
├── config.py          # 配置相关功能
├── device_config.py   # 设备配置管理
├── api.py             # API服务器实现
├── mock.py            # 模拟设备管理
├── sample_data.py     # 示例数据生成
├── models/            # 设备模型定义
└── utils/             # 工具函数
    ├── __init__.py
    ├── logging.py     # 日志配置
    └── mqtt_helpers.py # MQTT辅助函数
```

## 功能说明

- **cli.py**: 处理命令行参数解析和程序入口
- **service.py**: 封装应用服务管理，包括初始化、启动和关闭
- **mqtt_client.py**: 处理MQTT客户端创建和管理
- **sample_data.py**: 提供示例设备数据
- **main.py**: 简化的主程序入口点

## 使用方法

```bash
python -m ha_mqtt_mock -b mqtt.broker.address -p 1883 -u username --password password
```

更多选项请运行：

```bash
python -m ha_mqtt_mock --help
```

## 开发说明

项目重构使模块职责更加清晰，便于维护和扩展：

1. 将过长的main.py拆分成多个功能模块
2. 使用类封装服务生命周期管理
3. 分离MQTT客户端功能和示例数据生成
4. 减少模块间耦合 