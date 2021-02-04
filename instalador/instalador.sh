#!/bin/bash
if [[ $(id -u) -eq 0 ]]; then
	apt update
	apache2 --version 2> /dev/null 
	if [[  $? -ne 0 ]]; then
		apt install apache2 -y
		if [[ $(cat /etc/passwd | grep "operadorweb" | wc -l) -eq 0 ]]; then
			useradd -s /bin/bash --no-create-home -G www-data -d /var/www/html operadorweb
			echo operadorweb:paso | chpasswd
		fi
		chown -R operadorweb:www-data /var/www/html
		chmod -R 2775 /var/www/html
	fi
	php --version 2> /dev/null
	if [[ $? -ne 0 ]]; then
		apt install php7.4 -y			
	fi
	if [[ $( php -m | grep "xdebug" | wc -l ) -eq 0 ]]; then
		apt install php-xdebug -y
		cp ./xdebug.ini /etc/php/7.4/mods-available
	fi	
	mysql --version
	if [[ $? -ne 0 ]]; then
		apt install mysql-server-8.0 -y 
		apt install phpmyadmin php-mbstring -y
		mysql_secure_installation
		mysql < ./admin.sql
		sed -i 's/^bind-address/#bind-address/'/etc/mysql/mysql.conf.d/mysqld.cnf
	fi
	 named -v 2> /dev/null
	if [[ $? -ne 0 ]]; then
		apt install bind9 -y
	fi
	
else
	echo "Ejecuta el script como super usuario"
fi
