#!/bin/bash

function listado(){
  args=$( [[ -z $args ]] && echo $1 || echo $args);

  while read args; do 

    total=$(ls -A $1 | wc -l );
    if [[ -d $1 && $total -gt 0 ]]; then
      if [[ $args == $2 ]]; then
        echo "$1/$args" 
      fi
      listado "${1}/${args}" $2
    fi

  done <<< $(ls -A $1 2> /dev/null);
}

function main(){
	for args in $@; do
		listado $args tmp
	done
	
	#while read args; do
	#	echo $args
	#done <<< $(cat /tmp/archivos.txt)
}
