import sys
from time import sleep
from threading import Event
from struct import pack
from gattlib import GATTRequester, BTIOException

DEVICE_ADDRESS = "4C:EB:D6:62:18:3A"
SERVICE_UUID = "000000FF-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000FF01-0000-1000-8000-00805f9b34fb"
CHAR_HANDLE = 42


class Requester(GATTRequester):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wakeup = Event()

    def on_notification(self, handle, data):
        print("{handle=}, {data=}")
        if data:
            packet = self.read_by_handle(handle)
            print(f"{packet=}")
        self.wakeup.set()


class ReceiveNotification(object):
    def __init__(self, req):
        self.requester = req
        self.received = self.requester.wakeup
        self.wait_notification()

    def connect(self):
        print("Connecting...", end=" ")
        sys.stdout.flush()

        self.requester.connect(True)
        print("OK!")

    def wait_notification(self):
        print(
            "\nThis is a bit tricky. You need to make your device to send\n"
            "some notification. I'll wait..."
        )
        self.received.wait()


req = Requester(DEVICE_ADDRESS, False)


def get_config_packet(status, protocol):
    return pack("<2c", status.encode(), protocol.encode())


def get_status_protocol_pairs():
    status_protocol_pairs = []
    for status in (31, 30):
        for protocol in range(4):
            status_protocol_pairs.append((status, str(protocol)))
    return status_protocol_pairs


def main():
    for status, protocol in get_status_protocol_pairs():
        print(f"{status=}, {protocol=}")
        while True:
            try:
                if not req.is_connected():
                    req.connect(True)
                    print("connected")

                # write config
                req.write_by_handle(
                    CHAR_HANDLE, get_config_packet(chr(status), protocol)
                )
                for _ in range(3):
                    rec_not = ReceiveNotification(req)
                    rec_not.wait_notification()
                req.write_by_handle(CHAR_HANDLE, get_config_packet(chr(10), "0"))
                break
            except BTIOException:
                print("Error de conexión")
                sleep(1.5)
                continue


if __name__ == "__main__":
    main()
