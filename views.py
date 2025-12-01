from flask import Blueprint, request, jsonify
from . import controller
from . import models
#API - DECLARACION ENDPOINTS

bp = Blueprint('images', __name__, url_prefix='/')

@bp.route("/upload_image", methods=["POST"])
def upload_image():
    try:
        
        data = request.get_json()
        #MIRAR DOCKER CP Y EL SECRET MANAGER
        file_json = data.get('file_json')
        credentials = data.get('credentials')

        if not file_json:
            return jsonify({"error": "JSON no proporcionado"}), 400

        if not credentials:
            return jsonify({"error": "ficheros de Credenciales no proporcionadas"}), 401
        
       
        min_confidence = request.args.get("min_confidence", default=80, type=int)

        datos = controller.leer_json(file_json)
        image_uuid = datos['uuid']
        image_b64str = datos["data"]
        image_extension = datos["extension"]

        path_image = controller.guardar_imagen_json(file_json)
        url_image = controller.image_url(image_uuid, image_extension, image_b64str, credentials)
        tags = controller.image_tags(url_image, min_confidence, credentials)
        controller.registro_BBDD(image_uuid, path_image, tags)
        #controller.delete_image_url(url_image,credentials)
        #NOTA MIRAR TAGS 
        return jsonify({
            "id": image_uuid,
            "size": controller.image_size(path_image),
            "Date Registration": models.query_fecha_registro(image_uuid),
            "tags": models.query_picture_tags(image_uuid),
            "data":image_b64str
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/status", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "Servidor funcionando correctamente"}), 200

@bp.route("/images", methods=["GET"])
def get_images():
    #tags = request.args.get("tags")
    #if not min_date and max_date:
    #return jsonify({"error": "Imagen no encontrada"}), 404
    try:
        imgs = models.query_filtros(request.args.get("min_date"), request.args.get("max_date"))
        print(imgs)
        return jsonify(imgs)
    
    except Exception as e:
        # en producción usa un logger en vez de print
        return jsonify({"error": str(e)}), 500



@bp.route("/images/<image_id>", methods=["GET"])
def get_image(image_id):
    #image_uuid = request.get(image_id)

    if not image_id:
        return jsonify({"error": "Imagen no encontrada"}), 404

    info = models.query_info_picture(image_id)

    for cc in info:
        return jsonify({
            'id': cc['id'],
            "size": f"{controller.image_size(cc['path'])} KB",
            "path":cc['path'],
            "Date Registration": cc['date'],
            "tags": cc['tags'],
            "data":f"{controller.imagen_base64(cc['path'])}"
        }), 201
    
  
            

