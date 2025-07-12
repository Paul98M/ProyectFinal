import serial
import argparse
from datetime import datetime
from conexionBD import connectionBD
import sys
import time

def verificar_uid_en_bd(uid, conexion_db):
    try:
        with conexion_db.cursor(dictionary=True) as cursor:
            query = """
                SELECT u.id_usuario, u.nombre_usuario
                FROM tarjeta_rfid t
                JOIN usuarios u ON t.id_usuario = u.id_usuario
                WHERE t.tarjeta = %s AND t.estado = 'activo'
            """
            cursor.execute(query, (uid,))
            resultado = cursor.fetchone()
            if resultado:
                return resultado['id_usuario']
            return None
    except Exception as e:
        print(f"Error verificando UID: {e}")
        return None

def guardar_acceso(uid, id_usuario, conexion_db):
    try:
        with conexion_db.cursor() as cursor:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = "INSERT INTO accesos (fecha, clave, id_usuario) VALUES (%s, %s, %s)"
            cursor.execute(query, (now, uid, id_usuario))
            conexion_db.commit()
            print(f"✅ Acceso registrado para usuario {id_usuario} con UID {uid}")
    except Exception as e:
        print(f"❌ Error guardando acceso: {e}")

def guardar_lectura_rfid(uid, conexion_db):
    try:
        with conexion_db.cursor() as cursor:
            query = "INSERT INTO lecturas_rfid (tarjeta) VALUES (%s)"
            cursor.execute(query, (uid,))
            conexion_db.commit()
            print(f"📥 UID guardado en lecturas_rfid: {uid}")
    except Exception as e:
        print(f"❌ Error al guardar lectura RFID: {e}")

def enviar_comando_arduino(puerto_serial, comando):
    try:
        puerto_serial.write((comando + "\n").encode('utf-8'))
        print(f"📤 Comando enviado a Arduino: {comando}")
    except Exception as e:
        print(f"❌ Error enviando comando a Arduino: {e}")

def guardar_alerta_temperatura(valor_temp, conexion_db):
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
    print(f"🔄 Leyendo desde el puerto {puerto_serial.name}...")
    print("💳 Modo RFID y alerta sensores activado.")

    while True:
        try:
            if puerto_serial.in_waiting > 0:
                linea = puerto_serial.readline().decode('utf-8').strip()

                if linea.startswith("UID:"):
                    uid_limpio = linea[4:].strip().upper()
                    print(f"💳 UID de tarjeta recibido: {uid_limpio}")

                    with connectionBD() as conexion_MySQLdb:
                        guardar_lectura_rfid(uid_limpio, conexion_MySQLdb)  # 🔹 Se guarda en lecturas_rfid

                        id_usuario = verificar_uid_en_bd(uid_limpio, conexion_MySQLdb)
                        if id_usuario:
                            print(f"🔓 Acceso autorizado para usuario ID: {id_usuario}")
                            guardar_acceso(uid_limpio, id_usuario, conexion_MySQLdb)
                            enviar_comando_arduino(puerto_serial, "ABRIR")
                        else:
                            print("🔒 Acceso denegado.")
                            enviar_comando_arduino(puerto_serial, "DENEGAR")

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

                elif linea:
                    print(f"📭 Datos no relevantes recibidos: {linea}")

            time.sleep(0.1)

        except UnicodeDecodeError:
            print("⚠️ Error de decodificación. Verifica baudrate y codificación.")
        except Exception as e:
            print(f"❌ Error inesperado al leer del puerto serial: {e}")
            break

def main(port: str, baud: int):
    puerto = None
    try:
        puerto = serial.Serial(port=port, baudrate=baud, timeout=1)
        leer_datos_serial(puerto)
    except serial.SerialException as e:
        print(f"❌ Error al abrir el puerto serial '{port}': {e}")
        print("Verifica que el dispositivo esté conectado y el puerto sea el correcto.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Programa detenido por usuario.")
    finally:
        if puerto and puerto.is_open:
            puerto.close()
            print("🔌 Puerto serial cerrado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lector de tarjetas RFID y alertas desde sensores.")
    parser.add_argument('--port', default='COM7', help='Puerto serial (ej. COM6 o /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=9600, help='Baudrate del puerto serial.')

    args = parser.parse_args()
    main(port=args.port, baud=args.baud)
