import json
from typing import Any, Dict

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class Fan(MQTTDevice):
    def __init__(
        self,
        object_id: str,
        name: str | None = None,
        state: Dict[str, Any] | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            component="fan", object_id=object_id, name=name, *args, **kwargs
        )

        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "state_topic": self.state_topic,
            "state_value_template": "{{ value_json.state }}",
            "command_topic": self.command_topic,
            "command_template": '{ "state": "{{ value }}" }',
            "direction_command_template": "{{ iif(value == 'forward', 'fwd', 'rev') }}",
            "direction_value_template": "{{ iif(value == 'fwd', 'forward', 'reverse') }}",
            "oscillation_command_topic": self.command_topic,
            "oscillation_command_template": '{"state": "ON", "oscillation": "{{ value }}"}',
            "percentage_command_topic": self.command_topic,
            "percentage_command_template": '{"state": "ON", "percentage": "{{ value }}"}',
            "preset_mode_command_topic": self.command_topic,
            "preset_mode_command_template": '{"preset_mode": "{{ value }}"}',
            "preset_modes": ["auto", "smart", "whoosh", "eco", "breeze"],
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)