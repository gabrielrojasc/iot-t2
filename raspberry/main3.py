import asyncio
import logging
from struct import pack
from bleak import BleakClient
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BLE")

DEVICE_ADDRESS = "4C:EB:D6:62:18:3A"
CHARACTERISTIC_UUID = "0000FF01-0000-1000-8000-00805f9b34fb"


def get_config_packet(status, protocol):
    return pack("<2B2c", 0, 0, chr(status).encode(), protocol.encode())


def get_status_protocol_pairs():
    status_protocol_pairs = []
    for status in (31, 30):
        for protocol in range(4):
            status_protocol_pairs.append((status, str(protocol)))
    return status_protocol_pairs


class State(Enum):
    DISCONNECTED = 0
    CONFIGURATION = 1
    CONNECTING = 2
    RECONNECTIONG = 3
    CONNECTED = 4


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
        asyncio.sleep(1)


class StateMachine(GATTHelper):
    def __init__(self, status, protocol):
        self.status = status
        self.protocol = protocol
        self.state = State.DISCONNECTED
        self.loop = asyncio.get_event_loop()
        self.device_address = "4C:EB:D6:62:18:3A"
        self.characteristic_uuid = "0000FF01-0000-1000-8000-00805f9b34fb"
        self.reconnect_delay = 5  # Delay in seconds before attempting reconnection
        self.packets_received = 0
        self.first_connection = True

    def start(self):
        while True:
            if self.state == State.DISCONNECTED:
                self.disconnected_state()
            elif self.state == State.CONNECTING:
                self.check_connection()
            elif self.state == State.CONFIGURATION:
                self.configuration_state()
            elif self.state == State.RECONNECTING:
                self.reconnecting_state()
            elif self.state == State.CONNECTED:
                self.connected_state()

    def disconnected_state(self):
        self.loop.run_until_complete(self.disconnected_state_async())

    async def disconnected_state_async(self):
        logger.info(f"Disconnected. Connecting to device: {self.device_address}")
        self.client = BleakClient(self.device_address)
        self.state = State.CONNECTING

    def check_connection(self):
        self.loop.run_until_complete(self.check_connection_async())

    async def check_connection_async(self) -> bool:
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
                self.state = State.CONNECTED
            except Exception as e:
                print("Error connecting to device: {}".format(e))
                self.state = State.RECONNECTING

    def configuration_state(self):
        try:
            self.write_gatt_char(get_config_packet(self.status, self.protocol))
        except Exception as e:
            logger.info(f"Error writing to device: {e}")
            self.state = State.DISCONNECTED

    def connected_state(self):
        self.susbscribe_gatt_char(self.notify_callback)

    def notify_callback(self, sender, data):
        data = self.read_gatt_char()
        logger.info(f"Received data: {data}")
        self.packets_received += 1
        if self.packets_received >= 3:
            self.disconnect()

    def disconnet(self):
        self.write_gatt_char(get_config_packet(10, "0"))
        self.packets_received = 0
        self.state = State.DISCONNECTED
        self.client.disconnect()


if __name__ == "__main__":
    sm = StateMachine(30, "0")
    sm.start()
