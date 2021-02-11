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
### Permite creación y configuración rápida de un servidor
Crea el usuario **operadorweb** e instala: 
* Apache2 
* php7.4
* xdebug
* mysql
* phpmyadmin
* bind9
**Para mysql un usuario con todos los permisos y opción de grant**
