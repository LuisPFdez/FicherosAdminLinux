#!/bin/bash
rojo="\e[31m"
nor="\e[0m"
temporal="/tmp/datosCHROOT.txt"

trap borrado INT

function borrado (){
  echo "Saliendo"
  if [[ -f $temporal ]]; then
    rm $temporal
  fi
  exit 0
}

function ayuda (){
  echo -e "\tEste script permite la creacion de una jaula o entorno de forma automatica.
  \tEl script necesita de al menos dos parametros para funcionar, donde el primero ha de ser siempre un directorio y los siguientes los ejecutables.
  \tEl directorio sera el lugar donde se creara la jaula y ha de estar vacia
  \tSi el directorio no existe se creará uno nuevo, si existe usará el directorio proporcionado.
  \t${rojo}¡Si el directorio no esta vacio saldra del script con un error!${nor}
  \tPara cada ejecutable copiara el mismo ejecutable y las dependencias, la estructura de estas ejecutables será copiada también
  \tAntes de crear la estructura y copiarlo guarda en un fichero temporal las rutas a todos los ejecutables
  "
}

function dependencias (){
  localizacion=$(which $1);
  if [[ $? -eq 0 ]]; then
    echo $localizacion >> $temporal

  $( ldd $localizacion | awk '{

    	if( NF > 2 ){
    		printf "%s\n", $3
    	} else if (  NF=2 && $1 ~ /^\/+/ ){
    		printf "%s\n", $1
    	}

	}' >> $temporal)
  else
    echo "El programa $1 no existe"
  fi
}

function comprobarDirectorio (){
  if [[ -d $directorio ]]; then
    [[ $(ls -A $directorio) ]] && echo -e "El directorio no esta vacio" && exit 1
  elif [[ ! -z $directorio ]]; then
    mkdir $directorio > /dev/null
  else
    echo "El nombre del directorio esta vacio"
    exit 1
  fi
}


function main (){
  if [[ $# -ge 2 ]]; then
  	directorio=$1
    comprobarDirectorio
    shift

    if [[ ! -f $temporal ]]; then
      touch $temporal
    else
      echo /dev/null >| $temporal
    fi

    for args in $@ ; do
      echo $args
  	  dependencias $args
    done
    cd $directorio
    pwd
    cat $temporal | awk -F "/" 'BEGIN { OFS = "/"; ORS = "\n" }{NF--}1' | sed "s/^\///" | xargs -n1 mkdir -p
    cat $temporal | sed "s/^\///" | xargs -n1 -I ruta cp /ruta ruta
    borrado
  else
      ayuda
  fi
}
main $@
