from sqlalchemy import create_engine, text
#CONSULTAS DE BASE DE DATOS
engine = create_engine("mysql+pymysql://mbit:mbit@localhost/Pictures")


def query_fecha_registro(id_image):
    with engine.connect() as conn:
        query = text("SELECT date FROM pictures WHERE id = :id")
        result = conn.execute(query, {"id": id_image})
        date = result.scalar_one_or_none()
    return date

def query_picture_tags(id_image):
    with engine.connect() as conn:
            query = text("SELECT tag, confidence FROM tags WHERE pictures_id = :id")
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
                JOIN tags tgs ON tgs.pictures_id =  pc.id
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