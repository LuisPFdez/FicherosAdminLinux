#!/bin/bash
rojo="\e[31m"
nor="\e[0m" #Variable para eliminar 
temporal="/tmp/datosCHROOT.txt"

trap borrado INT #En caso de pulsar Control-C llama a la funcion borrado que eliminará el archivo temporal

function borrado (){ # Funcion encargada de borrar el archivo 
  if [[ -f $temporal ]]; then # Comprueba que exista el fichero temporal
    rm $temporal #Borra el fichero temporal
  fi
  exit 0 #Finaliza el programa sin codigo de error
}

function ayuda (){ #Funcion encargada de mostrar la ayuda
  echo -e "\tEste script permite la creacion de una jaula o entorno de forma automatica.
  \tEl script necesita de al menos dos parametros para funcionar, donde el primero ha de ser siempre un directorio y los siguientes los ejecutables.
  \tEl directorio sera el lugar donde se creara la jaula y ha de estar vacia
  \tSi el directorio no existe se creará uno nuevo, si existe usará el directorio proporcionado.
  \t${rojo}¡Si el directorio no esta vacio saldra del script con un error!${nor}
  \tPara cada ejecutable copiara el mismo ejecutable y las dependencias, la estructura de estas ejecutables será copiada también
  \tAntes de crear la estructura y copiarlo guarda en un fichero temporal las rutas a todos los ejecutables
  "
}

#Dependencias se encarga de escribir la ruta del ejecutable y sus dependencias en un archivo temporal
function dependencias (){ 
  localizacion=$(which $1); #Ejecuta un which del primer parametro, para conocer la ruta absoluta del ejecutable y almacena el resultado en localizacion
  #Si el ejecutable no existe which devuelve un mensaje de error. 
  if [[ $? -eq 0 ]]; then #En caso de que no devuelva un mensaje de error, empieza a escribir sobre el fichero temporal
    echo $localizacion >> $temporal #Almacena la ruta absoluta al ejecutable
#ldd mostrara las dependencias, awk se encargara de filtrar el resultado y añadirlo al fichero temporal
  $( ldd $localizacion | awk '{
	#Si el numero de campos de la linea es mayor a dos, imprimirá el tercer campo
    	if( NF > 2 ){
    		printf "%s\n", $3
	#En caso negativo, comprueba si el numero de campos es igual a dos y empieza por "/", en caso de coincidir muestra el campo 1
    	} else if (  NF=2 && $1 ~ /^\/+/ ){
    		printf "%s\n", $1
    	}

	}' >> $temporal)
  else #Si which devuelve un codigo de errro imprime un mensaje de error
    echo "${rojo}El programa $1 no existe${nor}"
  fi
}
#Funcion para comprobrar la existencia de un directorio o si esta vacio
function comprobarDirectorio (){ 
 #Si el directorio existe, comprobara que con ls -A que no tenga elementos. Sino mostrará un mensaje  de error y saldra del programa con el codigo 1
  if [[ -d $directorio ]]; then
    [[ $(ls -A $directorio) ]] && echo -e "${rojo}El directorio no esta vacio${nor}" && exit 1
  elif [[ ! -z $directorio ]]; then # En caso de que el directorio no exista pero la variable no este vacia, creara el directoro 
    mkdir $directorio > /dev/null 
  else
    echo "${rojo}El nombre del directorio esta vacio${nor}" #En caso de pasarle un nombre de directorio vacio mostrará un mensaje de eror
    exit 1 #Cierra el programa con el codigo de error 1
  fi
}


function main (){ #Funcion principal
  if [[ $# -ge 2 ]]; then #En caso de que el numero de argumentos sea mayor o igual a 2
	directorio=$1 #Asigna el primer argumento a directorio
    comprobarDirectorio #LLama a la funcion comprobar directorio
    shift #Elimina el primer argumeno

    if [[ ! -f $temporal ]]; then #Comprueba que el fichero temporal no este creado y lo crea
      touch $temporal
    else #En caso de estar creado lo vacia
      echo /dev/null >| $temporal
    fi

    for args in $@ ; do #Le pasa los argumentos restantes al for para recorrerlos. Cada argumento se guarda en args
  	dependencias $args #LLama a la funcion dependencias y le pasa args
    done
    cd $directorio #Se cambia al directorio
    #Lee el fichero temporal, con awk se elimina el ultimo parametro, sed eliminara la "/" inicial y xargs ejecutará el un parametro en funcion al stdout de los demas comandos. 
    #Awk establece como separador la "/".BEGIN establece la "/" como separador para que al mostrar la linea tambien se mueste y el final de line como un salto de linea con \n. NF-- eliminara el campo final de cada linea y 1 funciona a modo de true, que ejecutará el por defecto imprimir toda la linea
    #Xargs establece que al comando mkdir, -p permite pasarle una ruta y si algun directorio de la ruta no existe lo creara, el -n establece el numero de parametros pasados al comando
    cat $temporal | awk -F "/" 'BEGIN { OFS = "/"; ORS = "\n" }{NF--}1' | sed "s/^\///" | xargs -n1 mkdir -p
    #Xargs -I establecera donde se guardan los paramentros recibidos. Copia la ruta absoluta añadiendole "/" en la ruta relativa, esta dentro del directorio
    cat $temporal | sed "s/^\///" | xargs -I ruta cp /ruta ruta
    #Por ultimo llama a borrado para finalizar el programa y borrar el fichero temporal
    borrado
  else
      #En caso que los argumentos sean menores a 2 llama a la funcion ayuda
      ayuda
  fi
}
#LLamada a la funcion main, a la cual se le pasan todos los argumentos
main $@
