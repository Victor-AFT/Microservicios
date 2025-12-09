# Autor: Victor Fuentes Toledo
# Fecha: 2025-12-09
# Descripción: PC3

from flask import Flask
import logging

def create_app():
    app = Flask(__name__)
    #Configuración de logging
    

    
    # existing code omitted
    from . import views
    app.register_blueprint(views.bp)

    return app
