# Tarea 2 IoT

Integrantes:

- Alfredo Escobar
- Gabriel Rojas
- Nicolas Santibañez

## Aclaración uso maquina de estados y tabla Loss

Al empezar el proyecto no se utiliza una maquina de estados, pero la forma y lugares
donde se checkea si la conexion sigue activa es la misma que se utiliza en la
maquina de estados, por lo que la tabla Loss en verdad muestra los mismos datos para
el funcionamiento con maquina de estados y sin maquina de estados.

### Tabla Loss, sin maquina de estados:

| id_loss | time_to_connect  | connection_attempts |
| ------- | ---------------- | ------------------- |
| 1       | 39.2454037666321 | 39                  |
| 2       | 10.4346289634705 | 25                  |
| 3       | 31.9865679740906 | 32                  |
| 4       | 16.3069179058075 | 34                  |
| 5       | 31.4057264328003 | 13                  |
| 6       | 27.0578258037567 | 3                   |

### Tabla Loss, con maquina de estados:

| id_loss | time_to_connect  | connection_attempts |
| ------- | ---------------- | ------------------- |
| 1       | 1.46856284141541 | 1                   |
| 2       | 1.18323016166687 | 1                   |
| 3       | 6.03142619132996 | 6                   |
| 4       | 13.7802927494049 | 29                  |
| 5       | 71.5726852416992 | 92                  |
| 6       | 38.566068649292  | 26                  |

Podemos ver que los resultados de tiempo de conexion e intentos de conexion son un poco aleatorios, pero en general se puede ver que con maquina de estados se logra una conexion mas rapida y con menos intentos.

## Como correr el programa

### ESP

Para correr el codigo de la esp, se debe ir a la carpeta esp32 y correr:

```
idf.py build flash monitor
```

### Raspberry

Paquetes necesarios (pip):

- [bleak](https://bleak.readthedocs.io/en/latest)

Para correr el codigo de la raspberry en modo DEMO, se debe ir a la carpeta raspberry y correr:

El modo DEMO es correr la tarea con protocol 3 y cambiar entre el status 30 y 31.

```
DEMO=1 python3 main3.py
```
