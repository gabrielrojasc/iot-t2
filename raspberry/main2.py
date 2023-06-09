import sys
from time import sleep
from threading import Event
from struct import pack
from gattlib import GATTRequester, BTIOException, GATTException

DEVICE_ADDRESS = "4C:EB:D6:62:18:3A"
SERVICE_UUID = "000000FF-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000FF01-0000-1000-8000-00805f9b34fb"
CHAR_HANDLE = 42


class Requester(GATTRequester):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wakeup = Event()

    def on_notification(self, handle, data):
        print(f"{handle=}, {data=}")
        if data:
            self.check_connected()
            packet = self.read_by_handle(handle)
            print(f"{packet=}")
        else:
            print("no leyendo")
        self.wakeup.set()

    def check_connected(self):
        if not self.is_connected():
            try:
                self.connect(True)
                print("connected")
            except BTIOException:
                print("reconnecting...")
                sleep(1.5)
                self.check_connected()


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
            req.check_connected()
            try:
                req.write_by_handle(
                    CHAR_HANDLE, get_config_packet(chr(status), protocol)
                )
            except GATTException:
                print("No recibimos respuesta del write")

            for _ in range(3):
                sleep(3)
                req.check_connected()
                rec_not = ReceiveNotification(req)
                rec_not.wait_notification()

            req.check_connected()
            req.write_by_handle(CHAR_HANDLE, get_config_packet(chr(10), "0"))
            break


if __name__ == "__main__":
    main()
