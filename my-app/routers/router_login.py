
from app import app
from flask import render_template, request, flash, redirect, url_for, session
from flask import jsonify

# Importando mi conexión a BD
from conexion.conexionBD import connectionBD

# Para encriptar contraseña generate_password_hash
from werkzeug.security import check_password_hash

# Importando controllers para el modulo de login
from controllers.funciones_login import *
from controllers.funciones_home import *
PATH_URL_LOGIN = "/public/login"


@app.route('/', methods=['GET'])
def inicio():
    if 'conectado' in session:
        return render_template('public/base_cpanel.html', dataLogin=dataLoginSesion())
    else:
        return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/mi-perfil/<string:id>', methods=['GET'])
def perfil(id):
    if 'conectado' in session:
        
        return render_template(f'public/perfil/perfil.html', info_perfil_session=info_perfil_session(id), dataLogin=dataLoginSesion(), areas=lista_areasBD(), roles=lista_rolesBD())
    else:
        return redirect(url_for('inicio'))


# Crear cuenta de usuario
@app.route('/register-user', methods=['GET'])
def cpanelRegisterUser():
        return render_template(f'{PATH_URL_LOGIN}/auth_register.html',dataLogin = dataLoginSesion(),areas=lista_areasBD(), roles=lista_rolesBD())


# Recuperar cuenta de usuario
@app.route('/recovery-password', methods=['GET'])
def cpanelRecoveryPassUser():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_forgot_password.html')


# Crear cuenta de usuario
@app.route('/saved-register', methods=['POST'])
def cpanelRegisterUserBD():
    if request.method == 'POST' and 'cedula' in request.form and 'pass_user' in request.form:
        cedula = request.form['cedula']
        name = request.form['name']
        surname = request.form['surname']
        id_area = request.form['selectArea']
        id_rol = request.form['selectRol']
        pass_user = request.form['pass_user']

        resultData = recibeInsertRegisterUser(
            cedula, name, surname, id_area,id_rol,pass_user)
        if (resultData != 0):
            flash('la cuenta fue creada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            return redirect(url_for('inicio'))
    else:
        flash('el método HTTP es incorrecto', 'error')
        return redirect(url_for('inicio'))


# Actualizar datos de mi perfil
@app.route("/actualizar-datos-perfil/<int:id>", methods=['POST'])
def actualizarPerfil(id):
    if request.method == 'POST':
        if 'conectado' in session:
            respuesta = procesar_update_perfil(request.form,id)
            if respuesta == 1:
                flash('Los datos fuerón actualizados correctamente.', 'success')
                return redirect(url_for('inicio'))
            elif respuesta == 0:
                flash(
                    'La contraseña actual esta incorrecta, por favor verifique.', 'error')
                return redirect(url_for('perfil',id=id))
            elif respuesta == 2:
                flash('Ambas claves deben se igual, por favor verifique.', 'error')
                return redirect(url_for('perfil',id=id))
            elif respuesta == 3:
                flash('La Clave actual es obligatoria.', 'error')
                return redirect(url_for('perfil',id=id))
            else: 
                flash('Clave actual incorrecta', 'error')
                return redirect(url_for('perfil',id=id))
        else:
            flash('primero debes iniciar sesión.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Validar sesión
@app.route('/login', methods=['GET', 'POST'])
def loginCliente():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        if request.method == 'POST' and 'cedula' in request.form and 'pass_user' in request.form:

            cedula = str(request.form['cedula'])
            pass_user = str(request.form['pass_user'])
            conexion_MySQLdb = connectionBD()
            print(conexion_MySQLdb)
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM usuarios WHERE cedula = %s", [cedula])
            account = cursor.fetchone()

            if account:
                if check_password_hash(account['password'], pass_user):
                    # Crear datos de sesión, para poder acceder a estos datos en otras rutas
                    session['conectado'] = True
                    session['id'] = account['id_usuario']
                    session['name'] = account['nombre_usuario']
                    session['cedula'] = account['cedula']
                    session['rol'] = account['id_rol']

                    flash('la sesión fue correcta.', 'success')
                    return redirect(url_for('inicio'))
                else:
                    # La cuenta no existe o el nombre de usuario/contraseña es incorrecto
                    flash('datos incorrectos por favor revise.', 'error')
                    return render_template(f'{PATH_URL_LOGIN}/base_login.html')
            else:
                flash('el usuario no existe, por favor verifique.', 'error')
                return render_template(f'{PATH_URL_LOGIN}/base_login.html')
        else:
            flash('primero debes iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/closed-session',  methods=['GET'])
def cerraSesion():
    if request.method == 'GET':
        if 'conectado' in session:
            # Eliminar datos de sesión, esto cerrará la sesión del usuario
            session.pop('conectado', None)
            session.pop('id', None)
            session.pop('name_surname', None)
            session.pop('email', None)
            flash('tu sesión fue cerrada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('recuerde debe iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')


# =====================================
# Mostrar formulario para registrar un libro
# Método: GET
# =====================================
@app.route('/register-libro', methods=['GET', 'POST'])
def cpanelRegisterlibro():
    if request.method == 'POST':
        # ... guardar libro en BD ...

        flash('Libro creado exitosamente', 'success')
        return redirect(url_for('libros1'))

    # GET muestra formulario
    return render_template(f'{PATH_URL_LOGIN}/auth_registerlibro.html', dataLogin=dataLoginSesion(), areas=lista_areasBD(), roles=lista_rolesBD())

    

# =====================================
# Procesar formulario de registro de libro
# Método: POST
# =====================================
from flask import request, redirect, url_for, flash

@app.route('/registrar-libro', methods=['POST'])
def cpanelRegisterLibroBD():
    # Recibir datos enviados desde el formulario HTML
    titulo = request.form['titulo']
    autor = request.form['autor']
    anio = request.form['anio']
    categoria = request.form['categoria']
    ubicacion = request.form['ubicacion']
    stock_total = int(request.form['stock_total'])
    estado = request.form['estado']

    cantidad_disponible = stock_total  # Al principio es igual al stock total
    id_libro = generar_id_unico()      # Generar ID estilo L-01

    # Insertar en la base de datos
    query = """
        INSERT INTO libros (
            id_libro, titulo, autores, ubicacion, categoria,
            cantidad_disponible, stock_total, anio_publicacion, estado
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    datos = (
        id_libro, titulo, autor, ubicacion, categoria,
        cantidad_disponible, stock_total, anio, estado
    )

    try:
        with connectionBD() as db:
            with db.cursor() as cursor:
                cursor.execute(query, datos)
            db.commit()

        # Mensaje flash éxito
        flash('¡Felicitaciones! ✅ El libro fue registrado correctamente. ', 'success')
    except Exception as e:
        # Si hay error, puedes capturarlo y mostrar mensaje de error
        flash(f'Error al registrar el libro: {str(e)}', 'danger')

    return redirect(url_for('libros1'))
