# Autor: Victor Fuentes Toledo
# Fecha: 2025-12-09
# Descripción: PC3

from . import models
from sqlalchemy import create_engine, text
import json
from datetime import datetime
from imagekitio import ImageKit
import requests
import base64
import uuid
from pathlib import Path
import os
import logging

#FUNCIONES
#ESTA FUNCION NO ES NECESARIA
file_json_pss='/app/credentials.json'
UPLOAD_FOLDER = "/app/"

logging.basicConfig(
        filename='/app/app.log',
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(message)s'
    )
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def obten_fecha_actual():

    FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"
    ahora = datetime.now()
    fecha_formateada = ahora.strftime(FORMATO_FECHA)
    return fecha_formateada

def write_log(message, level="info"):
    if level == "info":
        logger.info(message)
    elif level == "error":
        logger.error(message)
    elif level == "debug":
        logger.debug(message)
    else:
        logger.warning(message)


def leer_json(fichero):
    write_log(f"uso de la funcion Leer_json {fichero}", level="debug")
    try:
        with open(fichero, 'r', encoding='utf-8') as archivo_json:
            data = json.load(archivo_json)
        return data
    except Exception as e:
        #write_log(f"error funcion leer_json: {e}", level="error")
        print(f"Ocurrió un error: {e}")
        return None      
    
#DEVUELVE LA URL  DE LA IMAGEN
def image_url(uuid,extension,image_strbase64):
    
    write_log(f"Entrada de datos en al funcion image_url", level="debug")
    credentials = leer_json(file_json_pss)

    imagekit = ImageKit(
    public_key=credentials["imagekit"]["public_key"],
    private_key=credentials["imagekit"]["private_key"],
    url_endpoint = credentials["imagekit"]["url_endpoint"]
    )

    try:
        name_image = f"{uuid}.{extension}"
        upload_info=imagekit.upload(file=image_strbase64, file_name=name_image)
        write_log(f"uso de la funcion image_url {upload_info.url}", level="debug")
        return {
            "url": upload_info.url,
            "file_id": upload_info.file_id
        }
    
    except Exception as e:
        #print(f"Error en la funcion image_url: {e}")
        write_log(f"Error en la funcion image_url: {e}", level="error")
        return None
    
def delete_image_url(image_url):
    
    credentials = leer_json(file_json_pss)
    write_log(f"uso de la funcion delete_image_url", level="debug")
    imagekit = ImageKit(
    public_key=credentials["imagekit"]["public_key"],
    private_key=credentials["imagekit"]["private_key"],
    url_endpoint = credentials["imagekit"]["url_endpoint"]
    )
    try:
        imagekit.delete_file(file_id=image_url)
        write_log(f"Borrado de la url", level="debug")
    except Exception as e:
        #print(f"Error en la funcion delete_image_url: {e}")
        write_log(f"Error en la funcion delete_image_url: {e}", level="error")
    return None


def image_tags(image_url,image_file_id,min_confidence):
        write_log(f"uso de la funcion image_tags", level="debug")
        credentials = leer_json(file_json_pss)
        api_key = credentials["imagga"]["api_key"]
        api_secret = credentials["imagga"]["api_secret"]

        response = requests.get(f"https://api.imagga.com/v2/tags?image_url={image_url}", auth=(api_key, api_secret))
        try:
            tags = [
                        {
                            "tag": t["tag"]["en"],
                            "confidence": t["confidence"]
                        }
                        for t in response.json()["result"]["tags"]
                        if t["confidence"] > min_confidence
                    ]
            write_log(f"se ha obtenido los siguientes tags: {tags}", level="debug")
            delete_image_url(image_file_id)
            return tags
        except Exception as e:
            #print(f"Error en la funcion image_tags: {e}")
            write_log(f"Error en la funcion image_tags: {e}", level="error")
            return None
#FALTA LA FUNCION PARA ELIMINAR EL RASTRO DE LA WEB

# DEVUELVE EL TAMAÑO DE LA IMAGEN
def image_size(ruta_imagen):
    try:
        if not ruta_imagen:
            write_log(f"La ruta de la imagen esta vacia: {e}", level="error")

        size_bytes=os.path.getsize(ruta_imagen)
        size_kb=size_bytes/1024
        write_log(f"uso de la funcion image_size", level="debug")
        return size_kb
    
    except Exception as e:
            #print(f"Ocurrió un error: {e}")
            write_log(f"Error en la funcion image_size: {e}", level="error")
            return None


#DEVUEVE LA IMAGEN COMO STRING EN BASE64
def imagen_base64(ruta_imagen):
    try:
        with open(ruta_imagen, mode="rb") as img:
                imgstr = base64.b64encode(img.read())
        write_log(f"uso de la funcion imagen_base64 ", level="debug")
        return imgstr
    except Exception as e:
            write_log(f"Error en la funcion imagen_base64: {e}", level="error")
            return None
    
#GUARDA LA IMAGEN DESDE EL JSON
def guardar_imagen_json(uuid,data,extension):
    write_log(f"uso de la funcion guardar_imagen_json", level="debug")
    try:
        
        imagen_bytes=base64.b64decode(data)
        os.makedirs(UPLOAD_FOLDER,exist_ok=True)
        ruta_imagen=os.path.join(UPLOAD_FOLDER,f"{uuid}{extension}")
        write_log(f"guardando imagen en la ruta:  {ruta_imagen}", level="debug")
        with open(ruta_imagen,"wb") as imagen_file:
             imagen_file.write(imagen_bytes)
        
        return ruta_imagen     

    except Exception as e:
            write_log(f"Error en la funcion guardar_imagen_json: {e}", level="error")
            return None
        




