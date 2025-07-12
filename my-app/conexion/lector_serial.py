import serial
import argparse
from datetime import datetime
from conexionBD import connectionBD
import sys
import time

def guardar_tarjeta(uid, conexion_db):
    """
    Verifica si la tarjeta ya existe. Si no, la guarda como desconocida.
    Si existe y está activa, muestra el nombre del usuario.
    """
    try:
        with conexion_db.cursor() as cursor:
            # Buscar tarjeta por UID
            query_select = "SELECT t.id_usuario, u.nombre_usuario, u.apellido_usuario, t.estado FROM tarjeta_rfid t LEFT JOIN usuarios u ON t.id_usuario = u.id_usuario WHERE t.tarjeta = %s"
            cursor.execute(query_select, (uid,))
            resultado = cursor.fetchone()

            if resultado:
                if resultado["estado"] == "activo":
                    nombre = f"{resultado['nombre_usuario']} {resultado['apellido_usuario']}"
                    print(f"✅ Tarjeta autorizada. Usuario: {nombre}")
                else:
                    print("⚠️ Tarjeta registrada pero no activa. Acceso denegado.")
            else:
                # Insertar como tarjeta desconocida
                query_insert = "INSERT INTO tarjeta_rfid (tarjeta, estado) VALUES (%s, 'desconocido')"
                cursor.execute(query_insert, (uid,))
                conexion_db.commit()
                print("🆕 Tarjeta desconocida registrada.")

    except Exception as e:
        print(f"❌ Error al procesar tarjeta RFID: {e}")


def guardar_alerta_temperatura(valor_temp, conexion_db):
    """
    Guarda en la base de datos un registro de alerta de temperatura.
    """
    try:
        with conexion_db.cursor() as cursor:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = "INSERT INTO sensor_temperatura_h (fecha_alerta, temperatura) VALUES (%s, %s)"
            cursor.execute(query, (now, valor_temp))
            conexion_db.commit()
            print(f"🔥 Alerta de temperatura registrada: {valor_temp} °C")
    except Exception as e:
        print(f"❌ Error al guardar alerta de temperatura: {e}")

def guardar_alerta_gas(valor_gas, conexion_db):
    """
    Guarda en la base de datos un registro de alerta de gas/humo.
    """
    try:
        with conexion_db.cursor() as cursor:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = "INSERT INTO sensor_humo_m (fecha_alerta, valor) VALUES (%s, %s)"
            cursor.execute(query, (now, valor_gas))
            conexion_db.commit()
            print(f"🌫️ Alerta de gas registrada: {valor_gas}")
    except Exception as e:
        print(f"❌ Error al guardar alerta de gas: {e}")

def leer_datos_serial(puerto_serial):
    """
    Bucle principal para leer datos del puerto serial y procesarlos.
    """
    print(f"🔄 Leyendo desde el puerto {puerto_serial.name}...")
    print("💳 Modo RFID y alerta sensores activado.")

    while True:
        try:
            if puerto_serial.in_waiting > 0:
                linea = puerto_serial.readline().decode('utf-8').strip()

                # Procesar UID de tarjeta
                if "UID:" in linea:
                    _, uid_raw = linea.split(":", 1)
                    uid_limpio = "".join(uid_raw.strip().upper().split())
                    print(f"💳 UID de tarjeta recibido: {uid_limpio}")

                    with connectionBD() as conexion_MySQLdb:
                        if conexion_MySQLdb:
                            guardar_tarjeta(uid_limpio, conexion_MySQLdb)

                # Procesar alerta desde Arduino
                elif "ALERTA|" in linea:
                    try:
                        partes = linea.split('|')
                        temp = float(partes[1].split(':')[1])
                        gas = float(partes[2].split(':')[1])

                        with connectionBD() as conexion_MySQLdb:
                            if temp > 24:
                                guardar_alerta_temperatura(temp, conexion_MySQLdb)
                            if gas > 5:
                                guardar_alerta_gas(gas, conexion_MySQLdb)

                    except Exception as e:
                        print(f"❌ Error al procesar datos de alerta: {e}")

                # Otras líneas no relevantes
                elif linea:
                    print(f"📭 Datos no relevantes recibidos: {linea}")

            time.sleep(0.1)

        except UnicodeDecodeError:
            print("⚠️ Error de decodificación. Verifica baudrate y codificación.")
        except Exception as e:
            print(f"❌ Error inesperado al leer del puerto serial: {e}")
            break

def main(port: str, baud: int):
    """
    Función principal que configura el puerto serie y comienza la lectura.
    """
    puerto = None
    try:
        puerto = serial.Serial(port=port, baudrate=baud, timeout=1)
        leer_datos_serial(puerto)
    except serial.SerialException as e:
        print(f"❌ Error al abrir el puerto serial '{port}': {e}")
        print("Verifica que el dispositivo esté conectado y el puerto sea el correcto.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Programa interrumpido por el usuario.")
    finally:
        if puerto and puerto.is_open:
            puerto.close()
            print("🔌 Puerto serial cerrado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lector de tarjetas RFID y alertas desde sensores.")
    parser.add_argument('--port', default='COM5', help='Puerto serial (ej. COM6 o /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=9600, help='Baudrate del puerto serial.')

    args = parser.parse_args()
    main(port=args.port, baud=args.baud)
