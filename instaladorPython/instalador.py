#!/usr/bin/env python3
import subprocess, os, json, sys
#La clase colores permitira mostrar mensajes mas personalizados
class Colores:
    ROJO = '\033[31m'
    FINC = '\033[m'
    VERDE = '\033[32m'
    AMARILLO = '\033[33m'
    AZUL = '\033[34m'

#Instala mediante apt el paquete pasado por parametro
def instalar(nombre_paquete):
    try:
        #Ejecuta el comando, establece el check a true para que en caso de error lance una excepcion
        #los errores son redirigidos al dev/null 
        subprocess.run(["apt", "install", nombre_paquete, "-y"], check=True, stderr=subprocess.DEVNULL)
    #Captura la excepcion CalledProcessError
    except (subprocess.CalledProcessError) as error:
        if error.returncode == 100: #Si el codigo es 100 muestra un mensaje indicando que el paquete no existe
            print("El paquete "+Colores.AMARILLO+nombre_paquete+Colores.FINC+" no existe")
        else: #En caso contrario muestra un mensaje de error y el codigo que ha devuelto
            print(Colores.ROJO+"Error, codigo devuelto devuelto: "+error.returncode+Colores.FINC)        

#Comprueba que un paquete no este instalado, con dpkg -s 
def instalado(nombre_paquete):
    try:
        #Ejecuta el comando, tanto la salida como los errores va al dev/null, establece check para que salte una excepcion en caso de no estar instalado
        subprocess.run(["dpkg","-s", nombre_paquete], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
        #Establece la variable instalado a true
        instalado=True
    except:
        #En caso de saltar la excepcion establece la variable a false
        instalado=False
    finally:
        #Devuelve la variable booleana
        return instalado

#Compueba que el resultado de un comando sea el esperado y ejecuta otro comando, caso contrario
#ejecutara otro parametro opcional, si ha sido pasado
def comprobar(comando):
    try:
        #Si el parametro comando no es una lista lanza una excepcion
        if not type(comando) is list:
            raise Exception("El valor ha de ser un array")
        #Ejecuta el comando, establece el parametro shell a true para evitar problemas con ciertos ascepectos de la shell
        #Los errores son redigidos al dev/null y la salida a la variable salida. En caso de erro lanza excepcion
        salida = subprocess.run(comando[0], shell=True ,check=True, stderr=subprocess.DEVNULL, text=True ,stdout=subprocess.PIPE)
        if salida.stdout.strip()  == str(comando[1]): #Comprueba si la salida es igual a lo esperado
            ejecutar_comando(comando[2]) #En caso afirmativo ejecuta el comando
        elif len(comando) == 4: #Comprueba la longitud, caso de ser 4 ejecuta el otro parametro
            ejecutar_comando(comando[3])
    except (subprocess.CalledProcessError) as error: #Captura la excepcion que lanza subprocess y muestra un mensaje
        print(Colores.ROJO+"Error, codigo de error: "+error.returncode+Colores.FINC)
    
def ejecutar_comando(comando):
    try:
        if type(comando) is list: #Comprueba si se le ha pasado una lista de comandos o un comando solo
            for com in comando:#Recorre la lista
                subprocess.run(com, shell=True ,check=True, stderr=subprocess.DEVNULL) #Ejecuta el comando
        else:
            subprocess.run(comando, shell=True ,check=True, stderr=subprocess.DEVNULL)#Ejecuta el comando
    except (subprocess.CalledProcessError) as error: #Captura la excepcion de subprocess y muesta un mensaje y el codigo que devuelve
        print(Colores.ROJO+"Error, codigo deveulto devuelto: "+error.returncode+Colores.FINC)    

#Funciona a la que se le pasaran los valores del json
def comandos(comando):
    if type(comando) is str and not instalado(comando): #Comprueba si el parametro es un string y si el paquete no esta instalado
        instalar(comando) #Instala el paquete
    elif type(comando) is dict: #Comprueba si el parametro es diccionario
        for llave in comando:#Recorre parametro
            if llave == "paquete" and not instalado(comando[llave]): #Comprueba si la clave es "paquete" y si no esta instalado el paquete
                instalar(comando[llave]) #LLama a la funcion instalar
            elif llave == "comando": #Comprueba si la clave es igual a "comando"
                ejecutar_comando(comando[llave])
            elif llave == "comprobar": #Comprueba si la clave es igual a "comprobar"
                comprobar(comando[llave])


if __name__ == "__main__":
    archivos = ["config.json"] #Por defecto el archivo de configuarion es config.json
    if os.geteuid() != 0: #Comprueba si el script se esta ejecutando como super usuario, en caso de que el uid no sea 0
        print("Tienes que ser super usuario")#Muestra un mensaje
        exit(1)#Sale con el codigo de error 1
    
    if len(sys.argv) >= 2: #Comprueba si se ha introducido algun elemento por parametro
        archivos = sys.argv[1:] #En caso de haber introducido algun elemento, obtendra el array apartir de la segunda posicion
    
    for archivo in archivos: #Recorre todos los archivos
        try:
            with open(archivo, "r") as fichero: #Abre el archivo config.json en modo lectura
                json=json.load(fichero)#Genera un dicionario y con el contenido del archivo y lo almacena en una variable json
            if not type(json) is list: #Si json no es una lista lanza una excepcion
                raise Exception("Todos los elementos han de estar en una lista")
            for js in json:#Recorre json
                comandos(js) #LLama a la funcion comandos y le pasa la variable js
        except FileNotFoundError as fichero: #En caso de no encontrar el archivo
            print(Colores.ROJO+"Error, no existe el fichero: "+Colores.VERDE+fichero.filename+Colores.FINC)
        except Exception  as e:#En caso de que salte otra excepcion
            print("Error: ", e)