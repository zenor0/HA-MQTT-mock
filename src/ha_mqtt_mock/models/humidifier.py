import json
from typing import Any, Dict

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class Humidifier(MQTTDevice):
    DEVICE_CLASSES = ["humidifier", "dehumidifier"]

    def __init__(
        self,
        object_id: str,
        name: str | None = None,
        state: Dict[str, Any] | None = None,
        device_type: str = "humidifier",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(component="humidifier", object_id=object_id, name=name, *args, **kwargs)

        if device_type not in self.DEVICE_CLASSES:
            raise ValueError(f"Invalid device class: {type}")

        self.state |= {"humidity": 50, "target_humidity": 50, "mode": "normal"}
        self.type = type
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "device_class": self.type,
            "state_topic": self.state_topic,
            "state_value_template": "{{ value_json.state }}",
            # "action_topic": f"{self.home_topic}/action",
            "action_topic": self.command_topic,
            "command_topic": self.command_topic,
            "command_template": '{ "state": "{{ value }}" }',
            "current_humidity_topic": self.state_topic,
            "current_humidity_template": "{{ value_json.humidity }}",
            "target_humidity_state_topic": self.state_topic,
            "target_humidity_state_template": "{{ value_json.target_humidity }}",
            "target_humidity_command_topic": self.command_topic,
            "target_humidity_command_template": '{"target_humidity": "{{ value }}" }',
            "mode_state_topic": self.state_topic,
            "mode_state_template": "{{ value_json.mode }}",
            "mode_command_topic": self.command_topic,
            "mode_command_template": '{"mode": "{{ value }}" }',
            "modes": [
                "normal",
                "eco",
                "away",
                "boost",
                "comfort",
                "home",
                "sleep",
                "auto",
                "baby",
            ],
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)

