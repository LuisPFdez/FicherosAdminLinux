# Instalador 
Permite definir en un json paquetes y comandos para que sean ejecutados o instalados. Permitiendo establecer una plantilla para configurar un servidor rápidamente

## Distribuciones
Para instalar los paquetes o comprobar si estos estan instalados, el script, usa el sistema de paquetes propio de cada distribución. 

El script (de momento), soporta el sistema de paquetes de **debian** y **arch linux**. 

Para añadir un nuevo sistema de paquetes, es necesario,  añadir al objeto **sistema_paquetes** una nueva propiedad, con el ID de la distro, o en casos como el de ubuntu, el ID de la distro de la que deriva y como valor otro objeto con las propiedades **instalar** y **comprobar**, cada uno con su correspondiente comando. 

La información para el ID se encuentra en **/etc/os-release**, las propiedades **ID** (identificador de la distribución) y **ID_LIKE** (identificador de la distribución de la deriva, no aparece si no deriva de ninguna). El **ID_LIKE** ha de ser la clave de la propiedad ( en caso de estar, en caso contrario el **ID**)

El comando ha de ser un array, cada posición del array corresponde a un argumento, ( **apt install -y** -> `["apt", "install", "-y" ]`
```python
    "ID distribucion": {
       "instalar": ["apt", "install", "-y" ],
        "comprobar": ["dpkg", "-s"]
    },
```
El script utiliza un paquete, **distro**, para obtener información acerca de la distribución de linux, ciertas distros, como arch linux no lo incluyen por defecto. 

El paquete puede ser instalado mediante [pip](https://pip.pypa.io/en/stable/getting-started/).

Tambien se puede modificar el código para selecionar manualmente la distro.

```python
    #Sustituir - paquete = cargar_paquete() - por : 
    paquete = sistema_paquetes.get("Nombre distro")
```

## Estructura de JSON
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
            ]
        }
        {
            "comando": [
                "comando",
                "comando",
            ],
            "comprobar": [
                "comando",
                "resultado esperado",
                "comando",
                "comando2"
            ]
        }
    ]
```