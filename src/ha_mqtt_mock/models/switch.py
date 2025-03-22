import json
from typing import Any, Dict

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class Switch(MQTTDevice):
    def __init__(
        self,
        object_id: str,
        name: str | None = None,
        state: Dict[str, Any] | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(component="switch", object_id=object_id, name=name, *args, **kwargs)

        self.state |= {"state": "OFF"}
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def _get_discovery_payload(self) -> Dict[str, Any]:
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "payload_on": '{"state": "ON"}',
            "payload_off": '{"state": "OFF"}',
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)
