#!/bin/bash

#Script para obtener la ip
#Este script esta hecho para mostrar la ip en el prompt de linux
#Imprime un símbolo, un cero en este caso, en caso de estarlo por defecto imprime la Ipv4, si el primer parametro es -6 imprimirá la ipv6
#Ejemplo de uso en el prompt PS1="\e[32m\$(date +"%H") \e[35m\h \n\e[36m\$(~/IP.sh) \e[34m->\e[0m "

interfaz=$(/usr/bin/ip route | head -n 1 | awk '{print $5}') #Obtiene el nombre de la interfaz por la cual se esta conectado la máquina a internet, en caso de no estar conectado será null
# Nombre de las interfaces
ethernet="enp0s3"
wifi=""
if [[ -n $interfaz ]]; then #Comprueba que este conectado
	if [[ $1 -eq "-6" ]]; then #Si el primer parametro es igual a -6 establecera la variable red para que escoga la ipv6
		red=inet6
	else
		red=inet #Por defecto se establecerá para que se escoga la ipv4
	fi
	if [[ $interfaz == $ethernet ]]; then #Comprueba que el nombre de la interfaz por la que se conecta es igual a la de la interfaz de ethernet
		ip a show $ethernet | grep -w $red | awk '{ printf $2}' | cut -d "/" -f 1
	elif [[ $interfaz == $wifi  ]]; then
		ip a show $wifi | grep -w $red | awk '{ printf $2}' | cut -d "/" -f 1
	fi
else
	echo O #En caso de no estar conectado imprime un valor 
fi
