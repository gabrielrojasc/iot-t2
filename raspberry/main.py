import pygatt
from time import sleep
from struct import pack

from unpacking import parse_data
from db import get_configs

# Definir los UUIDs de los servicios y características del dispositivo BLE
DEVICE_ADDRESS = "4C:EB:D6:62:18:3A"
SERVICE_UUID = "000000FF-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000FF01-0000-1000-8000-00805f9b34fb"

# Definir los estados de la máquina de estado
STATE_DISCONNECTED = 0
STATE_CONNECTING = 1
STATE_CONNECTED = 2

# Inicializar la conexión PyGatt y el estado inicial de la máquina de estado
adapter = pygatt.GATTToolBackend()
state = STATE_DISCONNECTED


# Función para manejar eventos de conexión
def handle_connection_event(event):
    global state
    if event == "disconnected":
        print("El dispositivo se desconectó")
        state = STATE_DISCONNECTED
    elif event == "connected":
        print("El dispositivo se conectó")
        state = STATE_CONNECTED


# Función para conectar al dispositivo BLE
def connect():
    global state
    state = STATE_CONNECTING
    device = adapter.connect(
        DEVICE_ADDRESS,
        address_type=pygatt.BLEAddressType.random,
        timeout=10,
        auto_reconnect=True,
    )
    device.subscribe(CHARACTERISTIC_UUID, callback=handle_notification)

    return device


# Función para desconectar del dispositivo BLE
def disconnect():
    global state
    state = STATE_DISCONNECTED
    adapter.stop()


# Función para manejar notificaciones de características
def handle_notification(handle, value):
    print("Notificación recibida:", value.hex())


# Bucle principal de la máquina de estado
while True:
    device = None
    if state == STATE_DISCONNECTED:
        # Si el estado actual es desconectado, intentar conectar
        try:
            device = connect()
        except:
            continue
    elif state == STATE_CONNECTING:
        # Si el estado actual es conectando, esperar hasta que se conecte o se agote el tiempo de espera
        try:
            adapter.start()
            sleep(1)
        except pygatt.exceptions.BLEError:
            pass
    elif state == STATE_CONNECTED and device is not None:
        # Si el estado actual es conectado, hacer cualquier operación necesaria en el dispositivo
        # transport_layer=10 -> Config
        # transport_layer=30 -> Continua
        # transport_layer=31 -> Discontinua
        for protocol, transport_layer in get_configs():
            print(f"Sending config: {protocol=}, {transport_layer}")
            packet = pack("<2c", str(protocol).encode(), str(transport_layer).encode())
            device.char_write(CHARACTERISTIC_UUID, packet, wait_for_response=True)

            print(f"Reading data...")
            raw_data = device.char_read(CHARACTERISTIC_UUID)
            print(f"Raw data received: {raw_data}")

            data = parse_data(raw_data, protocol)
            print(f"Data parse: {data}")


        sleep(1)
