from controllers.funciones_login import *
from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error


# Importando cenexión a BD
from controllers.funciones_home import *

@app.route('/lista-de-areas', methods=['GET'])
def lista_areas():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_areas.html', areas=lista_areasBD(), dataLogin=dataLoginSesion())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_usuarios.html',  resp_usuariosBD=lista_usuariosBD(), dataLogin=dataLoginSesion(), areas=lista_areasBD(), roles = lista_rolesBD())
    else:
        return redirect(url_for('inicioCpanel'))

#Ruta especificada para eliminar un usuario
@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)

    if resp == "dependencia":
        flash("⚠️ No se puede eliminar el usuario porque tiene registros asociados en otras tablas.", "danger")
    elif resp:
        flash("✅ El Usuario fue eliminado correctamente", "success")
    else:
        flash("❌ Error al intentar eliminar el usuario.", "danger")

    return redirect(url_for('usuarios'))


@app.route('/borrar-area/<string:id_area>/', methods=['GET'])
def borrarArea(id_area):
    resp = eliminarArea(id_area)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_areas'))
    else:
        flash('Hay usuarios que pertenecen a esta área', 'error')
        return redirect(url_for('lista_areas'))


@app.route("/descargar-informe-accesos/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route("/reporte-accesos", methods=['GET'])
def reporteAccesos():
    if 'conectado' in session:
        userData = dataLoginSesion()
        return render_template('public/perfil/reportes.html',  reportes=dataReportes(),lastAccess=lastAccessBD(userData.get('cedula')), dataLogin=dataLoginSesion())

#CREAR AREA
@app.route('/crear-area', methods=['GET','POST'])
def crearArea():
    if request.method == 'POST':
        area_name = request.form['nombre_area']  # Asumiendo que 'nombre_area' es el nombre del campo en el formulario
        resultado_insert = guardarArea(area_name)
        if resultado_insert:
            # Éxito al guardar el área
            flash('El Area fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
            
        else:
            # Manejar error al guardar el área
            return "Hubo un error al guardar el área."
    return render_template('public/usuarios/lista_areas')

##ACTUALIZAR AREA
@app.route('/actualizar-area', methods=['POST'])
def updateArea():
    if request.method == 'POST':
        nombre_area = request.form['nombre_area']  # Asumiendo que 'nuevo_nombre' es el nombre del campo en el formulario
        id_area = request.form['id_area']
        resultado_update = actualizarArea(id_area, nombre_area)
        if resultado_update:
           # Éxito al actualizar el área
            flash('El actualizar fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
        else:
            # Manejar error al actualizar el área
            return "Hubo un error al actualizar el área."

    return redirect(url_for('lista_areas'))

# ===============================================
# MOSTRAR DATOS DEL SENSOR DE TEMPERATURA (GET)
@app.route('/temperatura', methods=['GET'])
def sensor_temp():
    if 'conectado' in session:
        try:
            # Obtiene los datos de los sensores de temperatura desde la base de datos
            datos_sensor_temperatura = sensor_temperatura()

            # Renderiza la plantilla con los datos
            return render_template('public/sensores/temperatura.html', datos_sensor_temperatura = sensor_temperatura(), dataLogin=dataLoginSesion())
        except Exception as e:
            flash(f"Error al obtener datos de sensor de temperatura: {e}", 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
# ===============================================
# ELIMINAR SENSOR DE TEMPERATURA DESDE LA RUTA
@app.route('/eliminar-sensor-temperatura/<int:id_sensor>', methods=['GET', 'POST'])
def eliminar_sensor_temperatura_route(id_sensor):
    try:
        # Llama a la función para eliminar el registro del sensor de temperatura
        eliminarSensorTemperatura(id_sensor)
        flash('Registro del sensor de temperatura eliminado con éxito.', 'success')
    except Exception as e:
        flash(f"Error al eliminar el registro del sensor de temperatura: {e}", 'error')

    # Redirige a la página principal o a donde desees después de la eliminación
    return redirect(url_for('inicio'))

# ============================================
# MOSTRAR DATOS DEL SENSOR DE HUMO (GET)
@app.route('/sensor-humo', methods=['GET'])
def sensor_hum():
    if 'conectado' in session:
        try:
            # Obtiene los datos de los sensores de temperatura desde la base de datos
            datos_sensor_humo = sensor_humo()

            # Renderiza la plantilla con los datos
            return render_template('public/sensores/humo.html', datos_sensor_humo = sensor_humo(), dataLogin=dataLoginSesion())
        except Exception as e:
            flash(f"Error al obtener datos de sensor de humo: {e}", 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
# ===============================================
# ELIMINAR REGISTRO DE SENSOR DE HUMO (GET/POST)
@app.route('/eliminar-sensor-humo/<int:id_sensor>', methods=['GET', 'POST'])
def eliminar_sensor_humo_route(id_sensor):
    try:
        # Llama a la función para eliminar el registro del sensor de humo
        eliminarSensorHumo(id_sensor)
        flash('Registro del sensor de humo eliminado con éxito.', 'success')
    except Exception as e:
        flash(f"Error al eliminar el registro del sensor de humo: {e}", 'error')

    # Redirige a la página principal o a donde desees después de la eliminación
    return redirect(url_for('inicio'))

# ============================================
# MOSTRAR REGISTROS DE ACCESOS RFID (GET)
@app.route('/accesos-rfid', methods=['GET'])
def tarjet():
    if 'conectado' in session:
        try:
            # Obtiene los datos de los sensores de temperatura desde la base de datos
            datos_tarjeta = tarjeta()

            # Renderiza la plantilla con los datos
            return render_template('public/sensores/TarjetaRFID.html', datos_tarjeta = tarjeta(), dataLogin=dataLoginSesion())
        except Exception as e:
            flash(f"Error al obtener datos registros de la tarjeta: {e}", 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
# =============================
# Obtiene lista de usuarios y renderiza la página de generación de clave (GET)
@app.route("/interfaz-clave", methods=['GET'])
def claves():
    usuarios = obtenerUsuarios()  # Esta función debe retornar una lista de usuarios
    return render_template('public/usuarios/generar_clave.html', usuarios=usuarios, dataLogin=dataLoginSesion())
    
# ================================
# RUTA: VALIDAR CLAVE TEMPORAL (POST), # Obtiene clave y cédula del formulario, valida, marca como usada y registra acceso  
@app.route('/validar-clave-temporal', methods=['POST'])
def validar_clave_temporal():
    clave_ingresada = request.form['clave'].strip()
    cedula_usuario = request.form.get('cedula', '').strip()  # uso get para evitar error si no viene
    print(">>> Clave recibida:", repr(clave_ingresada))  # DEBUG
    if cedula_usuario:
        print(">>> Cédula usuario:", cedula_usuario)
    # Asumo que validarClaveTemporal acepta opcionalmente cedula_usuario
    if cedula_usuario:
        clave_info = validarClaveTemporal(clave_ingresada, cedula_usuario)
    else:
        clave_info = validarClaveTemporal(clave_ingresada)
    print(">>> Resultado desde BD:", clave_info)  # DEBUG

    if clave_info:
        print(">>> Fecha vencimiento:", clave_info['vence_en'], "| Ahora:", datetime.now())
        id_clave = clave_info['id_clave']
        id_usuario = clave_info['id_usuario']
        marcarClaveComoUsada(id_clave)
        registrarAcceso(id_usuario, clave_ingresada)

        flash("¡Acceso concedido! Clave válida.", "success")
    else:
        flash("Clave inválida, vencida, usada o no te pertenece.", "danger")
    return redirect(url_for('ingresar_clave'))

# ================================================
# RUTA: GENERAR Y GUARDAR CLAVE TEMPORAL (GET/POST)
@app.route('/generar-y-guardar-clave/<string:id>', methods=['GET','POST'])
def generar_clave(id):
    clave_generada = crearClave()
    guardarClaveTemporal(clave_generada, id)  # Guarda la clave con duración de 2 minutos
    return clave_generada

# ===============================
# Renderiza la página donde el usuario ingresa la clave temporal
@app.route('/ingresar-clave', methods=['GET'])
def ingresar_clave():
    return render_template('public/usuarios/colocar_clave.html',  dataLogin=dataLoginSesion())





# ============================================
# SECCIÓN: BIBLIOTECA
# SECCIÓN: BIBLIOTECA
# SECCIÓN: BIBLIOTECA
# ============================================


# =====================================
# ELIMINAR LIBRO POR ID
# =====================================
@app.route('/borrar-libro/<string:id>', methods=['GET'])
def borrarLibro(id):
    eliminado = eliminarLibro(id)
    if eliminado:
        flash('✅ El libro fue eliminado correctamente.', 'success')
    else:
        flash('❌ Hubo un error al eliminar el libro.', 'danger')
    return redirect(url_for('libros1'))  # Asegúrate que este endpoint existe



# =====================================
# MOSTRAR FORMULARIO DE EDICIÓN DE LIBRO
# =====================================
@app.route("/editar-libro/<id_libro>", methods=['GET'])
def viewEditarLibro(id_libro):
    if 'conectado' in session:
        libro = buscarLibroUnico(id_libro)  # <--- Cambia aquí
        if libro:
            return render_template('public/biblioteca/form_libro_update.html', libro=libro, dataLogin=dataLoginSesion())
        else:
            flash('El libro no existe.', 'error')
            return redirect(url_for('libros1'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login'))


# =====================================
# ACTUALIZAR DATOS DE UN LIBRO
# =====================================
@app.route("/actualizar-libro", methods=['POST'])
def actualizarLibro():  
    if request.method == 'POST':
        try:
            id_libro = request.form['id_libro']
            titulo = request.form['titulo']
            autores = request.form['autores']
            categoria = request.form['categoria']
            ubicacion = request.form['ubicacion']
            cantidad_disponible = request.form.get('cantidad_disponible', 0)
            stock_total = request.form.get('stock_total', 0)
            anio_publicacion = request.form.get('anio_publicacion', None)
            estado = request.form.get('estado', 'activo')

            datos = {
                'titulo': titulo,
                'autores': autores,
                'ubicacion': ubicacion,
                'categoria': categoria,
                'cantidad_disponible': cantidad_disponible,
                'stock_total': stock_total,
                'anio_publicacion': anio_publicacion,
                'estado': estado
            }

            resultado_update = actualizarLibroBD(id_libro, datos)

            if resultado_update:
                flash('El libro fue actualizado correctamente.', 'success')
                return redirect(url_for('libros1'))
            else:
                flash('No se realizaron cambios en el libro.', 'error')
                return redirect(url_for('viewEditarLibro', id_libro=id_libro))

        except Exception as e:
            print(f"Error en actualizarLibro(): {e}")
            flash('Error en el formulario de actualización.', 'error')
            return redirect(url_for('libros1'))

    else:
        flash('Método no permitido.', 'error')
        return redirect(url_for('libros1'))
    
# ------------------------------------------------------------
# RUTA: LISTA DE LIBROS
# ------------------------------------------------------------
# lO MISMO DEL PRIMERO.  
@app.route("/lista-de-libros", methods=['GET'])
def libros1():
    if 'conectado' in session:
        return render_template(
            'public/biblioteca/lista_libros.html',
            libros=lista_librosBD(),      # <--- Cambia a 'libros'
            dataLogin=dataLoginSesion()
        )
    else:
        return redirect(url_for('inicioCpanel'))


    