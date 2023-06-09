import asyncio
from bleak import BleakScanner, BleakClient
from time import sleep
from struct import pack

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


class StateMachine:
    def __init__(self):
        self.state = "disconnected"
        self.loop = asyncio.get_event_loop()
        self.device_address = "00:11:22:33:44:55"  # Replace with your device address
        self.characteristic_uuid = "00002a37-0000-1000-8000-00805f9b34fb"  # Replace with your characteristic UUID
        self.reconnect_delay = 5  # Delay in seconds before attempting reconnection

    async def start(self):
        while True:
            if self.state == "disconnected":
                await self.disconnected_state()
            elif self.state == "connecting":
                await self.connecting_state()
            elif self.state == "connected":
                await self.connected_state()

    async def disconnected_state(self):
        if not self.device_address:
            print("Device address is not defined.")
            return

        print(f"Disconnected. Connecting to device: {self.device_address}")
        self.client = BleakClient(self.device_address)
        self.state = "connecting"

    async def connecting_state(self):
        if await self.client.connect():
            print("Connected.")
            self.state = "connected"
        else:
            print("Connection failed. Retrying...")
            await asyncio.sleep(1)  # Wait for a while before retrying

    async def connected_state(self):
        while self.state == "connected":
            # Data sending/receiving operations go here
            self.client.write_gatt_char(
                self.characteristic_uuid, get_config_packet(31, "0")
            )

            # Example: Perform periodic connection check
            if not await self.check_connection():
                print("Connection lost. Reconnecting...")
                self.state = "connecting"
                await asyncio.sleep(self.reconnect_delay)
                break

            # Example: Disconnect after receiving data
            data = await self.client.read_gatt_char(self.characteristic_uuid)
            if data:
                print(f"Received data: {data}")
                await self.client.disconnect()
                print("Disconnected.")
                self.state = "disconnected"

    async def check_connection(self):
        """Check if the client is still connected."""
        if not await self.client.is_connected():
            try:
                await self.client.connect()
                return await self.client.is_connected()
            except Exception as e:
                print(f"Reconnection failed: {e}")
                return False
        return True


if __name__ == "__main__":
    sm = StateMachine()
    sm.loop.run_until_complete(sm.start())
