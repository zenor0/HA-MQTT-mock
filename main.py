import paho.mqtt.client as mqtt

from config import ROOT_PREFIX, USERNAME, PASSWORD, BROKER_ADDRESS, BROKER_PORT
from models import *
from custom_listener import on_connect, on_message

from rich import print

# Set logger
import logging
from rich.logging import RichHandler
logger = logging.getLogger("rich")
logger.setLevel(logging.DEBUG)
logger.addHandler(RichHandler())

# MQTT Broker 配置
client_id = "mock_device_client"

# 创建 MQTT 客户端并设置回调函数
client = mqtt.Client(client_id)
client.on_connect = on_connect
# client.on_message = on_message
client.username_pw_set(username=USERNAME, password=PASSWORD)

# 连接到 MQTT broker
client.connect(BROKER_ADDRESS, BROKER_PORT)

mqtt_devices : list[MQTT_Device] = [
    Light(object_id='rgb_light', name="灯光"),
    Light(object_id='rgb_light_book', name="书房灯光"),
    Light(object_id='rgb_light_dining', name="客厅灯光"),
    Light(object_id='rgb_light_bedroom', name="卧室灯光"),
    Sensor(object_id='temp_sensor', name="温度传感器", sensor_type="temperature"),
    Sensor(object_id='humidity_sensor', name="湿度传感器", sensor_type="humidity"),
    Sensor(object_id='pressure_sensor', name="压力传感器", sensor_type="pressure"),
    Sensor(object_id='illuminance_sensor', name="光照传感器", sensor_type="illuminance"),
    Sensor(object_id='co2_sensor', name="二氧化碳传感器", sensor_type="co2"),
    Sensor(object_id='pm25_sensor', name="PM2.5传感器", sensor_type="pm25"),
    Sensor(object_id='pm10_sensor', name="PM10传感器", sensor_type="pm10"),
    BinarySensor(object_id='motion_sensor', name="人体感应", sensor_type="motion"),
    BinarySensor(object_id='door_sensor', name="门窗感应", sensor_type="door"),
    BinarySensor(object_id='window_sensor', name="门窗感应", sensor_type="window"),
    BinarySensor(object_id='smoke_sensor', name="烟雾感应", sensor_type="smoke"),
    Fan(object_id='fan', name="风扇"),
    Switch(object_id='switch', name="开关"),
    Humidifier(object_id='humidifier', name="加湿器", type="humidifier"),
    Humidifier(object_id='dehumidifier', name="除湿器", type="dehumidifier"),
    Cover(object_id='window_cover', name="窗户"),
    Climate(object_id='air_conditioner', name="空调"),
    # Camera(object_id='camera', name="Camera"),
    Alarm(object_id='alarm', name="警报"),
    Lock(object_id='lock', name="锁"),
    Lock(object_id='lock_front', name="前门锁"),
    Lock(object_id='lock_back', name="后门锁"),
    Vacuum(object_id='vacuum', name="吸尘器"),
    Vacuum(object_id='vacuum_kitchen', name="厨房吸尘器"),
    # MediaPlayer(object_id='media_player', name="Media Player"),
    WaterHeater(object_id='water_heater', name="热水器"),
    WaterHeater(object_id='water_heater_kitchen', name="厨房热水器"),
    WaterHeater(object_id='water_heater_bathroom', name="浴室热水器"),
    LawnMower(object_id='lawn_mower', name="除草机"),
    Valve(object_id='valve', name="阀门"),
    Valve(object_id='valve_kitchen', name="厨房阀门"),
    Button(object_id='button', name="按钮"),
    Button(object_id='button_kitchen', name="厨房按钮"),
    Button(object_id='button_bathroom', name="浴室按钮"),
    Button(object_id='button_bedroom', name="卧室按钮"),
    Button(object_id='button_living_room', name="客厅按钮"),
]

command_device_mapping : dict[str, MQTT_Device]= {}
# Publish discovery information for all devices
for device in mqtt_devices:
    device.publish_discovery(client)
    device.publish_state(client)
    client.subscribe(device.command_topic)
    command_device_mapping[device.command_topic] = device

# print(command_device_mapping)
def on_message(client, userdata, message: mqtt.MQTTMessage):
    logger.debug(f"Received message: '{message.payload.decode()}'\non topic '{message.topic}'")
    command_device_mapping[message.topic].on_update(client, payload=message.payload)

client.on_message = on_message

import asyncio
from models.mock import mock_device

# client.loop_forever()
async def main():
    client.loop_start()
    await asyncio.gather(mock_device(client, mqtt_devices, freq=10))
    
asyncio.run(main())

