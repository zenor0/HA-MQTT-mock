from config import ROOT_PREFIX
import json

# 发布设备发现信息
def publish_discovery(client, component, object_id, payload):
    client.publish(
        f"{ROOT_PREFIX}/{component}/{object_id}/config",
        json.dumps(payload),
        retain=True,
    )
