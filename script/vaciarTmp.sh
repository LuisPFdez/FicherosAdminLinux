#!/bin/bash
#Directorio que tiene que buscar
directorio=tmp
#Funcion encargada de buscar la carpeta que se le pase por parametro
function buscarCarpeta(){
	if [[ -d $1 ]]; then #Comprueba que el directorio exista
		rutas=$(find $1 -name $directorio) #Busca todas las carpetas dentro del directorio
		echo $rutas #Devuelve las rutas obtenidas
	fi
}

for i in $@; do #Recorre todos los directorios que se le pasan por parametro
	rutas=$(buscarCarpeta $i) #LLama a la funcion buscarCarpeta y almacena el resultado en rutas
	for ruta in $rutas; do #Si buscarCarpeta devuelve algo recorrera lo que ha retornado 
		rm -r $ruta/* 2>/dev/null 1&>2 #Vacia la ruta, en caso de estar vacio muestra un error por lo que lo redirige a dev/null
	done	

done
exit 0 #Cierra el programa con un exit 0 (todo ejecutado de forma correcta)
