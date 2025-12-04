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
UPLOAD_FOLDER = "/app/data"

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
    write_log(f"uso de la funcion Leer_json {data}", level="debug")
    try:
        with open(fichero, 'r', encoding='utf-8') as archivo_json:
            data = json.load(archivo_json)
        return data
    except Exception as e:
        write_log(f"Ocurrió un error: {e}", level="error")
        print(f"Ocurrió un error: {e}")
        return None      
    
#DEVUELVE LA URL  DE LA IMAGEN
def image_url(uuid,extension,image_strbase64):
    
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
        return upload_info.url
    
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        write_log(f"Ocurrió un error: {e}", level="error")
        return None
    
def delete_image_url(image_url):
    
    credentials = leer_json(file_json_pss)

    imagekit = ImageKit(
    public_key=credentials["imagekit"]["public_key"],
    private_key=credentials["imagekit"]["private_key"],
    url_endpoint = credentials["imagekit"]["url_endpoint"]
    )
    try:
        imagekit.delete_file(file_id=image_url.file_id)
        write_log(f"uso de la funcion delete_image_url {upload_info.url}", level="debug")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        write_log(f"Ocurrió un error: {e}", level="error")
    return None


def image_tags(image_url,min_confidence):
        
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
            write_log(f"uso de la funcion image_tags {tags}", level="debug")
            delete_image_url(image_url,credentials)
            return tags
        except Exception as e:
            print(f"Ocurrió un error: {e}")
            write_log(f"Ocurrió un error: {e}", level="error")
            return None
#FALTA LA FUNCION PARA ELIMINAR EL RASTRO DE LA WEB

# DEVUELVE EL TAMAÑO DE LA IMAGEN
def image_size(ruta_imagen):
    try:
        size_bytes=os.path.getsize(ruta_imagen)
        size_kb=size_bytes/1024
        write_log(f"uso de la funcion image_size {size_kb}", level="debug")
        return size_kb
    
    except Exception as e:
            print(f"Ocurrió un error: {e}")
            write_log(f"Ocurrió un error: {e}", level="error")
            return None


#DEVUEVE LA IMAGEN COMO STRING EN BASE64
def imagen_base64(ruta_imagen):
    try:
        with open(ruta_imagen, mode="rb") as img:
                imgstr = base64.b64encode(img.read())
        write_log(f"uso de la funcion imagen_base64 ", level="debug")
        return imgstr
    except Exception as e:
            print(f"Ocurrió un error: {e}")
            write_log(f"Ocurrió un error: {e}", level="error")
            return None
    
#GUARDA LA IMAGEN DESDE EL JSON
def guardar_imagen_json(file_json):
    try:
        data=leer_json(file_json)
        nombre=data['uuid']
        extension=data['extension']
        strbase64=data['data']

        imagen_bytes=base64.b64decode(strbase64)
        
        os.makedirs(UPLOAD_FOLDER,exist_ok=True)
        ruta_imagen=os.path.join(UPLOAD_FOLDER,f"{nombre}{extension}")
        write_log(f"uso de la funcion guardar_imagen_json {ruta_imagen}", level="debug")
        
        with open(ruta_imagen,"wb") as imagen_file:
             imagen_file.write(imagen_bytes)
        
        return ruta_imagen     

    except Exception as e:
            print(f"Error al guardar la imagen: {e}")
            write_log(f"Ocurrió un error: {e}", level="error")
            return None
        




