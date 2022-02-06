#!/usr/bin/env python3
import subprocess
from json import load, loads, dumps
from os import geteuid, path
from sys import argv
from string import Template

#La clase colores permitira mostrar mensajes mas personalizados
class Colores:
    ROJO = '\033[31;1m'
    FINC = '\033[m'
    VERDE = '\033[32;1m'
    AMARILLO = '\033[33;1m'
    AZUL = '\033[34;1m'

# Clase propia que extiende de template
class Plantilla(Template):
    # Fija el patron para renderizar una variable
    pattern = r"""
        \$(?:
        (?P<escaped>\\\\)               | # Evita el caracter de escape
        (?P<named>(?!))                 | # Evita la renderizar la variable que no esta entre llaves
        \{(?P<braced>[A-Z_][A-Z_\-\d]+)\} | # Renderiza variable entre llaves
        (?P<invalid>)
    )"""

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

# Diccionario para almacenar los parametros del fichero de configuracion
archivo_config = {
    #  Almacena si el archivo de configuracion se ha inciado
    "iniciado": False,
    # Valor de la propiedad de contiene_variables de la configuracion, por defecto en falso
    "contiene_variables": False,
    # El diccionario con las variables del archivo de configuracion, por defecto un diccionario vacio
    "variables": {},
    # Valor de la propiedad de finalizar_error, por defecto en falso
    "finalizar_error": None,
}

#Variable global para almacenar el diccionario con los comandos del sistema de paquetes
paquete = None

# Funcion encargada de manejar como ha de comportarse el codigo en caso de error, por defecto el codigo finaliza en el caso de error
def funcion_error(codigo): return exit(codigo)

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
#ejecutara otro parametro opcional, en caso de haberse pasado
def comprobar(comando):
    try:
        #Si el parametro comando no es una lista lanza una excepcion
        if not type(comando) is list:
            raise Exception("El valor ha de ser un array")
        #Ejecuta el comando, establece el parametro shell a true para evitar problemas con ciertos aspectos de la shell
        #Los errores son redigidos al dev/null y la salida a la variable salida. En caso de erro lanza excepcion
        salida = subprocess.run(comando[0], shell=True ,check=True, stderr=subprocess.DEVNULL, text=True ,stdout=subprocess.PIPE)
        if salida.stdout.strip()  == str(comando[1]): #Comprueba si la salida es igual a lo esperado
            ejecutar_comando(comando[2]) #En caso afirmativo ejecuta el comando
        elif len(comando) == 4: #Comprueba la longitud, caso de ser 4 ejecuta el otro parametro
            ejecutar_comando(comando[3])
    except (subprocess.CalledProcessError) as error: #Captura la excepcion que lanza subprocess y muestra un mensaje
        print(Colores.ROJO+"Error al hacer la comprobacion,  codigo de error: "+str(error.returncode)+Colores.FINC)
        funcion_error(1) #Funcion que determina el comportamiento del codigo en un error

#Comprueba la salida de un comando sea el esperado y ejecuta un comando. en caso contrario, 
#ejecutara otro comando opcional, en caso de haberse pasado
def comprobar_comando(comando): 
    try:
        #Si el parametro comando no es una lista lanza una excepcion
        if not type(comando) is list:
            raise Exception("El valor ha de ser un array")
        #Ejecuta el comando, establece el parametro shell a true para evitar problemas con ciertos aspectos de la shell
        #Los errores son redigidos al dev/null y la salida a la variable salida.
        salida = subprocess.run(comando[0], shell=True ,check=False, stderr=subprocess.DEVNULL, text=True ,stdout=subprocess.PIPE)
        if salida.returncode  == int(comando[1]): #Comprueba si el codigo de ejecucion es igual al esperado
            ejecutar_comando(comando[2]) #En caso afirmativo ejecuta el comando
        elif len(comando) == 4: #Comprueba la longitud, caso de ser 4 ejecuta el otro comando
            ejecutar_comando(comando[3])
    except ValueError as error: #En caso de que el codigo de salida no sea un número
        print(Colores.ROJO+"Error, el codigo de salida del comando ha de ser un numero"+Colores.FINC)
        funcion_error(1) #Funcion que determina el comportamiento del codigo en un error

    

#Funcion para ejecutar un comando, comprueba si ese comando es una lista o un string
def ejecutar_comando(comando):
    try:
        if type(comando) is list: #Comprueba si se le ha pasado una lista de comandos o un comando solo
            for com in comando:#Recorre la lista
                subprocess.run(com, shell=True ,check=True, stderr=subprocess.DEVNULL) #Ejecuta el comando
        elif type(comando) is str: # Comprueba si comando es un string
            subprocess.run(comando, shell=True ,check=True, stderr=subprocess.DEVNULL)#Ejecuta el comando
        else: # En caso de no ser ni una lista ni un string lanza una excepcion
            raise Exception("El comando ha de ser una lista o un string") 
    except (subprocess.CalledProcessError) as error: #Captura la excepcion de subprocess y muesta un mensaje y el codigo que devuelve
        print(Colores.ROJO+"Error al ejecutar el comando, codigo devuelto devuelto: "+str(error.returncode)+Colores.FINC)    
        funcion_error(1) #Funcion que determina el comportamiento del codigo en un error

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
            elif llave == "comprobar_comando": #Comprueba si la clave es igual a "comprobar_comando"
                comprobar_comando(comando[llave])

#Seleciona el sistema de gestion de paquetes en funcion de la distribucion
def cargar_paquete (): 
    try:
        #Prueba a importar el paquete distro
        from distro import like, id as distro_id
    except:
        #En caso de no poder muetra un mensaje y cierra la aplicacion
        print(Colores.AZUL+"El paquete "+Colores.VERDE+"distro "+Colores.AZUL+"no esta instalado"+Colores.FINC)
        funcion_error(1) #Funcion que determina el comportamiento del codigo en un error
    
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

#Funcion que comprueba si existen los archivos pasados por dependencia
def comprobar_dependencias ( dependencias ):
    #Comprueba si dependencias es un string
    if type(dependencias) is str:
        # Comprueba si el archivo existe, en caso de no existir lanza un mensaje de error
        if not path.isfile(dependencias):
            print(Colores.ROJO+"El archivo "+Colores.AMARILLO+dependencias+Colores.ROJO+" no existe"+Colores.FINC) # Mensaje de error
            funcion_error(1)  #Funcion que determina el comportamiento del codigo en un error
    # Comprueba si dependencias es un list
    elif type(dependencias) is list:
        # Recorre dependencias
        for dependencia in dependencias:
            # Comprueba si el archivo existe, en caso de no existir lanza un mensaje de error
            if not path.isfile(dependencia):
                print(Colores.ROJO+"El archivo "+Colores.AMARILLO+dependencia+Colores.ROJO+" no existe"+Colores.FINC) # Mensaje de error
                funcion_error(1) #Funcion que determina el comportamiento del codigo en un error
    elif dependencias is None: # En caso de que dependencias no tenga valor, no devuelve ningun valor
        return None # Acaba la funcion pero no devuelve nada
    else: # En caso de tener un tipo distinto a los anteriores lanza una excepcion
        raise Exception("Error: el tipo de dependencias ha de ser un listado o un string") # Lanza una excepcion

# Funcion encargada de renderizar las variables de comandos y dependencias, y ejecutar los comandos
# El primer argumento es el json con los comandos, el segundo los archivos de los que depende ( tambien pueden contener variables )
# el tercero las variables locales del archivo y por ultimo la propiedad que indica si ha de renderizarse
# Salvo el primer argumento todos son opcionales y estan inicializados a None
def renderizar_variables ( json, dependencias = None, json_variables = None, contiene_variables = None  ):
    # Por defecto no se intenta remplazar las variables
    renderizar = False

    # Si las variables y la propiedad que contiene las variables son nulas asina el valor de contiene_variables del archivo de configuracion
    if json_variables is None and contiene_variables is None:
        renderizar = archivo_config["contiene_variables"] # Asigna a renderizar el valor de contiene_variables de archivo_config
    #Si el archivo tiene variables declaradas y contiene_variables es nulo, se renderizaran las variables
    elif type(json_variables) is dict and contiene_variables is None: 
        renderizar = True # Asigna True a renderizar
    else: # En el caso de que contiene_variables este declarado, independientemente de si lo esta json_variables
        renderizar = contiene_variables # Asigna a renderizar el valor de contiene_variables 
    
    #Si renderizar es igual a True
    if renderizar == True: # (En caso de que el valor sea 1 tambien entrará)
        # Hace una copia de la lista variables, de la variable global archivo_config y la almacena en datos_renderizado
        datos_renderizado = archivo_config["variables"].copy()
        # Actualiza la variable datos_renderizado con las variables locales del json ( en caso de tener un valor nulo usa una variable vacia)
        datos_renderizado.update( json_variables or {}) # En caso de que alguna propiedad se repita las variables locales la sobre

        # Le pasa el json convertido a string
        temp = Plantilla(dumps( json )) 
        # Sustituye las varibles por su valor
        temp = temp.safe_substitute(datos_renderizado)
        # Vuelve a convertir a un json los comandos y lo almacena en json
        json = loads(temp)

        if not dependencias is None: # Comprueba si dependencias tiene un valor nulo
            # Le pasa el json convertido a string
            temp = Plantilla(dumps( dependencias )) 
            # Sustituye las varibles por su valor
            temp = temp.safe_substitute(datos_renderizado)
            # Vuelve a convertir a un json los comandos y lo almacena en dependencias
            dependencias = loads(temp)

    # LLama a la variable comprobar dependencias y le pasa el parametro dependencias, renderizado en caso de tener algun valor
    comprobar_dependencias(dependencias)

    # Recorre los comandos
    for js in json:
        # LLama a comandos y le pasa la variable comandos renderizada
        comandos(js)

# Funcion encargada de definir el comportamiento del programa en caso de error, no todos los errores se comportan en base a esta funcion 
def definir_funcion_error ( error ):
    # Declara funcion_error como global
    global funcion_error

    if error == False: # En caso de que error sea False o 0 
        # Establece la variable funcion_error como una funcion anonima
        def funcion_error(codigo): return codigo # La funcion anonima no hace nada con el codigo, continua en caso de llamarse
    else:
        # Establece la variable funcion_error como una funcion anonima
        def funcion_error(codigo): return exit(codigo) # Establece funcion como una funcion que recibe un codigo y llama a exit 

# Funcion encargada de comprobar los valores y parametros del archivo de configuracion
def archivo_configuracion ( archivo ):
    #Define la variable como global
    global paquete

    if not archivo_config["iniciado"]: # Comprueba si ya se ha pasado antes otro archivo de configuracion
        # Establece la varible iniciado a True ( indica si se ha pasado un archivo de configuracion )
        archivo_config["iniciado"] = True
        
        # Comprueba si el archivo establece como necesario el usuario root y en caso de ser asi comprueba si el uid es igual a 0 (id del root)
        if archivo.get("sudo") == True and geteuid != 0: 
            print(Colores.ROJO+"Tienes que ser super usuario"+Colores.FINC) # Muestra un mensaje indicando que es necesario ser usuario root 
            exit(1)#Sale con el codigo de error 1
        
        # Comprueba si el archivo es de configuracion 
        if paquete is None and archivo.get("contiene_instalar") != False: # Contiene_instalar permite usar los comandos sin necesidas de cargar el sistema de paquetes
            if not archivo.get("distro") is None: # Comprueba si la distro esta declarada en el archivo
                paquete = sistema_paquetes.get(archivo.get("distro")) # Carga el sistema de paquetes apartir de la distro
            else :
                #Ejecuta la funcion cargar_paquete y guarda lo que devuelve en la variable paquete
                paquete = cargar_paquete() # Carga el paquete a traves del paquete distro 
        
        # Comprueba que la propiedad finalizar_error tenga algun valor
        if not archivo.get("finalizar_error") is None: 
            definir_funcion_error ( archivo.get("finalizar_error")) # LLama al la funcion que define el comportamiento y le pasa el valor de la propiedad
            archivo_config["finalizar_error"] = False # Establece finalizar_error en la configuracion global para que no sea sobreescrito

        # Comprueba si la propiedad dependencias esta declarada
        if archivo.get("dependencias"): 
            comprobar_dependencias(archivo.get("dependencias")) # Le pasa las dependendias a la funcion comprobar dependencias

        # Comprueba si el archivo tiene variables declaradas
        if type(archivo.get("variables")) is dict: 
            # Establece la variable que indica el valor de contiene_variables con el valor del archivo de configuracion, en caso de no estar
            # declarado lo establece a True
            archivo_config["contiene_variables"] = archivo.get("contiene_variables") or True 
            archivo_config["variables"] = archivo.get("variables") # Almacena las varibles globales
        elif type(archivo.get("contiene_variables")) is bool: # Comprueba si contiene variables es un boolean
            archivo_config["contiene_variables"] = archivo.get("contiene_variables") # Guarda el valor ed contiene_variables en la configuracion global

        # Por ultimo comprueba si se han declarado otros ficheros para ejecutar
        if archivo.get ("ficheros"):
            # LLama a la funcion obtener archivos y le pasa los ficheros a importar
            comprobador_archivos (archivo.get ("ficheros"))

    else :
        # En caso de que ya se haya pasado un archivo de configuracion se muestra un mensaje por pantalla 
        print( Colores.AMARILLO+"Aviso, ya se ha pasado antes otro archivo de configuración"+Colores.FINC )

def comprobar_configuracion (archivo): 
    #Define la variable como global
    global paquete

    # Comprueba si el archivo es de configuracion 
    if archivo.get("archivo_configuracion") == True:
        archivo_configuracion ( archivo ) # Pasa el json a la funcion encargada del archivo de configuracion

    else: # En caso de ser un archivo normal
        # Comprueba si el archivo establece como necesario el usuario root y en caso de ser asi comprueba si el uid es igual a 0 (id del root)
        if archivo.get("sudo") and geteuid != 0:
            print(Colores.ROJO+"Tienes que ser super usuario"+Colores.FINC)# Muestra un mensaje indicando que es necesario ser usuario root 
            exit(1)#Sale con el codigo de error 1
        
        # Comprueba si la varible paquete aun no se ha inicializado y el archivo no establece directamente que evita el uso del sistema de instalacion
        if paquete is None and archivo.get("contiene_instalar") != False: # Contiene_instalar permite usar los comandos sin necesidas de cargar el sistema de paquetes
            if not archivo.get("distro") is None: # Comprueba si la distro esta declarada en el archivo
                paquete = sistema_paquetes.get(archivo.get("distro")) # Carga el sistema de paquetes apartir de la distro
            else :
                #Ejecuta la funcion cargar_paquete y guarda lo que devuelve en la variable paquete
                paquete = cargar_paquete() # Carga el paquete a traves del paquete distro 
        
        # Comprueba si el archivo de configuracion ya ha definido el comportamiento en caso de error 
        if archivo_config["finalizar_error"] is None: 
            # LLama a funcion definir funcion error pasandole el valor de la propiedad finalizar_error
            definir_funcion_error ( archivo.get("finalizar_error")) # Si finalizar_error no esta declarado, se trata como false

        if not type(archivo.get("comandos")) is list: # En caso de que comandos no este definido lanza un error 
            print(Colores.ROJO+"Error, es necesario que exista la propiedad comandos y que sea una lista"+ Colores.FINC) # Mensaje de error
            exit (1) # Sale con el codigo de error 1
        
        # LLama a la funcion renderizar variables ( salvo la propiedad comandos, todas las demas variables no es necesario que esten declaradas )
        renderizar_variables(archivo.get("comandos"), archivo.get("dependencias"), archivo.get("variables"), archivo.get("contiene_variables"))

# Funcion que se encarga de convertir a json los datos del archivo y definir su comportamiento
def configuracion_archivo ( archivo ):
    json=load(archivo)#Genera un dicionario y con el contenido del archivo y lo almacena en una variable json

    if type(json) is list: #Si json es una lista llama directamente a renderizar_variables
        renderizar_variables(json) # A la funcion le pasa unicamente el json, los demas parametros tendran un valor nulo
    elif type (json) is dict: # En caso de ser un diccionario se llama a la funcion para comprobar su configuracion
        comprobar_configuracion (json)

# Funcion encargada de recorrer los archivos pasados por parametro
def comprobador_archivos(listado_archivos):
    try:
        # Comprueba si el listado de archivos es un string 
        if type(listado_archivos) is str:
            listado_archivos = [listado_archivos] # Convierte listado_archivos en una lista

        if not type(listado_archivos) is list: # Si listado_archivos no es una lista lanza una excepcion
            raise Exception("Los archivos han de ser una lista o un string")

        for archivo in listado_archivos: #Recorre todos los archivos
            with open(archivo, "r") as fichero: #Abre el archivo config.json en modo lectura
                configuracion_archivo( fichero ) # LLama a la funcion que se encarga de convertir los datos del archivo en un json
            # Muestra un mensaje indicando la finalizacion del archivo
            print ( Colores.VERDE+"Finalizada ejecucion el archivo: "+Colores.AZUL+archivo+Colores.FINC )
    
    except FileNotFoundError as fichero: #En caso de no encontrar el archivo
        print(Colores.ROJO+"Error, no existe el fichero: "+Colores.VERDE+fichero.filename+Colores.FINC) # Mensaje error
        funcion_error(1) #Funcion que determina el comportamiento del codigo en un error
    except Exception as e:#En caso de que salte otra excepcion
        print(Colores.ROJO+"Error: " + str(e) +Colores.FINC) # Mensaje error
        funcion_error(1) #Funcion que determina el comportamiento del codigo en un error

#Si el modulo es el principal
if __name__ == "__main__":
    archivos = ["config.json"] #Por defecto el archivo de configuarion es config.json
    
    if len(argv) >= 2: #Comprueba si se ha introducido algun elemento por parametro
        archivos = argv[1:] #En caso de haber introducido algun elemento, obtendra el array apartir de la segunda posicion

    #LLama a la funcion comprobador_archivo para que interprete la informacion de los json
    comprobador_archivos( archivos )

    # Muestra un mensaje de finalizacion del script 
    print(Colores.AZUL+"Finalizado script"+Colores.FINC);