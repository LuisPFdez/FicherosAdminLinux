# Instalador 
Permite definir en un json paquetes y comandos para que sean ejecutados o instalados. Permitiendo establecer una plantilla para configurar un servidor rápidamente. Es posible establecer ciertos parámetros de configuración en el json o usar un archivo json de configuración.

Para ejecutar el instalador (dentro de la carpeta de este) ejecuta `./instalador archivo.json`. 
Los parámetros han de ser archivos json, que se ejecutarán en orden secuencial 

**Si solo se ejecuta `./instalador` intentará ejecutar el archivo config.json**

## Distribuciones
Para instalar los paquetes o comprobar si estos están instalados, el script, usa el sistema de paquetes propio de cada distribución. 

El script, soporta el sistema de paquetes de **debian** y **arch linux**. 

Para añadir un nuevo sistema de paquetes, es necesario,  añadir al objeto **sistema_paquetes** una nueva propiedad, con el ID de la distro, o en casos como el de ubuntu, el ID de la distro de la que deriva y como valor otro objeto con las propiedades **instalar** y **comprobar**, cada uno con su correspondiente comando. 

La información para el ID se encuentra en **/etc/os-release**, las propiedades **ID** (identificador de la distribución) y **ID_LIKE** (identificador de la distribución de la deriva, no aparece si no deriva de ninguna). El **ID_LIKE** ha de ser la clave de la propiedad (en caso de estar, en caso contrario el **ID**)

El comando ha de ser un array, cada posición del array corresponde a un argumento, ( **apt install -y** -> `["apt", "install", "-y" ]`
```python
    "ID distribucion": {
       "instalar": ["apt", "install", "-y" ],
        "comprobar": ["dpkg", "-s"]
    },
```
Para instalar o comprobar un paquete, se obtendrá el comando correspondiente y se añadirá al final el nombre del paquete.

El script utiliza un paquete, **distro**, para obtener información acerca de la distribución de linux, ciertas distros, como arch linux no lo incluyen por defecto. 

El paquete puede ser instalado mediante [pip](https://pip.pypa.io/en/stable/getting-started/).

También se puede establecer como un **parámetro de configuración** en el json o en un archivo de configuración

## Configuracion JSON 

Es posible establecer ciertos parámetros de configuración, permitiendo facilitar la ejecución de los comandos. 

### Archivo de configuración y configuración local 

Es posible establecer configuración tanto a nivel global, archivo especifico de configuración, como a nivel del propio archivo de comandos. Algunos parámetros y funcionalidades son específicos de cada tipo de configuración, mientras que, otros, serán permitidos en ambos tipos aunque en dependiendo del parámetro se aplicará el de una configuración u otra.

También es posible definir el comportamiento en caso de error (Finalizar la aplicación o continuar la ejecución). Ciertos parámetros finalizaran la ejecución aunque en caso de error se haya establecido en continuar.

**A diferencia de los comandos, no es necesario un determinado orden para los parámetros**

### Variables 
Es posible establecer variables para los comandos y las dependencias (configuración local). 

Las variables pueden ser:
- **Globales**, declaradas en el archivo de configuración, se aplican para todos los archivos 
- **Locales**, declaradas en el propio archivo, se aplican unicamente a ese archivo. Si una variable local y una global tienen el mismo nombre, el archivo usará la variable local.

Para llamar a una variable usaremos **\${}**, con el nombre de la variable y este sera sustituida por el valor de la variable. Por ejemplo **${variable}**.

En caso de que la variable no exista se quedara igual. 

Si queremos que la variable no sea sustituida por su valor, es necesario añadir una **doble barra invertida**, entre el símbolo del dolar y la llave **$\\\\{variable}**. La doble barra invertida será eliminada automáticamente.

### Archivo configuración
Archivo especifico para configuración (no permite ejecutar parámetros). **Solo puede haber uno por ejecución**, en caso de haber más de uno, se ignorarán todos salvo el primero.

Parámetros:
- **archivo_configuracion**, establece que es un archivo de configuración, ha de tener el valor **True**
- **distro**, establece la distribución, en caso de no establecerse intentara obtenerla de forma automática, en caso de no tener el paquete distro, mostrará un error y finalizará la ejecución. Su valor puede ser **arch** o **debian**. Si ya se ha definido la distro, independientemente del tipo de configuración, se ignorará este parámetro
- **contiene_instalar**, si se establece a **False**, ignorará la distro. Si se ejecuta algún comando de instalar, el comando se intentará ejecutar normal pero lanzará un error al no haberse establecido la forma de instalación. Si algún archivo no establece el parámetro a false (independientemente del tipo), intentará cargar el sistema de paquetes de la distro (si **distro** esta establecido, usará distro, en caso contrario lo hará automáticamente)
- **variables**, objecto que contiene las variables globales
- **contiene_variables**, si se establece a **False** evita renderizar variables. Si no se declara pero se establece el **objeto de variables** es tratado como **True**, en caso contrario, como **False**
- **finalizar_error**, define el comportamiento en caso de error (continua o finalizar ejecución), si el valor es **False** continuará con la ejecución, cualquier otro valor hará finalizar el código en caso de error (comportamiento por defecto) al establecerse ignorara los **finalizar_error** de la configuración local.
- **ficheros**, archivo(s) json para ejecutar, se ejecutan después de finalizar con el archivo de configuración. Puede ser un **string** o una **lista**
- **dependencias**, **string** o **listado** de archivo(s) necesarios. Se comprobará si son ficheros (independientemente de su extensión) y si existen
- **sudo**, en caso de ser **True**, comprueba se ha ejecutado como **super usuario**

La configuración global se aplica a todos los ficheros json que son llamados después de este (archivos pasados por parámetro y la propiedad **ficheros**)

### Archivo local
JSON, con los comandos para ejecutar. Permite también parámetros de configuración local

Parámetros de configuración:
- **distro**, similar a **distro** del [archivo de configuración](#archivo-configuración)
- **contiene_instalar**, similar a **contiene_instalar** del **archivo de configuración**
- **variables**, objecto que contiene las variables propias del archivo, en caso de que alguna de las variables locales tenga el mismo nombre que las globales, primaran las variables locales
- **contiene_variables**, similar a **contiene_variables** del **archivo de configuración**, en caso de establecerse, su valor primará sobre el valor global. Si no se establece pero existe el objeto **variables**, se establecerá a true en local. En caso contrario tomará el valor global.
- **finalizar_error**, similar a **finalizar_error** del **archivo de configuración**. El valor global tendrá preferencia sobre el local
- **dependencias**, similar a **dependencias** del **archivo de configuración**. El parámetro local permite el uso de variables.
- **sudo**, similar a **sudo** del **archivo de configuración**
- **comandos**: **lista** de [comandos](#estructura-de-json-comandos). 

Los archivos JSON, que no sean de configuración pueden ser un objeto, cuyas propiedades servirán para definir la configuración local o una lista, que será tratada igual que el parámetro **comandos**. 

**Aunque el archivo se componga únicamente de comandos para ejecutar, permitirá variables globales**

#### Estructura de JSON (Comandos)
* Todos los elementos han de estar contenidos en una lista
* Las cadenas que no pertenezcan a un objeto son tratados como paquetes
* Las claves de los objetos:
    * **paquete** -> nombre del paquete a instalar, su valor ha de ser una cadena
    * **comando** -> comando para ejecutar, su valor ha de ser una cadena o una lista
    * **comprobar** -> recibe un lista, con tres o cuatro valores:
        1. El primer valor ha de ser un comando
        2. El primer valor ha de ser un valor para comparar con la salida del comando
        3. El tercer valor será un comando que se ejecutará en caso de coincidir los anteriores valores, puede ser una cadena o un lista
        4. El cuarto valor, opcional, será el comando que se ejecutará en caso de no coincidir los valores, puede ser una cadena o un lista
    * **comprobar_comando** -> recibe un lista, con tres o cuatro valores:
        1. El primer valor ha de ser un comando
        2. El primer valor ha de ser un número, el codigo de salida, esperada, del comando
        3. El tercer valor será un comando que se ejecutará en caso de coincidir los anteriores valores, puede ser una cadena o un lista
        4. El cuarto valor, opcional, será el comando que se ejecutará en caso de no coincidir los valores, puede ser una cadena o un lista

El archivo [config.json](config.json), imita al [instalador.sh](../instalador/instalador.sh) \
Ejemplo de uso: 
```json
    [
        "Nombre de un paquete", 
        {
            "paquete": "nombre paquete",
            "comando": "comando",
            "comprobar": [
                "comando",
                "resultado esperado",
                "comando"
            ],
            "comprobar_comando": [
                "comando para comprobar salida",
                2,
                "comando"
            ]
        },
        {
            "comando": [
                "comando",
                "comando"
            ],
            "comprobar": [
                "comando",
                "resultado esperado",
                "comando",
                "comando2"
            ],
            "comprobar_comando": [
                "comando para comprobar salida",
                2,
                "comando",
                "comando2"
            ]
        }
    ]
```