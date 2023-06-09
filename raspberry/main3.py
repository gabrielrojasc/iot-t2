import asyncio
from time import sleep
from struct import pack
from bleak import BleakClient

DEVICE_ADDRESS = "4C:EB:D6:62:18:3A"
CHARACTERISTIC_UUID = "0000FF01-0000-1000-8000-00805f9b34fb"


def get_config_packet(status, protocol):
    return pack("<2c", status.encode(), protocol.encode())


def get_status_protocol_pairs():
    status_protocol_pairs = []
    for status in (31, 30):
        for protocol in range(4):
            status_protocol_pairs.append((status, str(protocol)))
    return status_protocol_pairs


def disconnected_callback(client):
    print("reconnecting...")
    client.connect()


class Client(BleakClient):
    async def connect(self):
        try:
            await super().connect()
        except Exception:
            print("reconnecting...")
            await self.connect()


async def main():
    status_protocol_pairs = get_status_protocol_pairs()
    for status, protocol in status_protocol_pairs:
        print(f"status: {status}, protocol: {protocol}")
        client = Client(
            DEVICE_ADDRESS, disconnected_callback=disconnected_callback, timeout=5
        )
        await client.connect()
        config_packet = get_config_packet(status, protocol)
        client.write_gatt_char(CHARACTERISTIC_UUID, config_packet)
        sleep(1)
        packet = client.read_gatt_char(CHARACTERISTIC_UUID)
        print(f"{packet=}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
