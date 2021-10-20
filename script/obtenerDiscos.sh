#!/bin/bash
lsblk -l | awk '
BEGIN{
    print "Nombre:Tipo:Tamaño:Montura"
    print "-----:-----:-----:-----"
}{
if ( $3 == 0 ){        
    if ( $6 == "disk"){
        disco = $1;
        printf "%s:Disco:%s:%s\n", $1, $4, $7;
    } else if ( $6 == "part" ){
        printf "%s:Part-[%s]:%s:%s\n", $1, disco, $4, $7;
    }
} else if ( $3 == 1 ){
    if ( $6 == "disk"){
        disco = $1;
        printf "%s:Extraible:%s:%s\n", $1, $4, $7;
    } else if ( $6 == "part" ){
        printf "%s:ParExt-[%s]:%s:%s\n", $1, disco, $4, $7;
    }
}}' | column -s ':' -t 