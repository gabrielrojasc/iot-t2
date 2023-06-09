import asyncio
from bleak import BleakScanner, BleakClient
from time import sleep
from struct import pack
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEVICE_ADDRESS = "4C:EB:D6:62:18:3A"
CHARACTERISTIC_UUID = "0000FF01-0000-1000-8000-00805f9b34fb"


def get_config_packet(status, protocol):
    return pack("<2c", chr(status).encode(), protocol.encode())


def get_status_protocol_pairs():
    status_protocol_pairs = []
    for status in (31, 30):
        for protocol in range(4):
            status_protocol_pairs.append((status, str(protocol)))
    return status_protocol_pairs


class GATTHelper:
    def read_gatt_char(self):
        return self.loop.run_until_complete(self.read_gatt_char_async())

    async def read_gatt_char_async(self):
        return await self.client.read_gatt_char(self.characteristic_uuid)

    def write_gatt_char(self, data):
        return self.loop.run_until_complete(self.write_gatt_char_async(data))

    async def write_gatt_char_async(self, data):
        return await self.client.write_gatt_char(self.characteristic_uuid, data)


class StateMachine(GATTHelper):
    def __init__(self):
        self.state = "disconnected"
        self.loop = asyncio.get_event_loop()
        self.device_address = "4C:EB:D6:62:18:3A"
        self.characteristic_uuid = "0000FF01-0000-1000-8000-00805f9b34fb"
        self.reconnect_delay = 5  # Delay in seconds before attempting reconnection

    def start(self):
        while True:
            if self.state == "disconnected":
                self.disconnected_state()
            elif self.state == "connecting":
                self.check_connection()
            elif self.state == "connected":
                self.connected_state()

    def disconnected_state(self):
        self.loop.run_until_complete(self.disconnected_state_async())

    async def disconnected_state_async(self):
        logger.info(f"Disconnected. Connecting to device: {self.device_address}")
        self.client = BleakClient(self.device_address)
        self.state = "connecting"

    def check_connection(self):
        self.loop.run_until_complete(self.check_connection_async())

    async def check_connection_async(self) -> bool:
        """Check if the client is still connected."""
        if not self.client.is_connected:
            try:
                await self.client.connect()
                self.state = "connected"
            except Exception as e:
                self.state = "disconnected"

    def connected_state(self):
        data = self.read_gatt_char()
        logger.info(f"Received data: {data}")
        self.write_gatt_char(get_config_packet(31, "0"))

    def notify_callback(self, sender, data):
        ...


if __name__ == "__main__":
    sm = StateMachine()
    sm.loop.run_until_complete(sm.start())
