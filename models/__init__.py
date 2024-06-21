from config import ROOT_PREFIX
import json
import random

# Set logger
import logging

logger = logging.getLogger("rich")


def generate_device_info(name):
    return {
        "name": "Mock Bus",
        "identifiers": "zenor0's mock devices",
        "manufacturer": "zenor0's Corp",
        "model": "Mock Model",
        "sw_version": "0.1",
    }


class MQTT_Device:
    def __init__(self, component, object_id: str) -> None:
        self.component = component
        self.object_id = object_id
        self.state = {}

        self.home_topic = f"{ROOT_PREFIX}/{self.component}/{self.object_id}"

        self.state_topic = f"{self.home_topic}/state"
        self.command_topic = f"{self.home_topic}/command"

        self.discovery_topic = f"{self.home_topic}/config"

    def _get_discovery_payload(self):
        raise NotImplementedError

    def publish_discovery(self, client):
        client.publish(self.discovery_topic, self.discovery_payload, retain=True)

    def publish_state(self, client):
        client.publish(self.state_topic, json.dumps(self.state))

    def update_state(self, client, payload: dict):
        self.publish_discovery(client)
        try:
            self.state.update(payload)
            self.publish_state(client)
        except Exception as e:
            print(payload, e)
            return False
        return True

    def on_update(self, client, payload):
        if isinstance(payload, bytes):
            payload = payload.decode()

        # Check if payload a valid JSON
        if payload[0] != "{":
            logger.warning(f"Invalid JSON payload: {payload}, converting to string.")
            payload = {"payload": str(payload)}
        else:
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON payload: {payload}")
                return False

        ret = self.update_state(client, payload)
        if not ret:
            logger.error(f"Failed to update state for {self.name}")

    def dump_state(self):
        return json.dumps(self.state)


class Light(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="light", object_id=object_id)

        self.state |= {
            "state": "on",
            "brightness": 255,
            "color": [255, 0, 255],
            "effect": "none",
            "hue": 0,
            "sat": 0,
        }
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def _get_discovery_payload(self):
        payload = {
            "schema": "template",
            "name": self.name,
            "unique_id": self.object_id,
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "effect_list": ["rainbow", "colorloop"],
            "effect_template": "{{ value_json.effect }}",
            "command_on_template": '{"state": "on" {%- if brightness is defined -%} , "brightness": {{ brightness }} {%- endif -%} {%- if red is defined and green is defined and blue is defined -%} , "color": [{{ red }}, {{ green }}, {{ blue }}] {%- endif -%} {%- if hue is defined and sat is defined -%} , "huesat": [{{ hue }}, {{ sat }}] {%- endif -%} {%- if effect is defined -%} , "effect": "{{ effect }}" {%- endif -%} {%- if color_temp is defined -%} , "color_temp": "{{ color_temp }}" {%- endif -%} }\n',
            "command_off_template": '{"state": "off"}',
            "state_template": "{{ value_json.state }}",
            "brightness_template": "{{ value_json.brightness }}",
            "red_template": "{{ value_json.color[0] }}",
            "green_template": "{{ value_json.color[1] }}",
            "blue_template": "{{ value_json.color[2] }}",
            "effect_template": "{{ value_json.effect }}",
            "color_temp_template": "{{ value_json.color_temp }}",
            "max_mireds": 500,
            "min_mireds": 153,
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)


class BinarySensor(MQTT_Device):
    # https://www.home-assistant.io/integrations/binary_sensor/#device-class
    SENSOR_TYPES = [
        "motion",
        "door",
        "window",
        "smoke",
        "gas",
        "moisture",
        "occupancy",
        "vibration",
    ]

    def __init__(self, name, sensor_type=None, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="binary_sensor", object_id=object_id)

        if sensor_type not in self.SENSOR_TYPES:
            raise ValueError(f"Invalid sensor type: {sensor_type}")

        self.sensor_type = sensor_type
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "state_topic": self.state_topic,
            "value_template": "{{ value_json.state }}",
            "device_class": self.sensor_type,
            "payload_on": "ON",
            "payload_off": "OFF",
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)

    def update_state_mock(self):
        self.state = {"state": random.choice(["ON", "OFF"])}
        return


class Sensor(MQTT_Device):
    SENSOR_TYPES = [
        "temperature",
        "humidity",
        "pressure",
        "illuminance",
        "signal_strength",
        "battery",
        "co2",
        "pm25",
        "pm10",
        
    ]
    SENSOR_TYPE_PAYLOAD = {
        "temperature": {
            "value_template": "{{ value_json.temperature }}",
            "device_class": "temperature",
            "unit_of_measurement": "°C",
        },
        "humidity": {
            "value_template": "{{ value_json.humidity }}",
            "device_class": "humidity",
            "unit_of_measurement": "%",
        },
        "pressure": {
            "value_template": "{{ value_json.pressure }}",
            "device_class": "pressure",
            "unit_of_measurement": "hPa",
        },
        "illuminance": {
            "value_template": "{{ value_json.illuminance }}",
            "device_class": "illuminance",
            "unit_of_measurement": "lm",
        },
        "signal_strength": {
            "value_template": "{{ value_json.signal_strength }}",
            "device_class": "signal_strength",
            "unit_of_measurement": "dB",
        },
        "battery": {
            "value_template": "{{ value_json.battery }}",
            "device_class": "battery",
            "unit_of_measurement": "%",
        },
        "co2": {
            "value_template": "{{ value_json.co2 }}",
            "device_class": "co2",
            "unit_of_measurement": "ppm",
        },
        "pm25": {
            "value_template": "{{ value_json.pm25 }}",
            "device_class": "pm25",
            "unit_of_measurement": "µg/m³",
        },
        "pm10": {
            "value_template": "{{ value_json.pm10 }}",
            "device_class": "pm10",
            "unit_of_measurement": "µg/m³",
        },
        
        
    }

    def __init__(self, name, sensor_type: str = None, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="sensor", object_id=object_id)

        if sensor_type not in self.SENSOR_TYPES:
            raise ValueError(f"Invalid sensor type: {sensor_type}")
        self.sensor_type = sensor_type
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "state_topic": self.state_topic,
        }

        payload |= self.SENSOR_TYPE_PAYLOAD[self.sensor_type]

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)

    def update_state_mock(self):
        if self.sensor_type == "temperature":
            self.state = {"temperature": round(random.uniform(20, 30), 1)}
        elif self.sensor_type == "humidity":
            self.state = {"humidity": round(random.uniform(30, 60), 1)}
        elif self.sensor_type == "pressure":
            self.state = {"pressure": random.uniform(1000, 1010)}
        elif self.sensor_type == "illuminance":
            self.state = {"illuminance": random.uniform(100, 1000)}
        elif self.sensor_type == "signal_strength":
            self.state = {"signal_strength": random.uniform(-100, -50)}
        elif self.sensor_type == "battery":
            self.state = {"battery": random.uniform(20, 100)}
        elif self.sensor_type == "co2":
            self.state = {"co2": random.uniform(300, 1000)}
        elif self.sensor_type == "pm25":
            self.state = {"pm25": random.uniform(10, 100)}
        elif self.sensor_type == "pm10":
            self.state = {"pm10": random.uniform(10, 100)}
        return


class Switch(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="switch", object_id=object_id)

        self.state |= {"state": "OFF"}
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def _get_discovery_payload(self):
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


class Fan(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="fan", object_id=object_id)

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


class Climate(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="climate", object_id=object_id)

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


class Humidifier(MQTT_Device):
    DEVICE_CLASSES = ["humidifier", "dehumidifier"]

    def __init__(self, name, type=None, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="humidifier", object_id=object_id)

        if type not in self.DEVICE_CLASSES:
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


class Lock(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="lock", object_id=object_id)

        self.state |= {"state": "LOCKED"}
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def update_state(self, client, payload: dict):
        if "action" in payload:
            payload["state"] = payload.pop("action")

        jammed_rate = 0.5
        # It has possibility fail to lock or unlock, set state to JAMMED
        if payload["state"] == "LOCK" and random.random() < jammed_rate:
            payload["state"] = "MOTOR_JAMMED"
        elif payload["state"] == "UNLOCK" and random.random() < jammed_rate:
            payload["state"] = "MOTOR_JAMMED"

        return super().update_state(client, payload)

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "state_topic": self.state_topic,
            # "code_format": "^\\d{4}$",
            # "code_format": "123",
            "command_topic": self.command_topic,
            "command_template": '{ "action": "{{ value }}", "code":"{{ code }}" }',
            "payload_lock": "LOCK",
            "payload_unlock": "UNLOCK",
            "state_locked": "LOCK",
            "state_unlocked": "UNLOCK",
            "state_locking": "LOCKING",
            "state_unlocking": "UNLOCKING",
            "state_jammed": "MOTOR_JAMMED",
            "state_ok": "MOTOR_OK",
            "value_template": "{{ value_json.state }}",
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)


class Vacuum(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="vacuum", object_id=object_id)

        self.state |= {"state": "idle", "fan_speed": "off", "battery_level": 100}
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def update_state(self, client, payload: dict):
        fan_speed_enum = ["off", "min", "medium", "high", "max"]
        if payload["payload"] in fan_speed_enum:
            payload["fan_speed"] = payload["payload"]

        if payload["payload"] == "start":
            payload["state"] = "cleaning"

        if payload["payload"] == "pause":
            payload["state"] = "paused"

        if payload["payload"] == "stop":
            payload["state"] = "idle"

        if payload["payload"] == "return_to_base":
            payload["state"] = "returning"

        if payload["payload"] == "locate":
            payload["state"] = "idle"

        if payload["payload"] == "clean_spot":
            payload["state"] = "cleaning"

        error_rate = 0.1
        if random.random() < error_rate:
            payload["state"] = "error"

        return super().update_state(client, payload)

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "supported_features": [
                "start",
                "pause",
                "stop",
                "return_home",
                "battery",
                "status",
                "locate",
                "clean_spot",
                "fan_speed",
                "send_command",
            ],
            "command_topic": self.command_topic,
            "state_topic": self.state_topic,
            "set_fan_speed_topic": self.command_topic,
            "fan_speed_list": ["min", "medium", "high", "max"],
            "send_command_topic": self.command_topic,
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)


class WaterHeater(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="water_heater", object_id=object_id)

        self.state |= {"state": "ON", "mode": "eco", "temperature": 50}
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "power_command_topic": self.command_topic,
            "power_state_topic": self.state_topic,
            "power_state_template": "{{ value_json.state }}",
            "power_command_template": '{"state": "{{ "OFF" if value == "off" else "ON" }}" }',
            "mode_command_topic": self.command_topic,
            "mode_state_topic": self.state_topic,
            "mode_state_template": "{{ value_json.mode }}",
            "mode_command_template": '{"mode": "{{ value }}"}',
            "temperature_state_topic": self.state_topic,
            "temperature_state_template": "{{ value_json.temperature }}",
            "temperature_command_topic": self.command_topic,
            "temperature_command_template": '{"temperature": {{ value }} }',
            "precision": 0.1,
            "payload_off": "OFF",
            "payload_on": "ON",
            # "mode_state_topic": "~/mode/state",
            # "mode_state_template": "{{ value_json }}",
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)


class Button(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="button", object_id=object_id)

        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "command_on_template": '{"state": "ON"}',
            "payload_on": "ON",
            "payload_off": "OFF",
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)


class Valve(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="valve", object_id=object_id)

        self.state |= {"state": "opening", "position": 10}
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def update_state(self, client, payload: dict):
        if payload["position"]:
            position = int(payload["position"])
            payload["state"] = "open" if position > 0 else "closed"
        return super().update_state(client, payload)

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "state_topic": self.state_topic,
            # "value_template": "{{ value_json.state }}",
            "command_topic": self.command_topic,
            "command_template": '{ "position": "{{ value }}" }',
            "reports_position": True,
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)


class LawnMower(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="lawn_mower", object_id=object_id)

        self.state |= {"state": "docked"}
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def update_state(self, client, payload: dict):
        if payload["activity"] == "start_mowing":
            payload["state"] = "mowing"

        if payload["activity"] == "pause":
            payload["state"] = "paused"

        if payload["activity"] == "dock":
            payload["state"] = "docked"

        error_rate = 0.1
        if random.random() < error_rate:
            payload["state"] = "error"

        return super().update_state(client, payload)

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "activity_state_topic": self.state_topic,
            "activity_value_template": "{{ value_json.state }}",
            "pause_command_topic": self.command_topic,
            "pause_command_template": '{"activity": "{{ value }}"}',
            "dock_command_topic": self.command_topic,
            "dock_command_template": '{"activity": "{{ value }}"}',
            "start_mowing_command_topic": self.command_topic,
            "start_mowing_command_template": '{"activity": "{{ value }}"}',
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)


class Cover(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="cover", object_id=object_id)

        self.state |= {"state": "open", "position": 100, "tilt": 50}
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def update_state(self, client, payload: dict):

        try:
            if payload["action"] == "OPEN":
                payload["state"] = "open"
                payload["position"] = 100
            elif payload["action"] == "CLOSE":
                payload["state"] = "closed"
                payload["position"] = 0
            elif payload["action"] == "STOP":
                payload["state"] = "stopped"
        except KeyError:
            pass

        return super().update_state(client, payload)

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "position_topic": self.state_topic,
            "position_template": "{{ value_json.position }}",
            "set_position_topic": self.command_topic,
            "set_position_template": '{"position": {{ value }}}',
            "value_template": "{{ value_json.state }}",
            "tilt_command_topic": self.command_topic,
            "tilt_command_template": '{"tilt": {{ value }}}',
            "tilt_status_topic": self.state_topic,
            "tilt_status_template": "{{ value_json.tilt }}",
            "payload_open": '{"action": "OPEN"}',
            "payload_close": '{"action": "CLOSE"}',
            "payload_stop": '{"action": "STOP"}',
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)


class Alarm(MQTT_Device):
    def __init__(self, name, object_id=None) -> None:
        object_id = object_id if object_id else name.lower().replace(" ", "_")
        super().__init__(component="alarm_control_panel", object_id=object_id)

        self.state |= {"state": "arming", "code": "1234"}
        self.name = name
        self.discovery_payload = self._get_discovery_payload()

    def update_state(self, client, payload: dict):
        ARM_PAYLOADS = ["ARM_HOME", "ARM_AWAY", "ARM_NIGHT", "ARM_CUSTOM_BYPASS"]

        if payload["action"] in ARM_PAYLOADS:
            payload["state"] = "armed_" + payload["action"].split("_")[1].lower()

        if payload["action"] == "DISARM":
            payload["state"] = "disarmed"

        return super().update_state(client, payload)

    def _get_discovery_payload(self):
        payload = {
            "name": self.name,
            "unique_id": self.object_id,
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "value_template": "{{ value_json.state }}",
            "command_template": '{ "action": "{{ action }}", "code":"{{ code }}" }',
            "code": 123,
        }

        payload["device"] = generate_device_info(self.name)
        return json.dumps(payload)
