#!/bin/bash
directorio=/git

function ayuda(){
	echo "Script para la creación y borrado de repositorios git:
	-n Nombre, crea un repositorio, en caso existir en el repositorio muestra un mensaje de error
	-b Nombre, borra un repositorio, caso de no existir muestra un mensaje de error
	-h Muestra la ayuda
	-v Muestra la version
	";
}

function crear(){
	ruta=${directorio}/${1}.git
	if [[ ! -d "$ruta" ]]; then
		mkdir $ruta
		git init --bare $ruta > /dev/null 2>&1

		[[ $? -eq 0 ]] && echo "Repositorio creado" || echo "Error, algo ha fallado al crear el repositorio. Codigo de error: $?"

	else
		echo "El repositorio $1 ya existe"
	fi
	unset ruta
}

function borrar(){
	ruta=${directorio}/${1}.git
	if [[ -d "$ruta" ]]; then
		echo -n "Quieres borrar el repositorio ( s | S ): " 
		read borra
		borra=$(tr '[:upper:]' '[:lower:]' <<< $borra);
		if [[ $borra == "s" ]]; then
			rm -r $ruta > /dev/null 2>&1 

			[[ $? -eq 0 ]] && echo "Repositorio borrado" || echo "Error, algo ha fallado al borrar el repositorio. Codigo de error: $?"
			
		else
			echo "No se ha borrado el repositorio"
		fi
	else
		echo "No existe el repositorio especificado"	
	fi

}
if [[ $1 -eq "--version" ]]; then
while getopts ':n:b: hv' flag; do
	case $flag in
		n) crear $OPTARG;;
		b) borrar $OPTARG;;
		v) echo "versión 0.5";;
		\? | \: | h) ayuda;;

	esac

done
