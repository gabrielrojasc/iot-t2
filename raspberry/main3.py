import asyncio
import logging
from struct import pack
from bleak import BleakClient
from enum import Enum
from time import sleep

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
            try:
                await self.client.connect()
                self.state = State.CONFIGURATION
            except Exception as e:
                print("Error connecting to device: {}".format(e))
                self.state = State.DISCONNECTED

    def reconnecting_state(self):
        self.loop.run_until_complete(self.reconnecting_state_async())

    async def reconnecting_state_async(self):
        if not self.client.is_connected:
            try:
                await self.client.connect()
                self.state = State.SUBSCRIBING
            except Exception as e:
                print("Error connecting to device: {}".format(e))
                self.state = State.RECONNECTING

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
        self.go_to_sleep(3)

    def go_to_sleep(self, seconds):
        self.loop.run_until_complete(self.go_to_sleep_async(seconds))

    async def go_to_sleep_async(self, seconds):
        await asyncio.sleep(seconds)

    def disconnecting_state(self):
        self.loop.run_until_complete(self.disconnect())

    def notify_callback(self, sender, data):
        logger.info(f"{sender=}, {data=}")
        # data = self.read_gatt_char()
        self.packets_received += 1
        if self.packets_received >= 3:
            self.state = State.DISCONNECTING

    async def disconnect(self):
        self.write_gatt_char_wait_for_config()
        self.packets_received = 0
        self.state = State.FINISHED
        await self.client.disconnect()

    def write_gatt_char_wait_for_config(self):
        self.write_gatt_char(get_config_packet(10, "0"))


if __name__ == "__main__":
    sm = StateMachine(30, "0")
    sm.start()
