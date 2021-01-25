#!/bin/bash
if [[ $(id -u) -eq 0 ]]; then
	php --version > /dev/null
	if [[ $? -ne 0 ]]; then
		echo "PHP no esta instalado, instalando PHP 7.4"
		apt update > /dev/null
		apt install php7.4 > /dev/null
	fi
	if [[ $(php -m | grep "SimpleXML" | wc -l) -eq 0 ]]; then
		echo "Descargando el modulo xml para php"
		apt install php-xml -y
	fi
	phpenmod xml
	if [[ ! -f ./phpDocumentor.phar ]]; then
		echo "Descargando phpDocumentor"
		curl -L -O https://github.com/phpDocumentor/phpDocumentor/releases/download/v3.0.0/phpDocumentor.phar > /dev/null
	fi
	chmod +x phpDocumentor.phar
	mv phpDocumentor.phar /usr/local/bin/phpDoc
else
	echo "Ejecuta el script como super usuario"
fi
