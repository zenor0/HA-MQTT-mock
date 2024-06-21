from utils import publish_discovery
# 连接回调函数
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")

    else:
        print("Connection failed with code", rc)


# 消息回调函数
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
