# Autor: Victor Fuentes Toledo
# Fecha: 2025-12-09
# Descripción: PC3

from flask import Blueprint, request, jsonify
from . import controller
from . import models
#API - DECLARACION ENDPOINTS

bp = Blueprint('images', __name__, url_prefix='/')

@bp.route("/upload_image", methods=["POST"])
def upload_image():
    try:
        controller.write_log(f"Peticion POST /upload_image ", level="debug")
        
        data = request.get_json()
        controller.write_log(f"Peticion POST -> Fichero JSON recibidos{data} ", level="debug")
        
        if not data:
            return jsonify({"error": "JSON no proporcionado"}), 400

        min_confidence = request.args.get("min_confidence", default=80, type=int)
        
        controller.write_log(f"Peticion POST -> leyendo contenido ", level="debug")
        controller.write_log(f"Peticion POST -> leyendo uuid: {data.get('uuid')} ", level="debug")
        controller.write_log(f"Peticion POST -> leyendo imagen en base64: {data.get('data')} ", level="debug")
        controller.write_log(f"Peticion POST -> leyendo imagen en Extension: {data.get('extension')} ", level="debug")

        image_uuid = data.get('uuid')
        image_b64str = data.get("data")
        image_extension = data.get("extension")
        
        controller.write_log(f"Peticion POST -> guardando imagen ", level="debug")
        path_image = controller.guardar_imagen_json(image_uuid,image_b64str,image_extension)
        
        controller.write_log(f"Peticion POST -> obteniendo url imagen ", level="debug")
        url_image = controller.image_url(image_uuid, image_extension, image_b64str)
        
        controller.write_log(f"Peticion POST -> obteniendo tags imagen ", level="debug")
        tags = controller.image_tags(url_image['url'],url_image['file_id'], min_confidence )
        
        controller.write_log(f"Peticion POST -> escribiendo datos picture en BBDD ", level="debug")
        models.registro_BBDD(image_uuid, path_image, tags)

        #NOTA MIRAR TAGS
        controller.write_log(f"Peticion POST -> retornando resultado ", level="debug")
        return jsonify({
            "id": image_uuid,
            "size": controller.image_size(path_image),
            "Date Registration": controller.obten_fecha_actual(),
            "tags": models.query_picture_tags(image_uuid),
            "data":image_b64str
        }), 201

    except Exception as e:
        controller.write_log(f"error: {str(e)}", level="error")
        return jsonify({"error": str(e)}), 500
        
        
@bp.route("/status", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "Servidor funcionando correctamente"}), 200

@bp.route("/images", methods=["GET"])
def get_images():
    min_date = request.args.get("min_date")
    max_date = request.args.get("max_date")
    controller.write_log(f"Peticion GET -> /images iniciando peticiones de imagenes ", level="debug")
    
    if not min_date and max_date:
        return jsonify({"error": "Imagen no encontrada"}), 404
    try:
        respuesta=[]
        controller.write_log(f"Peticion GET -> /images  buscando las imagenes con los filtros {min_date,max_date}", level="debug")
        imgs = models.query_filtros(min_date, max_date)
        controller.write_log(f"Peticion GET -> /images  resultado busqueda  {imgs}", level="debug")
        #print(imgs)
        for cc in imgs:
            print(cc)
            respuesta.append({
                'id': cc['id'],
                "size": f"{controller.image_size(cc['path'])} KB",
                "Date Registration": cc['fecha'],
                "tags": cc['tags'],
                "data":f"{controller.imagen_base64(cc['path'])}"
            })
        controller.write_log(f"Peticion GET -> /images  retornando la respuesta  {respuesta}", level="debug")
        return jsonify(respuesta),201
    except Exception as e:
        controller.write_log(f"error peticion images: {str(e)}", level="error")
        return jsonify({"error": str(e)}), 500



@bp.route("/images/<image_id>", methods=["GET"])
def get_image(image_id):
    #image_uuid = request.get(image_id)
    controller.write_log(f"Peticion GET -> /images/id  iniciando peticion  ", level="debug")
    if not image_id:
        return jsonify({"error": "Imagen no encontrada"}), 404
    try:
        info = models.query_info_picture(image_id)
        controller.write_log(f"Peticion GET -> /images/id  retornnando la consulta de un picture ", level="debug")
        for cc in info:
            return jsonify({
                'id': cc['id'],
                "size": f"{controller.image_size(cc['path'])} KB",
                "path":cc['path'],
                "Date Registration": cc['date'],
                "tags": cc['tags'],
                "data":f"{controller.imagen_base64(cc['path'])}"
            }), 201
        
    except Exception as e:
        controller.write_log(f"error: {str(e)}", level="error")
        return jsonify({"error": str(e)}), 500

#MODO DEBUGGER
@bp.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open('app.log', 'r') as f:
            content = f.readlines()
        return jsonify({"logs": content})
    except Exception as e:
        controller.write_log(f"error: {str(e)}", level="error")
        return jsonify({"error": str(e)}), 500
            

