# Ficheros de administración para Linux
Conjunto de script, servicios y ficheros de configuración para linux

## Servicios
* vaciadoTmp -> Servicio que tiene asignado un timer, se encarga unicamente de llamar a un script para vaciar los ficheros de las carpetas tmp del servidor
* vaciadoTmp **(timer)** -> Se ejecuta el servicio cada hora
## Scripts
* IP -> Obtiene la dirección ip (4 o 6), y en caso de no estar conectado devuelve un símbolo
* gitAdmin -> Permite la administración de un servidor de repositorios
* phpDocInstalador -> Permite la instalacián rapida de phpDocumentor
* ssl -> Permite crea y autofirmar certificados con openssl
* vaciadoTmp -> Busca todas las carpetas tmp y borra su contenido
* preparadoChroot -> Permite la creación rápida de una jaula 
## Instalador
**Permite creación y configuración rápida de un servidor** \
Crea el usuario **operadorweb**, sino esta creado, e instala: 
* Apache2 
* php7.4
* xdebug
* mysql
* phpmyadmin 
* bind9 

En **mysql**, crea un usuario con todos los privilegios sobre todas las bases de datos y con la opcion de grant.
Para **xdebug**, copia un archivo con la configuracion en la carpeta */etc/php/7.4/mods-available*

## InstaladorPython 
**Permite crear una plantilla, json, para configurar un servidor basado en Debian**
