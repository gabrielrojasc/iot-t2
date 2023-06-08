from time import sleep
from struct import pack
from gattlib import GATTRequester, BTIOException

DEVICE_ADDRESS = "4C:EB:D6:62:18:3A"
SERVICE_UUID = "000000FF-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000FF01-0000-1000-8000-00805f9b34fb"
READ_HANDLE = 42
WRITE_HANDLE = 43


# Inicializar la conexión PyGatt y el estado inicial de la máquina de estado


class MyRequester(GATTRequester):
    ...


req = MyRequester(DEVICE_ADDRESS, False)


def get_config_packet(profile, protocol, status):
    return pack("<3B", profile, protocol.encode(), status)


# Bucle principal de la máquina de estado
while True:
    try:
        if not req.is_connected():
            req.connect(True)
        else:
            print("connected")

        # write config
        req.write_by_handle(WRITE_HANDLE, get_config_packet(1, "1", 30))

        req.read()

        sleep(1)
    except BTIOException:
        print("Error de conexión")
        sleep(1)
        continue
