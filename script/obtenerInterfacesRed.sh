#!/bin/bash

resultado="Nombre interfaz:Tipo\n----------:----------"


for interfaz in $(ip link | awk '(NR <= 2 || $1 !~ /[0-9]*:/ ) { next }; { print $2 } ' | sed 's/:$//'); do

	if [[ -d  /sys/class/net/$interfaz/wireless/ ]]; then
		resultado="${resultado}\n${interfaz}:Wifi"
	else
		resultado="${resultado}\n${interfaz}:Ethernet"
	fi
done
echo -e $resultado | column -s ':' -t 
