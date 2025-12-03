from flask import Flask
import logging

def create_app():
    app = Flask(__name__)
    #Configuración de logging
    logging.basicConfig(
        filename='/app/app.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # existing code omitted
    from . import views
    app.register_blueprint(views.bp)

    return app
