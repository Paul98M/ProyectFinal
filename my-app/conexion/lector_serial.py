import serial
from datetime import datetime
from conexionBD import connectionBD


# Configurar puerto serial (ajusta 'COM5' según tu caso)
puerto = serial.Serial(port='COM6', baudrate=9600, timeout=1)

# Guardar temperatura en la base de datos
def guardar_temperatura(temperatura):
    try:
        temperatura = float(temperatura.strip())
        fecha_alerta = datetime.now()

        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                querySQL = """
                    INSERT INTO sensor_temperatura_h (fecha_alerta, temperatura)
                    VALUES (%s, %s)
                """
                cursor.execute(querySQL, (fecha_alerta, temperatura))
                conexion_MySQLdb.commit()

                print(f"✔ Temperatura {temperatura} guardada correctamente en la base de datos.")

    except ValueError:
        print(f"❌ Valor inválido recibido como temperatura: '{temperatura}'")
    except Exception as e:
        print(f"❌ Error al guardar temperatura: {e}")

# Bucle principal: leer datos del puerto serial
print("🔄 Esperando datos del sensor de temperatura...")
while True:
    try:
        if puerto.in_waiting > 0:
            linea = puerto.readline().decode('utf-8').strip()
            if "TEMPERATURA:" in linea:
                _, valor = linea.split(":", 1)
                valor = valor.replace("°C", "").strip()  # 🔥 Limpieza del dato
                print(f"📡 Dato recibido: {valor}")
                guardar_temperatura(valor)
            else:
                print(f"📭 Línea no válida: {linea}")
    except Exception as e:
        print(f"❌ Error al leer del puerto serial: {e}")



