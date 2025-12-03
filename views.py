from flask import Blueprint, request, jsonify
from . import controller
from . import models
#API - DECLARACION ENDPOINTS

bp = Blueprint('images', __name__, url_prefix='/')

@bp.route("/upload_image", methods=["POST"])
def upload_image():
    try:
        write_log(f"Peticion POST /upload_image ", level="debug")
        data = request.get_json()
        file_json = data.get('file_json')
        
        if not file_json:
            return jsonify({"error": "JSON no proporcionado"}), 400

        min_confidence = request.args.get("min_confidence", default=80, type=int)
        
        write_log(f"Peticion POST -> leyendo json recibido ", level="debug")
        datos = controller.leer_json(file_json)
        
        image_uuid = datos['uuid']
        image_b64str = datos["data"]
        image_extension = datos["extension"]
        
        write_log(f"Peticion POST -> guardando imagen ", level="debug")
        path_image = controller.guardar_imagen_json(file_json)
        
        write_log(f"Peticion POST -> obteniendo url imagen ", level="debug")
        url_image = controller.image_url(image_uuid, image_extension, image_b64str)
        
        write_log(f"Peticion POST -> obteniendo tags imagen ", level="debug")
        tags = controller.image_tags(url_image, min_confidence )
        
        write_log(f"Peticion POST -> escribiendo datos picture en BBDD ", level="debug")
        models.registro_BBDD(image_uuid, path_image, tags)

        #NOTA MIRAR TAGS
        write_log(f"Peticion POST -> retornando resultado ", level="debug")
        return jsonify({
            "id": image_uuid,
            "size": controller.image_size(path_image),
            "Date Registration": models.query_fecha_registro(image_uuid),
            "tags": models.query_picture_tags(image_uuid),
            "data":image_b64str
        }), 201

    except Exception as e:
        write_log(f"error": str(e)}", level="error")
        return jsonify({"error": str(e)}), 500
        
        
@bp.route("/status", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "Servidor funcionando correctamente"}), 200

@bp.route("/images", methods=["GET"])
def get_images():
    min_date = request.args.get("min_date")
    max_date = request.args.get("max_date")
    write_log(f"Peticion GET -> /images iniciando peticiones de imagenes ", level="debug")
    
    if not min_date and max_date:
        return jsonify({"error": "Imagen no encontrada"}), 404
    try:
        respuesta=[]
        write_log(f"Peticion GET -> /images  buscando las imagenes con los filtros ", level="debug")
        imgs = models.query_filtros(min_date, max_date)
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
        write_log(f"Peticion GET -> /images  retornando la respuesta ", level="debug")
        return jsonify(respuesta),201
    except Exception as e:
        write_log(f"error": str(e)}", level="error")
        return jsonify({"error": str(e)}), 500



@bp.route("/images/<image_id>", methods=["GET"])
def get_image(image_id):
    #image_uuid = request.get(image_id)
    write_log(f"Peticion GET -> /images/id  iniciando peticion  ", level="debug")
    if not image_id:
        return jsonify({"error": "Imagen no encontrada"}), 404
    try:
        info = models.query_info_picture(image_id)
        write_log(f"Peticion GET -> /images/id  retornnando la consulta de un picture ", level="debug")
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
        return jsonify({"error": str(e)}), 500

#MODO DEBUGGER
@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open('app.log', 'r') as f:
            content = f.readlines()
        return jsonify({"logs": content})
    except Exception as e:
        write_log(f"error": str(e)}", level="error")
        return jsonify({"error": str(e)}), 500
            

