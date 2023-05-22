#include <math.h>
#include <stdlib.h>
#include "esp_system.h"
#include "esp_mac.h"
#include "esp_log.h"

/*

Aqui generamos los 5 tipos de protocolos con sus datos.
Las timestamps en realidad siempre mandamos 0, y por comodidad
guardamos la timestampo del tiempo de llegada en el servidor de la raspberry.


En general los "mensajes" los creamos copiando a la mala (con memcpy) la memoria de los datos en un char*.
No es muy elegante pero funciona.

Al final lo único que se usa fuera de este archivo es:

message: dado un protocolo, crea un mensaje (con header y datos) codificado en un array de bytes (char*).
messageLength: dado un protocolo, entrega el largo del mensaje correspondiente

*/

float floatrand(float min, float max)
{
  return min + (float)rand() / (float)(RAND_MAX / (max - min));
}

float *acc_sensor_acc_x()
{
  float *arr = malloc(2000 * sizeof(float));
  for (int i = 0; i < 2000; i++)
  {
    float n = floatrand(-8000, 8000);
    arr[i] = 2.0 * sinf(2.0 * M_PI * 0.001 * n);
  }
  return arr;
}

float *acc_sensor_acc_y()
{
  float *arr = malloc(2000 * sizeof(float));
  for (int i = 0; i < 2000; i++)
  {
    float n = floatrand(-8000, 8000);
    arr[i] = 3.0 * cosf(2.0 * M_PI * 0.001 * n);
  }
  return arr;
}

float *acc_sensor_acc_z()
{
  float *arr = malloc(2000 * sizeof(float));
  for (int i = 0; i < 2000; i++)
  {
    float n = floatrand(-8000, 8000);
    arr[i] = 10.0 * sinf(2.0 * M_PI * 0.001 * n);
  }
  return arr;
}

char THPC_sensor_temp()
{
  char n = (char)(5 + (rand() % 26));
  return n;
}

char THPC_sensor_hum()
{
  char n = (char)(30 + (rand() % 51));
  return n;
}

float THPC_sensor_pres()
{
  float n = floatrand(1000, 1200);
  return n;
}

float THPC_sensor_co()
{
  float n = floatrand(30, 200);
  return n;
}

int batt_sensor()
{
  int n = 1 + rand() % 101;
  return n;
}

float acc_kpi_amp_x()
{
  float n = floatrand(0.0059, 0.12);
  return n;
}

float acc_kpi_frec_x()
{
  float n = floatrand(29.0, 31.0);
  return n;
}

float acc_kpi_amp_y()
{
  float n = floatrand(0.0041, 0.11);
  return n;
}

float acc_kpi_frec_y()
{
  float n = floatrand(59.0, 61.0);
  return n;
}

float acc_kpi_amp_z()
{
  float n = floatrand(0.008, 0.15);
  return n;
}

float acc_kpi_frec_z()
{
  float n = floatrand(89.0, 91.0);
  return n;
}
