import traceback
from db import data_save
from struct import unpack, pack

# Documentación struct unpack,pack :https://docs.python.org/3/library/struct.html#
"""
Estas funciones se encargan de parsear y guardar los datos recibidos.
Usamos struct para pasar de un array de bytes a una lista de numeros/strings. (https://docs.python.org/3/library/struct.html)
(La ESP32 manda los bytes en formato little-endian, por lo que los format strings deben empezar con <)

-data_save: Guarda los datos en la BDD
-response: genera un OK para mandar de vuelta cuando se recibe un mensaje, con posibilidad de pedir que se cambie el status/protocol
-protUnpack: desempaca un byte array con los datos de un mensaje (sin el header)
-headerDict: Transforma el byte array de header (los primeros 10 bytes de cada mensaje) en un diccionario con la info del header
-dataDict: Transforma el byta array de datos (los bytes luego de los primeros 10) en un diccionario con los datos edl mensaje

"""

# Data Expected Length
DATA_EXPECTED_LEN = (6, 16, 20, 44, 24016)


def response(change: bool = False, status: int = 255, protocol: int = 255):
    OK = 1
    CHANGE = 1 if change else 0
    return pack("<BBBB", OK, CHANGE, status, protocol)


def parse_data(packet, expected_protocol: int):
    header = packet[:12]
    data = packet[12:]
    header = header_dict(header)
    data_dict = None
    if header is not None:
        protocol = header["protocol"]
        data_dict = get_data_dict(protocol, data)

    if data_dict is None:
        print("Error: data_dict is None")
        return None
    if header is None:
        print("Error: Header is None")
        return None

    data_save(header, data_dict)

    return {**header, **data_dict}


def prot_unpack(protocol: int, data):
    protocol_unpack = ["<2Bl", "<2BlBfBf", "<2BlBfBff", "<2BlBfB8f", "<2BlBfBf6000f"]
    array = unpack(protocol_unpack[protocol], data)
    if protocol == 4:
        pad = 7
        l_arr = 2000
        array = (
            *array[:pad],
            array[pad : pad + l_arr],
            array[pad + l_arr : pad + 2 * l_arr],
            array[pad + 2 * l_arr :],
        )
    return array


def header_dict(data):
    try:
        (
            id_device,
            M1,
            M2,
            M3,
            M4,
            M5,
            M6,
            transport_layer,
            protocol,
            leng_msg,
        ) = unpack("<2s6BccH", data)
    except Exception as e:
        traceback.print_exc()
        return None
    MAC = ":".join([hex(x)[2:] for x in [M1, M2, M3, M4, M5, M6]])
    return {
        "id_device": id_device,
        "MAC": MAC,
        "transport_layer": ord(transport_layer),
        "protocol": int(protocol),
        "length": leng_msg,
    }


def get_data_dict(protocol: int, data):
    if protocol not in [0, 1, 2, 3, 4, 5]:
        print("Error: protocol doesnt exist")
        return None

    p0 = ("Val: 1", "Batt_level", "Timestamp")
    p1 = (*p0, "Temp", "Press", "Hum", "Co")
    p2 = (*p1, "RMS")
    p3 = (*p2, "Amp_x", "Frec_x", "Amp_y", "Frec_y", "Amp_z", "Frec_z")
    p4 = (*p1, "Acc_x", "Acc_y", "Acc_z")
    p = (p0, p1, p2, p3, p4)

    try:
        unp = prot_unpack(protocol, data)
        keys = p[protocol]
        return {key: val for (key, val) in zip(keys, unp)}
    except Exception:
        print("Data unpacking Error:", traceback.format_exc())
        return None
