# openhabWeb
Servidor Web para *openHAB*

Desarrollo propio empleando Python, Flask y JS para crear un frontal adaptado a mis necesidades
que accede a los datos de un servidor openHAB doméstico.

El sistema está siempre en desarrollo.

El código está preparado para funcionar con **python3**

**Información adicional**

* /bbdd	Contiene los scripts python y crontab para hacer copias de seguridad de la base de datos
	Y consolidar en tablas horarias y diarias la información de los sensores

* /templates	Directorio con los templates **jinja**

* /static		Todo el contenido estático del servidor web

**Otros enlaces**

Dispone de la URL http://server/health para comprobar si los datos están actualizados en la base de datos.
