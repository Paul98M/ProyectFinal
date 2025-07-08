import serial
import argparse
from datetime import datetime
from conexionBD import connectionBD
import sys
import time

def guardar_tarjeta(uid_str: str, conexion_db):
    """
    Registra la lectura de una tarjeta RFID en la base de datos.
    Si la tarjeta ya existe, usa su id_usuario y nombre.
    Si no, la inserta como 'Desconocido' con id_usuario NULL.
    """
    try:
        with conexion_db.cursor() as cursor:
            # Buscar si la tarjeta ya existe
            query_check = "SELECT id_usuario, nombre FROM tarjeta_rfid WHERE tarjeta = %s"
            cursor.execute(query_check, (uid_str,))
            resultado = cursor.fetchone()

            # *** FIX: Cerrar resultados pendientes antes de siguiente execute ***
            cursor.fetchall()

            if resultado:
                id_usuario, nombre = resultado
                print(f"✔ Tarjeta {uid_str} registrada anteriormente. Usuario: {nombre}")
            else:
                id_usuario = None
                nombre = "Desconocido"
                print(f"⚠️ Tarjeta {uid_str} no registrada previamente. Se guardará como 'Desconocido'.")

            # Insertar registro en la tabla tarjeta_rfid como log de acceso
            query_insert = """
                INSERT INTO tarjeta_rfid (tarjeta, id_usuario, nombre, estado)
                VALUES (%s, %s, %s, 'activo')
            """
            cursor.execute(query_insert, (uid_str, id_usuario, nombre))
            conexion_db.commit()
            print(f"💾 Registro de acceso guardado correctamente. UID: {uid_str}")

    except Exception as e:
        print(f"❌ Error al guardar la tarjeta RFID: {e}")


def leer_datos_serial(puerto_serial):
    """
    Bucle principal para leer datos del puerto serial y procesarlos.
    """
    print(f"🔄 Intentando leer desde el puerto {puerto_serial.name}...")
    print("💳 Modo de lectura de tarjetas RFID activado.")

    while True:
        try:
            if puerto_serial.in_waiting > 0:
                linea = puerto_serial.readline().decode('utf-8').strip()
                
                if "UID:" in linea:
                    _, uid_raw = linea.split(":", 1)
                    # Limpiar y unir el UID recibido
                    uid_limpio = "".join(uid_raw.strip().upper().split())
                    print(f"💳 UID de tarjeta recibido: {uid_limpio}")

                    with connectionBD() as conexion_MySQLdb:
                        if conexion_MySQLdb:
                            guardar_tarjeta(uid_limpio, conexion_MySQLdb)

                else:
                    if linea: # Solo imprimir si la línea no está vacía
                        print(f"📭 Datos no relevantes recibidos: {linea}")

            time.sleep(0.1) # Pequeña pausa para no saturar la CPU
        except UnicodeDecodeError:
            print("⚠️ Error de decodificación. Asegúrate de que el baudrate y la codificación son correctos.")
        except Exception as e:
            print(f"❌ Error inesperado al leer del puerto serial: {e}")
            break # Salir del bucle si hay un error grave

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
        print("Asegúrate de que el dispositivo esté conectado y el puerto sea el correcto.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Programa interrumpido por el usuario. Cerrando...")
    finally:
        if puerto and puerto.is_open:
            puerto.close()
            print("🔌 Puerto serial cerrado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lector de tarjetas RFID desde puerto serial.")
    parser.add_argument('--port', default='COM3', help='Puerto serial a utilizar (ej. COM6 en Windows, /dev/ttyUSB0 en Linux).')
    parser.add_argument('--baud', type=int, default=9600, help='Baudrate del puerto serial.')
    
    args = parser.parse_args()
    
    main(port=args.port, baud=args.baud)
