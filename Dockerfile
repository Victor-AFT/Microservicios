
FROM python:3.11-slim

WORKDIR /app

# Copiamos requirements si existe (mejor para caching)
COPY requirements.txt /app/requirements.txt


# Instalar deps de Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copiamos el código de la API
COPY . /app

# Puerto en el que el contenedor escuchará (waitress lo usará)
EXPOSE 8080

CMD ["waitress-serve", "--listen=0.0.0.0:8080","--call", "app:create_app"]

