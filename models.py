from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from . import controller
#CONSULTAS DE BASE DE DATOS
engine = create_engine("mysql+pymysql://mbit:mbit@localhost/Pictures")

def registro_BBDD(uuid,path_image,image_tags):
    #engine = create_engine("mysql+pymysql://mbit:mbit@localhost/Pictures")
    #Tabla que contendrá una fila por cada imagen almacenada en el sistema.
    BBDD_pictures_id=uuid
    BBDD_pictures_path=path_image
    BBDD_pictures_date=controller.obten_fecha_actual()

    try:
         
        with engine.connect() as conn:

            #tabla pictures
            query = text(f"INSERT INTO pictures VALUES ('{BBDD_pictures_id}','{BBDD_pictures_path}','{BBDD_pictures_date}')")
            controller.write_log(f"uso de la funcion registro_BBDD tabla pictures {query}", level="debug")
            conn.execute(query)
            conn.commit()

            #Tabla que contendrá las tags asociadas a cada imagen. 
            for x in image_tags:
                BBDD_tags_tag=x['tag']
                BBDD_tags_picture_id=BBDD_pictures_id
                BBDD_tags_confidence=x['confidence']
                BBDD_tags_date=controller.obten_fecha_actual()

                query = text(f"INSERT INTO tags VALUES ('{BBDD_tags_tag}','{BBDD_tags_picture_id}','{BBDD_tags_confidence}','{BBDD_tags_date}')")
                conn.execute(query)
                conn.commit()
            controller.write_log(f"uso de la funcion registro_BBDD tabla tag {query}", level="debug")
                
    except Exception as e:
            print(f"Ocurrió un error: {e}")
            controller.write_log(f"Ocurrió un error: {e}", level="error")

def query_fecha_registro(id_image):
    with engine.connect() as conn:
        query = text("SELECT date FROM pictures WHERE id = :id")
        result = conn.execute(query, {"id": id_image})
        date = result.scalar_one_or_none()
    return date

def query_picture_tags(id_image):
    with engine.connect() as conn:
            query = text("SELECT tag, confidence FROM tags WHERE picture_id = :id")
            result = conn.execute(query, {"id": id_image})
            columns = result.keys()
            tags_confidence = [
            dict(zip(columns, row))
            for row in result
                ]
    return tags_confidence

def query_info_picture(id_image):
    with engine.connect() as conn:
            query = text("""
                SELECT 
                    pc.id,
                    pc.path,
                    pc.date,
                    tgs.tag,
                    tgs.confidence,
                    tgs.date
                FROM pictures pc
                JOIN tags tgs ON tgs.picture_id =  pc.id
                WHERE pc.id = :id
                         """)
            result = conn.execute(query, {"id": id_image})
            columns = result.keys()
            tags_confidence = [
            dict(zip(columns, row))
            for row in result
                ]
    grouped = {}
    combined=[]
    for x in tags_confidence:
        if x["id"] not in grouped:
            grouped[x["id"]] = {
                "id": x["id"],
                "path": x["path"],
                "date": x["date"],
                "tags": []
            }
        grouped[x["id"]]["tags"].append({
            "tag": x["tag"],
            "confidence": x["confidence"]
        })
    combined = [
    {
        "id": img_id,
        "path": data["path"],
        "date": data["date"],
        "tags": data["tags"]
    }
    for img_id, data in grouped.items()
    ]
    return combined

def query_filtros(min_date, max_date):
    
    query = text("""
        SELECT p.id,
               p.path,
               DATE_FORMAT(p.date, '%Y-%m-%d %H:%i:%s') AS fecha,
               GROUP_CONCAT(t.tag, ', ') AS tags,
               AVG(t.confidence) AS confidence
        FROM pictures p
        LEFT JOIN tags t ON p.id = t.picture_id
        WHERE p.date BETWEEN :fecha_min AND :fecha_max
        GROUP BY p.id, p.date
        ORDER BY p.date
    """)

    with Session(engine) as session:
        results = session.execute(query, {"fecha_min": min_date, "fecha_max": max_date})
        return [
            {
                "id": r.id,
                "path":r.path,
                "fecha": r.fecha,
                "tags": r.tags,
                "confidence": 1.0  # valor fijo o calculado
            }
            for r in results
        ]

    return results


