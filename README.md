# HA-MQTT-mock (重构版)

这个项目提供了一个简单的MQTT模拟服务，用于在Home Assistant中模拟各种MQTT设备。

## 重构改进

原始项目已经进行了以下重构和改进：

1. **改进的项目结构**：采用标准Python包结构，使用`src`布局
2. **更好的配置管理**：使用环境变量和数据类进行配置管理
3. **模块化设计**：将设备模型分离到独立的文件中
4. **增强的错误处理**：添加了异常处理和日志记录
5. **类型注解**：添加了类型提示，提高代码可读性
6. **测试支持**：添加了单元测试
7. **命令行界面**：提供了更丰富的命令行选项
8. **开发工具支持**：添加了代码格式化和检查工具

## 功能

此项目可以模拟Home Assistant支持的大多数MQTT设备。目前实现的设备类型包括：

- 灯光设备 (Light)
- 传感器 (Sensor)
- 二元传感器 (BinarySensor)

可以通过添加更多设备模型类来扩展支持的设备类型。

## 项目结构

```
.
├── Makefile                # 构建和开发工具
├── README.md               # 项目说明
├── requirements.txt        # 项目依赖
├── setup.py                # 包安装配置
├── src/                    # 源代码目录
│   └── ha_mqtt_mock/       # 主包
│       ├── __init__.py     # 包初始化
│       ├── config.py       # 配置管理
│       ├── main.py         # 主程序入口
│       ├── mock.py         # 模拟器核心
│       ├── models/         # 设备模型
│       │   ├── __init__.py # 模型初始化
│       │   ├── base.py     # 基础设备模型
│       │   ├── light.py    # 灯光设备模型
│       │   └── sensor.py   # 传感器设备模型
│       └── utils/          # 工具函数
│           ├── __init__.py # 工具初始化
│           ├── logging.py  # 日志工具
│           └── mqtt_helpers.py # MQTT助手函数
└── tests/                  # 测试目录
    ├── __init__.py         # 测试包初始化
    ├── test_config.py      # 配置测试
    └── test_models.py      # 模型测试
```

## 安装

### 使用pip安装

```bash
pip install -e .
```

### 使用Makefile安装

```bash
# 标准安装
make install

# 开发模式安装
make dev-install
```

## 配置

可以通过环境变量或命令行参数配置MQTT连接：

### 环境变量

```bash
export MQTT_BROKER_ADDRESS=192.168.1.100
export MQTT_BROKER_PORT=1883
export MQTT_USERNAME=your_username
export MQTT_PASSWORD=your_password
export MQTT_ROOT_PREFIX=homeassistant
```

### 命令行参数

```bash
ha-mqtt-mock --broker 192.168.1.100 --port 1883 --username your_username --password your_password
```

## 使用方法

### 命令行运行

安装后可以直接运行：

```bash
ha-mqtt-mock
```

或者使用Makefile：

```bash
make run
```

### 命令行选项

```
usage: ha-mqtt-mock [-h] [-b BROKER] [-p PORT] [-u USERNAME] [--password PASSWORD] [-i INTERVAL] [-v] [--no-rich] [--log-file LOG_FILE]

Home Assistant MQTT模拟器

options:
  -h, --help            显示帮助信息并退出
  -b BROKER, --broker BROKER
                        MQTT服务器地址
  -p PORT, --port PORT  MQTT服务器端口
  -u USERNAME, --username USERNAME
                        MQTT用户名
  --password PASSWORD   MQTT密码
  -i INTERVAL, --interval INTERVAL
                        模拟更新间隔（秒）
  -v, --verbose         启用详细日志
  --no-rich             禁用富文本日志格式
  --log-file LOG_FILE   日志文件路径
```

## 开发

### 代码格式化

```bash
make format
```

### 代码检查

```bash
make lint
```

### 运行测试

```bash
make test
```

## 扩展

要添加新的设备类型，只需创建一个继承自`MQTTDevice`的新类，并实现必要的方法：

1. 在`src/ha_mqtt_mock/models/`目录下创建新的设备模型文件
2. 实现`_get_discovery_payload()`方法，提供设备的发现信息
3. 实现`update_state_mock()`方法，提供模拟行为
4. 在`src/ha_mqtt_mock/models/__init__.py`中导出新的设备类

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。 