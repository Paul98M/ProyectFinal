
# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD

import datetime
import re
import os

from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio


import openpyxl  # Para generar el excel
# biblioteca o modulo send_file para forzar la descarga
from flask import send_file, session

def accesosReporte():
    if session['rol'] == 1 :
        try:
            with connectionBD() as conexion_MYSQLdb:
                with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                    querySQL = ("""
                        SELECT a.id_acceso, u.cedula, a.fecha, r.nombre_area, a.clave 
                        FROM accesos a 
                        JOIN usuarios u 
                        JOIN area r
                        WHERE u.id_area = r.id_area AND u.id_usuario = a.id_usuario
                        ORDER BY u.cedula, a.fecha DESC
                                """) 
                    cursor.execute(querySQL)
                    accesosBD=cursor.fetchall()
                return accesosBD
        except Exception as e:
            print(
                f"Errro en la función accesosReporte: {e}")
            return None
    else:
        cedula = session['cedula']
        try:
            with connectionBD() as conexion_MYSQLdb:
                with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                    querySQL = ("""
                        SELECT 
                            a.id_acceso, 
                            u.cedula, 
                            a.fecha,
                            r.nombre_area, 
                            a.clave 
                            FROM accesos a 
                            JOIN usuarios u JOIN area r 
                            WHERE u.id_usuario = a.id_usuario AND u.id_area = r.id_area AND u.cedula = %s
                            ORDER BY u.cedula, a.fecha DESC
                                """) 
                    cursor.execute(querySQL,(cedula,))
                    accesosBD=cursor.fetchall()
                return accesosBD
        except Exception as e:
            print(
                f"Errro en la función accesosReporte: {e}")
            return None


def generarReporteExcel():
    dataAccesos = accesosReporte()
    wb = openpyxl.Workbook()
    hoja = wb.active

    # Agregar la fila de encabezado con los títulos
    cabeceraExcel = ("ID", "CEDULA", "FECHA", "ÁREA", "CLAVE GENERADA")

    hoja.append(cabeceraExcel)

    # Agregar los registros a la hoja
    for registro in dataAccesos:
        id_acceso = registro['id_acceso']
        cedula = registro['cedula']
        fecha = registro['fecha']
        area = registro['nombre_area']
        clave = registro['clave']

        # Agregar los valores a la hoja
        hoja.append((id_acceso, cedula, fecha,area, clave))

    fecha_actual = datetime.datetime.now()
    archivoExcel = f"Reporte_accesos_{session['cedula']}_{fecha_actual.strftime('%Y_%m_%d')}.xlsx"
    carpeta_descarga = "../static/downloads-excel"
    ruta_descarga = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), carpeta_descarga)

    if not os.path.exists(ruta_descarga):
        os.makedirs(ruta_descarga)
        # Dando permisos a la carpeta
        os.chmod(ruta_descarga, 0o755)

    ruta_archivo = os.path.join(ruta_descarga, archivoExcel)
    wb.save(ruta_archivo)

    # Enviar el archivo como respuesta HTTP
    return send_file(ruta_archivo, as_attachment=True)

def buscarAreaBD(search):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            a.id_area,
                            a.nombre_area
                        FROM area AS a
                        WHERE a.nombre_area LIKE %s 
                        ORDER BY a.id_area DESC
                    """)
                search_pattern = f"%{search}%"  # Agregar "%" alrededor del término de búsqueda
                mycursor.execute(querySQL, (search_pattern,))
                resultado_busqueda = mycursor.fetchall()
                return resultado_busqueda

    except Exception as e:
        print(f"Ocurrió un error en def buscarEmpleadoBD: {e}")
        return []


# Lista de Usuarios creados
def lista_usuariosBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_usuario, cedula, nombre_usuario, apellido_usuario, id_area, id_rol FROM usuarios"
                cursor.execute(querySQL,)
                usuariosBD = cursor.fetchall()
        return usuariosBD
    except Exception as e:
        print(f"Error en lista_usuariosBD : {e}")
        return []

def lista_areasBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_area, nombre_area FROM area"
                cursor.execute(querySQL,)
                areasBD = cursor.fetchall()
        return areasBD
    except Exception as e:
        print(f"Error en lista_areas : {e}")
        return []

# Eliminar usuario
def eliminarUsuario(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM usuarios WHERE id_usuario=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarUsuario : {e}")
        return []    

def eliminarArea(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM area WHERE id_area=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarArea : {e}")
        return []
    
def dataReportes():
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                SELECT a.id_acceso, u.cedula, a.fecha, r.nombre_area, a.clave 
                FROM accesos a 
                JOIN usuarios u 
                JOIN area r
                WHERE u.id_area = r.id_area AND u.id_usuario = a.id_usuario
                ORDER BY u.cedula, a.fecha DESC
                """
                cursor.execute(querySQL)
                reportes = cursor.fetchall()
        return reportes
    except Exception as e:
        print(f"Error en listaAccesos : {e}")
        return []

def lastAccessBD(id):
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT a.id_acceso, u.cedula, a.fecha, a.clave FROM accesos a JOIN usuarios u WHERE u.id_usuario = a.id_usuario AND u.cedula=%s ORDER BY a.fecha DESC LIMIT 1"
                cursor.execute(querySQL,(id,))
                reportes = cursor.fetchone()
                print(reportes)
        return reportes
    except Exception as e:
        print(f"Error en lastAcceso : {e}")
        return []
import random
import string
def crearClave():
    caracteres = string.ascii_letters + string.digits  # Letras mayúsculas, minúsculas y dígitos
    longitud = 6  # Longitud de la clave

    clave = ''.join(random.choice(caracteres) for _ in range(longitud))
    print("La clave generada es:", clave)
    return clave

def lista_rolesBD():
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM rol"
                cursor.execute(querySQL)
                roles = cursor.fetchall()
                return roles
    except Exception as e:
        print(f"Error en select roles : {e}")
        return []
##CREAR AREA
def guardarArea(area_name):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                    sql = "INSERT INTO area (nombre_area) VALUES (%s)"
                    valores = (area_name,)
                    mycursor.execute(sql, valores)
                    conexion_MySQLdb.commit()
                    resultado_insert = mycursor.rowcount
                    return resultado_insert 
        
    except Exception as e:
        return f'Se produjo un error en crear Area: {str(e)}' 
    
##ACTUALIZAR AREA
def actualizarArea(area_id, area_name):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                sql = """UPDATE area SET nombre_area = %s WHERE id_area = %s"""
                valores = (area_name, area_id)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                resultado_update = mycursor.rowcount
                return resultado_update 
        
    except Exception as e:
        return f'Se produjo un error al actualizar el área: {str(e)}'
    
# =============================================================
# FUNCIÓN: OBTENER DATOS HISTÓRICOS DE SENSORES DE TEMPERATURA  
def sensor_temperatura():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Modifica la consulta según la estructura de tu base de datos
                querySQL = "SELECT id_sensor, fecha_alerta, temperatura FROM sensor_temperatura_h"
                cursor.execute(querySQL)
                datos_sensor_temperatura = cursor.fetchall()
        return datos_sensor_temperatura
    except Exception as e:
        print(f"Error al obtener datos de sensores de temperatura: {e}")
        return []
    
# ==========================================================
# FUNCIÓN: ELIMINAR REGISTRO DE SENSOR DE TEMPERATURA POR ID
def eliminarSensorTemperatura(id_sensor):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM sensor_temperatura_h WHERE id_sensor=%s"
                cursor.execute(querySQL, (id_sensor,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarSensorTemperatura: {e}")
        return []
    
# =======================================================
# FUNCIÓN: OBTENER DATOS HISTÓRICOS DEL SENSOR DE HUMO
def sensor_humo():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Modifica la consulta según la estructura de tu base de datos
                querySQL = "SELECT id_sensor, fecha_alerta, valor FROM sensor_humo_m"
                cursor.execute(querySQL)
                datos_sensor_humo = cursor.fetchall()
        return datos_sensor_humo
    except Exception as e:
        print(f"Error al obtener datos de sensor de humo: {e}")
        return []
    
# ====================================================
# FUNCIÓN: ELIMINAR REGISTRO DE SENSOR DE HUMO POR ID
def eliminarSensorHumo(id_sensor):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM sensor_humo_m WHERE id_sensor=%s"
                cursor.execute(querySQL, (id_sensor,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarSensorHumo: {e}")
        return []

# =======================================================
# FUNCIÓN: OBTENER REGISTROS DE TARJETAS RFID DESDE BD
def tarjeta():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Modifica la consulta según la estructura de tu base de datos
                querySQL = "SELECT nombre, tarjeta, id_usuario, fecha_hora, estado, id_area FROM tarjeta_rfid ORDER BY fecha_hora DESC"
                cursor.execute(querySQL)
                datos_tarjeta = cursor.fetchall()
        return datos_tarjeta
    except Exception as e:
        print(f"Error al obtener registros de la tarjeta: {e}")
        return []


from datetime import datetime, timedelta

# ==========================================================
# Inserta una nueva clave temporal con tiempo de expiración en 2 minutos
def guardarClaveAuditoria(clave, id_usuario):
    tiempo_actual = datetime.now()
    vence_en = tiempo_actual + timedelta(minutes=2)  # ⚠️ Aquí defines los 2 minutos
    with connectionBD() as conexion_MYSQLdb:
        with conexion_MYSQLdb.cursor() as cursor:
            cursor.execute("""
                INSERT INTO claves_temporales (clave, id_usuario, creada_en, vence_en, usada)
                VALUES (%s, %s, %s, %s, FALSE)
            """, (clave, id_usuario, tiempo_actual, vence_en))
            conexion_MYSQLdb.commit()

# ====================================================
# FUNCIÓN: MARCAR CLAVE TEMPORAL COMO USADA POR SU ID

def marcarClaveComoUsada(id_clave):
    with connectionBD() as conexion_MYSQLdb:
        with conexion_MYSQLdb.cursor() as cursor:
            cursor.execute("""
                UPDATE claves_temporales SET usada = TRUE WHERE id_clave = %s
            """, (id_clave,))
            conexion_MYSQLdb.commit()

# ===============================================
# FUNCIÓN: REGISTRAR ACCESO DE USUARIO CON CLAVE
def registrarAcceso(id_usuario, clave):
    with connectionBD() as conexion_MYSQLdb:
        with conexion_MYSQLdb.cursor() as cursor:
            cursor.execute("""
                INSERT INTO accesos (fecha, clave, id_usuario) 
                VALUES (NOW(), %s, %s)
            """, (clave, id_usuario))
            conexion_MYSQLdb.commit()
    
# ==========================================================
# Consulta usuarios junto con el nombre de su rol desde la base de datos
def obtenerUsuarios():
    with connectionBD() as conexion_MYSQLdb:
        with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT u.id_usuario, u.nombre_usuario, u.cedula, r.nombre_rol
                FROM usuarios u
                JOIN rol r ON u.id_rol = r.id_rol
            """)
            usuarios = cursor.fetchall()
            return usuarios
        
# ============================================================
# FUNCIÓN: VALIDAR CLAVE TEMPORAL NO USADA Y NO VENCIDA POR CÉDULA
def validarClaveTemporal(clave_ingresada, cedula_usuario):
    with connectionBD() as conexion_MYSQLdb:
        with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT ct.*, u.cedula 
                FROM claves_temporales ct
                JOIN usuarios u ON ct.id_usuario = u.id_usuario
                WHERE ct.clave = %s AND ct.usada = FALSE AND u.cedula = %s
            """, (clave_ingresada, cedula_usuario))
            
            resultado = cursor.fetchone()

            if resultado:
                print(">>> Fecha en BD:", resultado['vence_en'], "| Fecha actual:", datetime.now())  # DEBUG

            # Verifica si aún está dentro del tiempo
            if resultado and resultado['vence_en'] > datetime.now():
                return resultado
            else:
                return None

# =========================================================
# Inserta una clave temporal válida por 2 minutos en la base de datos
def guardarClaveTemporal(clave, id_usuario):
    vence_en = datetime.now() + timedelta(minutes=2)  # Clave válida por 2 minutos
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                sql = """
                    INSERT INTO claves_temporales (clave, id_usuario, vence_en)
                    VALUES (%s, %s, %s)
                """
                valores = (clave, id_usuario, vence_en)
                cursor.execute(sql, valores)
                conexion_MYSQLdb.commit()
                return cursor.rowcount
    except Exception as e:
        print(f"Error al guardar clave temporal: {e}")
        return 0