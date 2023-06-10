import db
import time
import traceback
import asyncio
import logging
from struct import pack
from bleak import BleakClient
from enum import Enum
from unpacking import parse_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BLE")

DEVICE_ADDRESS = "4C:EB:D6:62:18:3A"
CHARACTERISTIC_UUID = "0000FF01-0000-1000-8000-00805f9b34fb"


def get_config_packet(status, protocol):
    return pack("<2B2c", 3, 0, chr(status).encode(), protocol.encode())


def get_status_protocol_pairs():
    status_protocol_pairs = []
    for status in (30, 31):
        for protocol in range(4):
            status_protocol_pairs.append((status, str(protocol)))
    return status_protocol_pairs


class State(Enum):
    DISCONNECTED = "DISCONNECTED"
    CONFIGURATION = "CONFIGURATION"
    SUBSCRIBING = "SUBSCRIBING"
    CONNECTING = "CONNECTING"
    RECONNECTING = "RECONNECTING"
    CONNECTED = "CONNECTED"
    DISCONNECTING = "DISCONNECTING"
    FINISHED = "FINISHED"


class GATTHelper:
    def read_gatt_char(self):
        return self.loop.run_until_complete(self.read_gatt_char_async())

    async def read_gatt_char_async(self):
        return await self.client.read_gatt_char(self.characteristic_uuid)

    def write_gatt_char(self, data):
        logger.info(f"Writing {data} to {self.characteristic_uuid}")
        return self.loop.run_until_complete(self.write_gatt_char_async(data))

    async def write_gatt_char_async(self, data):
        return await self.client.write_gatt_char(self.characteristic_uuid, data)

    def susbscribe_gatt_char(self, notify_callback):
        logger.info(f"Subscribing to {self.characteristic_uuid}")
        self.loop.run_until_complete(self.susbscribe_gatt_char_async(notify_callback))

    async def susbscribe_gatt_char_async(self, notify_callback):
        await self.client.start_notify(self.characteristic_uuid, notify_callback)


class StateMachine(GATTHelper):
    def __init__(self, status, protocol):
        self.status = status
        self.protocol = protocol
        self.state = State.DISCONNECTED
        self.loop = asyncio.get_event_loop()
        self.device_address = "4C:EB:D6:62:18:3A"
        self.characteristic_uuid = "0000FF01-0000-1000-8000-00805f9b34fb"
        self.packets_received = 0
        self.time_to_connect = 0.0
        self.connection_attempts = 0

    def start(self):
        while True:
            logger.info(f"Current state: {self.state}")
            if self.state == State.FINISHED:
                break
            method = getattr(self, f"{self.state.value.lower()}_state")
            method()

    def disconnected_state(self):
        self.loop.run_until_complete(self.disconnected_state_async())

    async def disconnected_state_async(self):
        logger.info(f"Disconnected. Connecting to device: {self.device_address}")
        self.client = BleakClient(self.device_address)
        self.state = State.CONNECTING

    def connecting_state(self):
        self.loop.run_until_complete(self.connecting_state_async())

    async def connecting_state_async(self) -> bool:
        """Check if the client is still connected."""
        if not self.client.is_connected:
            await self.try_reconnect(State.CONFIGURATION, State.DISCONNECTED)

    def reconnecting_state(self):
        self.loop.run_until_complete(self.reconnecting_state_async())

    async def reconnecting_state_async(self):
        if not self.client.is_connected:
            await self.try_reconnect(State.SUBSCRIBING, State.RECONNECTING)

    async def try_reconnect(self, successful_state, error_state):
        t1 = time.time()
        self.connection_attempts += 1
        try:
            await self.client.connect()
            self.state = successful_state
            self.time_to_connect += time.time() - t1
            self.save_loss()
        except Exception as e:
            logger.warning("Error connecting to device: {}".format(e))
            self.state = error_state
            self.time_to_connect += time.time() - t1

    def save_loss(self):
        db.save_loss(self.time_to_connect, self.connection_attempts)
        self.time_to_connect = 0.0
        self.connection_attempts = 0

    def configuration_state(self):
        self.write_gatt_char(get_config_packet(self.status, self.protocol))
        self.state = State.SUBSCRIBING

    def subscribing_state(self):
        try:
            self.susbscribe_gatt_char(self.notify_callback)
            self.state = State.CONNECTED
            logger.info("Subscribed to device")
        except Exception as e:
            logger.info(f"Error subscribing to device: {e}")
            self.state = State.RECONNECTING

    def connected_state(self):
        if not self.client.is_connected:
            self.state = State.RECONNECTING
        self.go_to_sleep(1)
        if self.data_ready:
            data = self.read_gatt_char()
            logger.info(f"Received data: {data}")
            self.packets_received += 1
            if self.packets_received >= 3:
                self.state = State.DISCONNECTING
            try:
                parsed_data = parse_data(data, int(self.protocol))
                logger.info(f"Parsed data: {parsed_data}")
            except Exception as e:
                logger.error(f"Error parsing data: {e}")
                traceback.print_exc()
            self.data_ready = False

    def go_to_sleep(self, seconds):
        self.loop.run_until_complete(self.go_to_sleep_async(seconds))

    async def go_to_sleep_async(self, seconds):
        await asyncio.sleep(seconds)

    def notify_callback(self, sender, data):
        logger.info(f"{sender=}, {data=}")
        self.data_ready = True

    def disconnecting_state(self):
        self.loop.run_until_complete(self.disconnecting_state_async())

    async def disconnecting_state_async(self):
        await self.write_gatt_char_wait_for_config()
        self.packets_received = 0
        self.state = State.FINISHED
        await self.client.disconnect()

    async def write_gatt_char_wait_for_config(self):
        await self.write_gatt_char_async(get_config_packet(10, "0"))


if __name__ == "__main__":
    sm = StateMachine(30, "0")
    sm.start()
