#!/bin/bash
#Script para crear repositorios accesibles de forma remota, mediante el usuario git
directorio=/git #Directorio donde se encuentran los repositorios 

function ayuda(){ #En caso de error, o que se introduzca un parametro mal, mostrara el mensaje de ayuda
	echo "Script para la creación y borrado de repositorios git:
	-n Nombre, crea un repositorio, en caso existir en el repositorio muestra un mensaje de error
	-b Nombre, borra un repositorio, caso de no existir muestra un mensaje de erro
	-h, muestra la ayuda
	-v, muestra la version
	";
}

function crear(){ #Se encarga de crear el repositorio
	ruta=${directorio}/${1}.git #Crea la variable ruta, que es la ruta absoluta al directorio
	if [[ ! -d "$ruta" ]]; then #Comprueba que la ruta no exista en caso de existir lo muestra por pantalla
		mkdir $ruta #Crea el directorio
		git init --bare $ruta > /dev/null 2>&1 #Inicia el repositorio, vacio, en la ruta expecificada, redirigelos stderr y stdout a /dev/null

		[[ $? -eq 0 ]] && echo "Repositorio creado" || echo "Error, algo ha fallado al crear el repositorio. Codigo de error: $?" #En funcion del resultado del ultimo comando $? muestra el mensaje de error o no

	else
		echo "El repositorio $1 ya existe"
	fi
	unset ruta #Elimina la variable ruta 
}

function borrar(){ #Se encarga de borra el repositorio
	ruta=${directorio}/${1}.git #Crea la variable ruta, para almacenar al ruta absoluta
	if [[ -d "$ruta" ]]; then #Comprueba que exista el repositorio 
		read -p "Quieres borrar el repositorio ( s | S ): " borra #Pregunta a el usuario si quiere borra el repositorio, almacena la respuesta en borra
		borra=$(tr '[:upper:]' '[:lower:]' <<< $borra); #Pasa las mayusculas a minusculas con el comando tr
		if [[ $borra == "s" ]]; then #Comprueba que la variable borra sea igual a s
			rm -r $ruta > /dev/null 2>&1 #Borra el repositorio y su contendio con redirecinamiento de la salida a /dev/null

			[[ $? -eq 0 ]] && echo "Repositorio borrado" || echo "Error, algo ha fallado al borrar el repositorio. Codigo de error: $?" #En función del estado del ultimo comando muestra un mensaje
			
		else
			echo "No se ha borrado el repositorio"
		fi
	else
		echo "No existe el repositorio especificado"	
	fi

}

while getopts ':n:b: hv' flag; do #Con getops se capturan las "flags para llamar a las respectivas funciones
	case $flag in
		n) crear $OPTARG;; 
		b) borrar $OPTARG;;
		v) echo "versión 0.5";;
		\? | \: | h) ayuda;; 

	esac

done
