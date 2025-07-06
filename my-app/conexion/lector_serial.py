import serial
import argparse
from datetime import datetime
from conexionBD import connectionBD
import sys
import time

def guardar_temperatura(temperatura_str: str, conexion_db):
    """
    Convierte y guarda la temperatura en la base de datos.
    """
    try:
        temperatura = float(temperatura_str)
        fecha_alerta = datetime.now()

        with conexion_db.cursor() as cursor:
            querySQL = """
                INSERT INTO sensor_temperatura_h (fecha_alerta, temperatura)
                VALUES (%s, %s)
            """
            cursor.execute(querySQL, (fecha_alerta, temperatura))
            conexion_db.commit()
            print(f"✔ Temperatura {temperatura}°C guardada correctamente.")

    except ValueError:
        print(f"❌ Valor inválido recibido como temperatura: '{temperatura_str}'")
    except Exception as e:
        print(f"❌ Error al guardar temperatura: {e}")

def guardar_tarjeta(uid_str: str, id_usuario: int or None, conexion_db):
    """
    Guarda una tarjeta RFID en la BD.
    Si se proporciona un id_usuario válido, vincula la tarjeta.
    Si no, la registra como 'Desconocido'.
    """
    try:
        with conexion_db.cursor() as cursor:
            # Verificar si la tarjeta ya existe
            query_check = "SELECT id_tarjeta FROM tarjeta_rfid WHERE tarjeta = %s"
            cursor.execute(query_check, (uid_str,))
            resultado = cursor.fetchone()
            if resultado:
                print(f"ℹ️  La tarjeta {uid_str} ya está registrada.")
                return

            if id_usuario:
                # Buscar datos del usuario
                query_user = "SELECT nombre_usuario, apellido_usuario, id_area FROM usuarios WHERE id_usuario = %s"
                cursor.execute(query_user, (id_usuario,))
                user_data = cursor.fetchone()

                if not user_data:
                    print(f"❌ No se encontró el usuario con ID {id_usuario}. Se registrará como 'Desconocido'.")
                    nombre_completo = "Desconocido"
                    id_usuario = None
                    id_area = None
                else:
                    nombre_completo = f"{user_data[0]} {user_data[1]}"
                    id_area = user_data[2]
            else:
                nombre_completo = "Desconocido"
                id_usuario = None
                id_area = None

            # Insertar tarjeta
            query_insert = """
                INSERT INTO tarjeta_rfid (tarjeta, id_usuario, nombre, id_area, estado)
                VALUES (%s, %s, %s, %s, 'activo')
            """
            cursor.execute(query_insert, (uid_str, id_usuario, nombre_completo, id_area))
            conexion_db.commit()
            print(f"✔ Tarjeta {uid_str} registrada como '{nombre_completo}'.")

    except Exception as e:
        print(f"❌ Error al guardar la tarjeta RFID: {e}")



def leer_datos_serial(puerto_serial, id_usuario: int = None):
    """
    Bucle principal para leer datos del puerto serial y procesarlos.
    """
    print(f"🔄 Intentando leer desde el puerto {puerto_serial.name}...")
    if id_usuario:
        print(f"👤 Modo de registro RFID activado para el usuario ID: {id_usuario}")
    else:
        print("🌡️  Modo de solo lectura de temperatura activado (no se registrarán tarjetas RFID).")

    while True:
        try:
            if puerto_serial.in_waiting > 0:
                linea = puerto_serial.readline().decode('utf-8').strip()
                
                if "TEMPERATURA:" in linea:
                    _, valor = linea.split(":", 1)
                    valor_limpio = valor.replace("°C", "").strip()
                    print(f"📡 Dato de temperatura recibido: {valor_limpio}")
                    
                    with connectionBD() as conexion_MySQLdb:
                        if conexion_MySQLdb:
                             guardar_temperatura(valor_limpio, conexion_MySQLdb)

                elif "UID detectado:" in linea:
                    _, uid_raw = linea.split(":", 1)
                    # El UID viene como "12 34 AB CD ", lo limpiamos y unimos.
                    uid_limpio = "".join(uid_raw.strip().upper().split())
                    print(f"💳 UID de tarjeta recibido: {uid_limpio}")

                    if id_usuario:
                        with connectionBD() as conexion_MySQLdb:
                            if conexion_MySQLdb:
                                guardar_tarjeta(uid_limpio, id_usuario, conexion_MySQLdb)
                    else:
                        print("⚠️  UID detectado, pero no se especificó un --user-id para registrar la tarjeta.")

                else:
                    if linea: # Solo imprimir si la línea no está vacía
                        print(f"📭 Datos no relevantes recibidos: {linea}")

            time.sleep(0.1) # Pequeña pausa para no saturar la CPU
        except UnicodeDecodeError:
            print("⚠️ Error de decodificación. Asegúrate de que el baudrate y la codificación son correctos.")
        except Exception as e:
            print(f"❌ Error inesperado al leer del puerto serial: {e}")
            break # Salir del bucle si hay un error grave

def main(port: str, baud: int, user_id: int = None):
    """
    Función principal que configura el puerto serie y comienza la lectura.
    """
    puerto = None
    try:
        puerto = serial.Serial(port=port, baudrate=baud, timeout=1)
        leer_datos_serial(puerto, user_id)
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
    parser = argparse.ArgumentParser(description="Lector de datos desde puerto serial (Temperatura y RFID).")
    parser.add_argument('--port', default='COM3', help='Puerto serial a utilizar (ej. COM6 en Windows, /dev/ttyUSB0 en Linux).')
    parser.add_argument('--baud', type=int, default=9600, help='Baudrate del puerto serial.')
    parser.add_argument('--user-id', type=int, help='(Opcional) ID del usuario para registrar una nueva tarjeta RFID.')
    
    args = parser.parse_args()
    
    main(port=args.port, baud=args.baud, user_id=args.user_id)
