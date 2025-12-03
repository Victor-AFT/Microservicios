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
    try:
        with open(fichero, 'r', encoding='utf-8') as archivo_json:
            data = json.load(archivo_json)
        return data

    except Exception as e:
        write_log(f"Ocurrió un error: {e}", level="error")
        #print(f"Ocurrió un error: {e}")
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
        
        return upload_info.url
    
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return None
    
def delete_image_url(image_url):
    
    credentials = leer_json(file_json_pss)

    imagekit = ImageKit(
    public_key=credentials["imagekit"]["public_key"],
    private_key=credentials["imagekit"]["private_key"],
    url_endpoint = credentials["imagekit"]["url_endpoint"]
    )

    return imagekit.delete_file(file_id=image_url.file_id)


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
            
            delete_image_url(image_url,credentials)
            return tags
            #delete_image_url(image_url,credentials)
        except Exception as e:
            print(f"Ocurrió un error: {e}")
            return None
#FALTA LA FUNCION PARA ELIMINAR EL RASTRO DE LA WEB

# DEVUELVE EL TAMAÑO DE LA IMAGEN
def image_size(ruta_imagen):
    try:
        size_bytes=os.path.getsize(ruta_imagen)
        size_kb=size_bytes/1024
        return size_kb
    
    except Exception as e:
            print(f"Ocurrió un error: {e}")
            return None

#REGISTRA LOS DATOS DE LA IMAGEN Y SUS TAGS EN LA BASE DE DATOS
def registro_BBDD(uuid,path_image,image_tags):

    engine = create_engine("mysql+pymysql://mbit:mbit@localhost/Pictures")

    #Tabla que contendrá una fila por cada imagen almacenada en el sistema.
    BBDD_pictures_id=uuid
    BBDD_pictures_path=path_image
    BBDD_pictures_date=obten_fecha_actual()

    try:
         
        with engine.connect() as conn:

            #tabla pictures
            query = text(f"INSERT INTO pictures VALUES ('{BBDD_pictures_id}','{BBDD_pictures_path}','{BBDD_pictures_date}')")
            conn.execute(query)
            conn.commit()

            #Tabla que contendrá las tags asociadas a cada imagen. 
            for x in image_tags:
                BBDD_tags_tag=x['tag']
                BBDD_tags_picture_id=BBDD_pictures_id
                BBDD_tags_confidence=x['confidence']
                BBDD_tags_date=obten_fecha_actual()

                query = text(f"INSERT INTO tags VALUES ('{BBDD_tags_tag}','{BBDD_tags_picture_id}','{BBDD_tags_confidence}','{BBDD_tags_date}')")
                conn.execute(query)
                conn.commit()
                
    except Exception as e:
            print(f"Ocurrió un error: {e}")

#DEVUEVE LA IMAGEN COMO STRING EN BASE64
def imagen_base64(ruta_imagen):
    try:
        with open(ruta_imagen, mode="rb") as img:
                imgstr = base64.b64encode(img.read())
        return imgstr
    except Exception as e:
            print(f"Ocurrió un error: {e}")
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

        with open(ruta_imagen,"wb") as imagen_file:
             imagen_file.write(imagen_bytes)
        
        return ruta_imagen     

    except Exception as e:
            print(f"Error al guardar la imagen: {e}")

            return None
        

