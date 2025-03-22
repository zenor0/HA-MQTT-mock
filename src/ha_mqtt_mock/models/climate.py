import json
from typing import Any, Dict

from ha_mqtt_mock.utils.mqtt_helpers import generate_device_info
from ha_mqtt_mock.models.base import MQTTDevice


class Climate(MQTTDevice):
    def __init__(
        self,
        object_id: str,
        name: str | None = None,
        state: Dict[str, Any] | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(component="climate", object_id=object_id, name=name, *args, **kwargs)

        self.state |= {"state": "on", "mode": "cool", "temperature": 25}
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "state_topic": self.state_topic,
            "state_value_template": "{{ value_json.state }}",
            "modes": ["off", "cool", "fan_only", "heat", "dry"],
            "swing_modes": ["on", "off"],
            "fan_modes": ["high", "medium", "low"],
            "preset_modes": ["eco", "sleep", "activity", "comfort"],
            "preset_mode_state_topic": self.state_topic,
            "preset_mode_command_topic": self.command_topic,
            "preset_mode_command_template": '{ "preset_mode": "{{ value }}" }',
            "mode_state_topic": self.state_topic,
            "mode_state_template": "{{ value_json.mode }}",
            "mode_command_topic": self.command_topic,
            "mode_command_template": '{"state": "{{ "off" if value == "off" else "on" }}", "mode": "{{ value }}" }',
            "temperature_state_topic": self.state_topic,
            "temperature_state_template": "{{ value_json.temperature }}",
            "temperature_command_topic": self.command_topic,
            "temperature_command_template": '{ "temperature": {{ value }} }',
            "temperature_high_state_topic": self.state_topic,
            "temperature_high_state_template": "{{ value_json.temperature_high }}",
            "temperature_high_command_topic": self.command_topic,
            "temperature_high_command_template": '{ "temperature_high": {{ value }} }',
            "temperature_low_state_topic": self.state_topic,
            "temperature_low_state_template": "{{ value_json.temperature_low }}",
            "temperature_low_command_topic": self.command_topic,
            "temperature_low_command_template": '{ "temperature_low": {{ value }} }',
            "fan_mode_command_topic": self.command_topic,
            "fan_mode_command_template": '{ "fan_mode": "{{ value }}" }',
            "swing_mode_command_topic": self.command_topic,
            "swing_mode_command_template": '{ "swing_mode": "{{ value }}" }',
            "precision": 1,
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)

