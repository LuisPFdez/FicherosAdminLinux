#!/bin/bash
if [[ $# -ge 1 && $(id -u) -eq 0 ]]; then
	[[ -n $2 && $2 -lt 1024 ]] && echo "Introduce un valor superior a 1024 para el numero de bits" && exit 1
       	[[ -n $3 && ! $3 =~ ^[0-9]+ ]]	&& echo "Introduce un numero entero para los dias" && exit 1

	nombre=$1
	bits=$([[ -n $2 ]] && echo $2 || echo 2048)
	dias=$([[ -n $3 ]] && echo $3 || echo 365)
	
	echo "Generando clave privada"
#	openssl genpkey -algorithm rsa -pkeyopt rsa_keygen_bits:${bits} > ${nombre}.key 2> /dev/null 
	echo "Generando csr"
#	openssl req -new -key ${nombre}.key > ${nombre}.csr
	echo "Generando crt"
#	openssl x509 -req -days $dias -in ${nombre}.csr -signkey ${nombre}.key > ${nombre}.crt 2> /dev/null
	if [[ $(apache2ctl -M 2> /dev/null | grep "ssl_module" | wc -l) -ne 1 ]]; then
		echo "Activando modulo ssl"
		a2enmod ssl > /dev/null 2&>1
		echo "Reiniciando apache"
		/etc/init.d/apache2 restart > /dev/null 2&>1
	fi	
else
	echo -e "Script para crear y firmar certificados mediante ssl.
	El script inicia el modulo ssl de apache en caso de no estar activado por lo que es necesario que se ejecute como superusuario
	Son necesarios X paramentros:
	1-> Nombre de los archivos donde se guardaran las claves
       	2-> Numeros de bits para la clave privada.
	3-> Dias de valided de la firma"
fi
