# Imagen base
FROM python:3.11-slim-buster

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias primero para aprovechar caché
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer el puerto del servidor Flask
EXPOSE 8080

# Variable de entorno
ENV FLASK_APP=my-app/run.py

# Comando de arranque
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
