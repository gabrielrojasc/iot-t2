import sys
from time import sleep
from threading import Event
from struct import pack
from gattlib import GATTRequester, BTIOException

DEVICE_ADDRESS = "4C:EB:D6:62:18:3A"
SERVICE_UUID = "000000FF-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000FF01-0000-1000-8000-00805f9b34fb"
READ_HANDLE = 42
WRITE_HANDLE = 43


class Requester(GATTRequester):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wakeup = Event()

    def on_notification(self, handle, data):
        print("- notification on handle: {}\n".format(handle))
        print(f"{data=}")
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


def main():
    status = input("Status: ")
    protocol = input("Protocol: ")
    while True:
        try:
            if not req.is_connected():
                req.connect(True)
                print("connected")

            # write config
            req.write_by_handle(WRITE_HANDLE, get_config_packet(status, protocol))
            rec_not = ReceiveNotification(req)

            rec_not.wait_notification()
            sleep(1)
        except BTIOException:
            print("Error de conexión")
            sleep(1)
            continue


if __name__ == "__main__":
    main()
