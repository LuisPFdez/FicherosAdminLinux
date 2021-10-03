#!/usr/bin/env python3
from io import TextIOWrapper
import subprocess
from json import load, loads, dumps
from os import geteuid, path
from sys import argv
from string import Template

#La clase colores permitira mostrar mensajes mas personalizados
class Colores:
    ROJO = '\033[31;0m'
    FINC = '\033[m'
    VERDE = '\033[32;1m'
    AMARILLO = '\033[33;1m'
    AZUL = '\033[34;1m'

#Gestor de paquetes de cada distribucion, se compone del comando para instalar un paquete y para comprobar si un paquete esta instalado
#El nombre de la distribucion asociada al paquete ha de ser la distribucion principal, por ejemplo para ubuntu y linux mint, debian o arch linux para manjaro
#En /etc/os-release esta el nombre tanto de la distribucion en la que se basa, como el id de la misma, en caso de no estar basada en ninguna
sistema_paquetes = {
    "debian": {
        "instalar": ["apt", "install", "-y" ],
        "comprobar": ["dpkg", "-s"]
    },
    "arch": {
       "instalar": ["pacman", "-S", "--noconfirm" ],
       "comprobar": ["pacman", "-Qi"]
    },
}

archivo_config = {
    "iniciado": False,
    "contine_variables": False,
    "variables": {},
    "finalizar_error": None,
}

paquete = None

# Funcion encargada de manejar como ha de comportarse el codigo en caso de error, por defecto el codigo finaliza el en caso de error
funcion_error = lambda codigo: exit(codigo)

#Instala mediante apt el paquete pasado por parametro
def instalar(nombre_paquete):
    try:
        #Hace una copia del array con el comando para instalar el paquete
        comando = paquete.get("instalar").copy()
        #Inserta el nombre del paquete al final del array
        comando.append(nombre_paquete)
        #Ejecuta el comando, establece el check a true para que en caso de error lance una excepcion
        #los errores son redirigidos al dev/null 
        subprocess.run( comando, check=True, stderr=subprocess.DEVNULL)
    #Captura la excepcion CalledProcessError
    except (subprocess.CalledProcessError) as error:
        if error.returncode == 100: #Si el codigo es 100 muestra un mensaje indicando que el paquete no existe
            print("El paquete "+Colores.AMARILLO+nombre_paquete+Colores.FINC+" no existe")
            funcion_error(1)
        else: #En caso contrario muestra un mensaje de error y el codigo que ha devuelto
            print(Colores.ROJO+"Error al instalar, codigo devuelto devuelto: "+str(error.returncode)+Colores.FINC)        
            funcion_error(1)

#Comprueba que un paquete no este instalado, con dpkg -s 
def instalado(nombre_paquete):
    try:
        #Hace una copia del array con el comando para comprobar si el paquete esta instalado
        comando = paquete.get("comprobar").copy()
        #Inserta el nombre del paquete al final del array
        comando.append(nombre_paquete)
        #Ejecuta el comando, tanto la salida como los errores va al dev/null, establece check para que salte una excepcion en caso de no estar instalado
        subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
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
        print(Colores.ROJO+"Error al hacer la comprobacion,  codigo de error: "+str(error.returncode)+Colores.FINC)
        funcion_error(1)

def ejecutar_comando(comando):
    try:
        if type(comando) is list: #Comprueba si se le ha pasado una lista de comandos o un comando solo
            for com in comando:#Recorre la lista
                subprocess.run(com, shell=True ,check=True, stderr=subprocess.DEVNULL) #Ejecuta el comando
        else:
            subprocess.run(comando, shell=True ,check=True, stderr=subprocess.DEVNULL)#Ejecuta el comando
    except (subprocess.CalledProcessError) as error: #Captura la excepcion de subprocess y muesta un mensaje y el codigo que devuelve
        print(Colores.ROJO+"Error al ejecutar el comando, codigo devuelto devuelto: "+str(error.returncode)+Colores.FINC)    
        funcion_error(1)

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

#Seleciona el sistema de gestion de paquetes en funcion de la distribucion
def cargar_paquete (): 
    try:
        #Prueba a importar el paquete distro
        from distro import like, id as distro_id
    except:
        #En caso de no poder muetra un mensaje y cierra la aplicacion
        print(Colores.AZUL+"El paquete "+Colores.VERDE+"distro "+Colores.AZUL+"no esta instalado"+Colores.FINC)
        funcion_error(1) 
    
    #Comprueba si la distribucion deriva de otra y si se encuentra en el objeto de sistema_paquetes
    if ( like() and like() in sistema_paquetes ):
        #Guarda los comandos en la variable paquete
        paquete = sistema_paquetes.get(like().lower())
    #Comprueba si el id de la distribucion se encuentra en el objeto de sistema_paquetes
    elif (distro_id() in sistema_paquetes ): 
        #Guarda los comandos en la variable paquete
        paquete = sistema_paquetes.get(distro_id().lower())
    else:
        #En caso de que la distribucion no se encuentre en sistema_paquetes, muestra un mensaje y cierra la apliación
        print(Colores.AZUL+"El sistema de archivos de la distribucion"+Colores.VERDE+distro_id()+Colores.AZUL+" no esta soportado"+Colores.FINC)
        exit(1)
    
    #Devuelve la variable con los comandos
    return paquete

def comprobar_dependencias ( dependencias ):
    if type(dependencias) is str:
        if not path.isfile(dependencias):
            print("El archivo no existe")
            funcion_error(1)

    elif type(dependencias) is list:
        for dependencia in dependencias:
            if not path.isfile(dependencia):
                print("El archivo no existe")
                funcion_error(1)
    else:
        raise Exception("Error provisional, el tipo de denpendencia has de ser distinto ")

def renderizar_variables ( json, dependencias = None, json_variables = None, contiene_variables = None  ):
    renderizar = False

    if json_variables is None and contiene_variables is None:
        renderizar = archivo_config["contine_variables"]
    elif type(json_variables) is dict and contiene_variables is None:
        renderizar = True
    else:
        renderizar: contiene_variables

    if renderizar: 
        datos_renderizado = archivo_config["variables"].copy()
        datos_renderizado.update( json_variables or {})

        temp = Template(dumps( json ))
        temp = temp.safe_substitute(datos_renderizado)
        temp = temp.replace("$\\\{", "${")
        json = loads(temp)
        if not dependencias is None:
            temp = Template(dumps( json ))
            temp = temp.safe_substitute(datos_renderizado)
            temp = temp.replace("$\\\{", "${")
            dependencias = loads(temp)

    comprobar_dependencias(dependencias)

    for js in json:
        print ( js )
        #ejecutar_comando(js)

def definir_funcion_error ( error ):
    if error:
        funcion_error = lambda codigo: exit(codigo)
    else:
        funcion_error = lambda codigo: codigo

def archivo_configuracion ( archivo ):
    global paquete

    if archivo.get("sudo") and geteuid != 0: # Comprueba si el archivo necesita el
            print(Colores.AZUL+"Tienes que ser super usuario"+Colores.FINC)#Muestra un mensaje
            exit(1)#Sale con el codigo de error 1

    if not archivo_config["iniciado"]:
        archivo_config["iniciado"] = True;
        if paquete is None:
            if not archivo.get("distro") is None: 
                paquete = sistema_paquetes.get(archivo.get("distro"))
            else :
                #Ejecuta la funcion cargar_paquete y guarda lo que devuelve en la variable paquete
                paquete = cargar_paquete()
        
        if archivo.get("finalizar_error") :
            definir_funcion_error ( archivo.get("finalizar_error"))
            archivo_config["finalizar_error"] = False

        if archivo.get("dependencias"): 
            comprobar_dependencias(archivo.get("dependencias"))

        if type(archivo.get("variables")) is dict: 
            archivo_config["contine_variables"] = True;
            archivo_config["variables"] = archivo.get("variables")
        elif type(archivo_config.get("contine_variables")) :
            archivo_config["contine_variables"] = archivo.get("contine_variables");

        if archivo.get ("ficheros"):
            configuracion_archivo(archivo.get ("ficheros"))
            
    else :
        print( "Ya se ha pasdado otro archivo de configuracion" )
        funcion_error(1)

def comprobar_configuracion (archivo): 
    global paquete

    if archivo.get("archivo_configuracion"):
        archivo_configuracion ( archivo )
    else: 
        if archivo.get("sudo") and geteuid != 0: # Comprueba si el archivo necesita el
            print(Colores.AZUL+"Tienes que ser super usuario"+Colores.FINC)#Muestra un mensaje
            exit(1)#Sale con el codigo de error 1
        
        if paquete is None:
            if not archivo.get("distro") is None: 
                paquete = sistema_paquetes.get(archivo.get("distro"))
            else :
                #Ejecuta la funcion cargar_paquete y guarda lo que devuelve en la variable paquete
                paquete = cargar_paquete()
        
        if archivo_config["finalizar_error"] is None: 
            definir_funcion_error ( archivo.get("finalizar_error"))
        
        if archivo.get("dependencias"): 
            comprobar_dependencias(archivo.get("dependencias"))

def configuracion_archivo ( archivo ):
    json=load(archivo)#Genera un dicionario y con el contenido del archivo y lo almacena en una variable json

    if type(json) is list: #Si json no es una lista lanza una excepcion
        renderizar_variables(json)
    elif type (json) is dict:
        comprobar_configuracion (json)



def comprobador_archivos(listado_archivos):
    try:
        if type(listado_archivos) is str:
            listado_archivos = [listado_archivos];

        if not type(listado_archivos) is list:
            raise Exception("El listado de archivo ha de ser una lista");

        for archivo in archivos: #Recorre todos los archivos
            with open(archivo, "r") as fichero: #Abre el archivo config.json en modo lectura
                configuracion_archivo( fichero )
    
    except FileNotFoundError as fichero: #En caso de no encontrar el archivo
        print(Colores.ROJO+"Error, no existe el fichero: "+Colores.VERDE+fichero.filename+Colores.FINC)
        funcion_error(1)
    except Exception as e:#En caso de que salte otra excepcion
        print(Colores.ROJO+"Error: " + str(e) +Colores.FINC)
        funcion_error(1)

#Si el modulo es el principal
if __name__ == "__main__":
    archivos = ["config.json"] #Por defecto el archivo de configuarion es config.json
    
    if len(argv) >= 2: #Comprueba si se ha introducido algun elemento por parametro
        archivos = argv[1:] #En caso de haber introducido algun elemento, obtendra el array apartir de la segunda posicion

    #LLama a la funcion comprobador_archivo para que interprete la informacion de los json
    comprobador_archivos( )