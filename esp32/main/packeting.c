#include "sensors.c"
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "esp_system.h"
#include "esp_mac.h"
#include "esp_log.h"

#include <time.h>

extern char *dataprotocol0();
extern char *dataprotocol1();
extern char *dataprotocol2();
extern char *dataprotocol3();
unsigned short dataLength(char protocol);

/*
Tendra las funciones necesarias para armar el paquete de envio, este puede ser sola una función si prefiere incluirlo en otro de los archivos. Llamara a todo lo necesario desde Sensores. Se recomienda tener:
    - Header(protocolo), crea el header para cierto protocolo.
    - Body(protocolo), llama a las funciones de generación de dato y arma el cuerpo del mensaje.
    - Packet(protocolo), usando las funciones anteriores arma el paquete entero y lo deja preparado para envio.
*/

// Genera el header de un mensaje, con la MAC, el protocolo, status, y el largo del mensaje.
char *header(char protocol, char transportLayer)
{
  char *head = malloc(12);

  char *ID = "D1";
  memcpy((void *)&(head[0]), (void *)ID, 2);
  uint8_t *MACaddrs = malloc(6);
  esp_efuse_mac_get_default(MACaddrs);
  memcpy((void *)&(head[2]), (void *)MACaddrs, 6);
  head[8] = transportLayer;
  head[9] = protocol;
  unsigned short dataLen = dataLength(protocol);
  memcpy((void *)&(head[10]), (void *)&dataLen, 2);
  free(MACaddrs);
  return head;
}

unsigned short lengmsg[5] = {6, 16, 20, 44, 24016};
unsigned short dataLength(char protocol)
{
  return lengmsg[(unsigned short)protocol - 48];
}

unsigned short messageLength(char protocol)
{
  return 12 + dataLength(protocol);
}

char *mensaje(char protocol, char transportLayer)
{
  char *mnsj = malloc(messageLength(protocol));
  // mnsj[messageLength(protocol)-1]= '\0';
  char *hdr = header(protocol, transportLayer);
  char *data;
  switch (protocol)
  {
  case '0':
    data = dataprotocol0();
    break;
  case '1':
    data = dataprotocol1();
    break;
  case '2':
    data = dataprotocol2();
    break;
  case '3':
    data = dataprotocol3();
    break;
  default:
    data = dataprotocol0();
    break;
  }
  memcpy((void *)mnsj, (void *)hdr, 12);
  memcpy((void *)&(mnsj[12]), (void *)data, dataLength(protocol));
  free(hdr);
  free(data);

  return mnsj;
}

// Arma un paquete para el protocolo 0, con la bateria
char *dataprotocol0()
{

  char *msg = malloc(dataLength('0'));
  char val = '1';
  msg[0] = val;
  char batt = (void *)batt_sensor();
  msg[1] = batt;
  long t = time(NULL);
  memcpy((void *)&(msg[2]), (void *)&t, 4);
  return msg;
}

char *dataprotocol1()
{

  char *msg = malloc(dataLength('1'));
  char *msg0 = dataprotocol0();
  memcpy((void *)&(msg[0]), (void *)msg0, dataLength('0'));
  free(msg0);

  char temp = THPC_sensor_temp();
  msg[6] = temp;

  float press = THPC_sensor_pres();
  memcpy((void *)&(msg[7]), (void *)&press, 4);

  char hum = THPC_sensor_hum();
  msg[11] = hum;

  float co = THPC_sensor_co();
  memcpy((void *)&(msg[12]), (void *)&co, 4);

  return msg;
}

char *dataprotocol2()
{

  char *msg = malloc(dataLength('2'));
  char *msg1 = dataprotocol1();
  memcpy((void *)&(msg[0]), (void *)msg1, dataLength('1'));
  free(msg1);

  float amp_x = acc_kpi_amp_x();
  float amp_y = acc_kpi_amp_y();
  float amp_z = acc_kpi_amp_z();
  float rms = (float)sqrt(amp_x * amp_x + amp_y * amp_y + amp_z * amp_z);
  memcpy((void *)&(msg[16]), (void *)&rms, 4);

  return msg;
}

char *dataprotocol3()
{

  char *msg = malloc(dataLength('3'));
  char *msg1 = dataprotocol1();
  memcpy((void *)&(msg[0]), (void *)msg1, dataLength('1'));
  free(msg1);

  float amp_x = acc_kpi_amp_x();
  float amp_y = acc_kpi_amp_y();
  float amp_z = acc_kpi_amp_z();
  float rms = (float)sqrt(amp_x * amp_x + amp_y * amp_y + amp_z * amp_z);
  memcpy((void *)&(msg[16]), (void *)&rms, 4);

  memcpy((void *)&(msg[20]), (void *)&amp_x, 4);
  float frec_x = acc_kpi_frec_x();
  memcpy((void *)&(msg[24]), (void *)&frec_x, 4);

  memcpy((void *)&(msg[28]), (void *)&amp_y, 4);
  float frec_y = acc_kpi_frec_y();
  memcpy((void *)&(msg[32]), (void *)&frec_y, 4);

  memcpy((void *)&(msg[36]), (void *)&amp_z, 4);
  float frec_z = acc_kpi_frec_z();
  memcpy((void *)&(msg[40]), (void *)&frec_z, 4);

  return msg;
}
