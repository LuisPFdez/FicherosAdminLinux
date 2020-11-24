#!/bin/bash

trap borrado exit

function borrado() {
  if [[ -f /tmp/datosCHROOT.txt ]]; then
    rm /tmp/datosCHROOT.txt
  fi
  exit 0
}

function ayuda() {
  echo -e "\tEste script permite la creacion de una jaula o entorno de forma automatica.
  \tEl script necesita de al menos dos parametros para funcionar, donde el primero ha de ser siempre un directorio y los siguientes los ejecutables.
  \tSi el directorio no existe se creará uno nuevo, si existe usará el directorio proporcionado.
  \t\e[31m¡Si el directorio no esta vacio saldra del script con un error!\e[0m
  \tPara cada ejecutable copiara el mismo ejecutable y las dependencias, la estructura de estas ejecutables será copiada también
  \tAntes de crear la estructura y copiarlo guarda en un fichero temporal las rutas a todos los ejecutables
  "
}

function dependencias() {
  echo "ps"
}

function comprobarDirectorio() {
  local directorio= $1
  if [[ -d $directorio ]]; then
    [[ $(ls -A $directorio) ]] && echo "El directorio no esta vacio"; exit 1
  elif [[ ! -z $directorio ]]; then
    mkdir $directorio > /dev/null
  else
      echo "El nombre del directorio esta vacio"
      exit 1
  fi
}


function main() {
  directorio=$1
  comprobarDirectorio $directorio
  shift

  if [[ $# -ge 1 ]]; then
    for args in $@; do
      echo "hola"
    done
  else
    ayuda
  fi
}

main $@
