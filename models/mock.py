from . import *

import asyncio

async def mock_device(client, sensor: MQTT_Device | list[MQTT_Device], freq: int=10):
    while True:
        if not isinstance(sensor, list):
            sensor = [sensor]
        
        for s in sensor:
            # Check instance if have update_state_mock method
            if not hasattr(s, "update_state_mock"):
                continue
            s.update_state_mock()
            s.publish_state(client)
            logger.debug(f"Published state for '{s.name}'\t state: {s.state}")
        
        await asyncio.sleep(freq)