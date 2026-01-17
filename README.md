# Microservicios
En este proyecto vamos a crear una aplicación basada en microservicios, utilizando la tecnología Docker para ejecutar cada microservicio en un entorno reproducible.

La aplicación permitirá subir fotos, las cuales etiquetará automáticamente, y las almacenará en una carpeta además de crear una base de datos donde existirá toda esta información (paths a imágenes y etiquetas  asignadas). Esta información será utilizada para permitir también buscar imágenes por una etiqueta concreta.

Existirán los siguientes microservicios:

- API: implementada en Flask y servida mediante waitress.
- Base de datos: utilizaremos una base de datos MySQL 8.0.


<img width="793" height="407" alt="image" src="https://github.com/user-attachments/assets/56b20b17-8b40-4c50-a22a-7588288ab579" />
