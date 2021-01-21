#!/bin/bash
#Script para crear y auto firmar claves ssl
#Colores para los mensajes
verde="\e[32m"
rojo="\e[31m"
azul="\e[34m"
fin="\e[0m"
#Comprueba que el numero de argumentos sea mayor a uno y el id de usuario igual a 0 (root), sino muestra la ayuda
if [[ $# -ge 1 && $(id -u) -eq 0 ]]; then
	#Comprueba que en caso de introducir un segundo argumento sea mayor a 1024, si no muestra un mensaje y sale con el codigo 1
	[[ -n $2 && $2 -lt 1024 ]] && echo -e "${rojo}Introduce un valor superior a 1024 para el numero de bits${fin}" && exit 1 
	#Comprueba que si el tercer argumento se ha introducido sea un numero, si no muestra un mensaje y sale con el codigo 1
       	[[ -n $3 && ! $3 =~ ^[0-9]+ ]]	&& echo -e "${rojo}Introduce un numero entero para los dias${fin}" && exit 1

	nombre=$1 #Nombre almacenará el valor del primer argumento
	bits=$([[ -n $2 ]] && echo $2 || echo 2048) #bits por defecto, si no se ha introducido un segundo argumento será igual a 2048
	dias=$([[ -n $3 ]] && echo $3 || echo 365) #dias por defecto, en caso de no haber introducido un 3 argumento, será igual a 365
	
	echo "Generando clave privada"
	openssl genpkey -algorithm rsa -pkeyopt rsa_keygen_bits:${bits} > ${nombre}.key 2> /dev/null #Genera la clave privada
	echo "Generando csr"
	openssl req -new -key ${nombre}.key > ${nombre}.csr 
	echo "Generando crt"
	openssl x509 -req -days $dias -in ${nombre}.csr -signkey ${nombre}.key > ${nombre}.crt 2> /dev/null
	if [[ -f /etc/ssl/private/${nombre}.key ]]; then
		cp ${nombre}.key /etc/ssl/private/${nombre}.key
		chown root:ssl-cert /etc/ssl/private/${nombre}.key
		chmod 640 /etc/ssl/private/${nombre}.key
	fi
	if [[ -f /etc/ssl/certs/${nombre}.crt ]]; then
		cp ${nombre}.crt /etc/ssl/certs/${nombre}.crt 
		chown root:root /etc/ssl/certs/${nombre}.crt
	fi
	if [[ $(apache2ctl -M 2> /dev/null | grep "ssl_module" | wc -l) -ne 1 ]]; then
		echo "Activando modulo ssl"
		a2enmod ssl > /dev/null 2&>1
		echo "Reiniciando apache"
		/etc/init.d/apache2 restart > /dev/null 2&>1
	fi	
else
	echo -e "Script para crear y firmar certificados mediante ssl
El script inicia el modulo ssl de apache en caso de no estar activado por lo que es necesario que se ejecute como ${azul}superusuario${fin}
Son necesarios X paramentros:
${verde}1${fin}-> Nombre de los archivos donde se guardaran las claves
${verde}2${fin}-> Numeros de bits para la clave privada.
${verde}3${fin}-> Dias de valided de la firma"
fi
