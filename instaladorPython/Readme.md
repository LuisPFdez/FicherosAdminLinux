# Instalador 
Permite definir en un json paquetes y comandos para que sean ejecutados o instalados. Permitiendo establecer una plantilla para configurar un servidor, **basado en debian**, rapidamente

## Estructura de JSON
* Todos los elementos han de estar contenidos en una lista
* Las cadenas que no pertenezcan a un objeto son tratados como paquetes
* Las claves de los objetos:
    * **paquete** -> nombre del paquete a instalar, su valor ha de ser una cadena
    * **comando** -> comando para ejecutar, su valor ha de ser una cadena o una lista
    * **comprobar** -> recibe un lista, con tres o cuatro valores:
        1. El primer valor ha de ser un comando
        2. El primer valor ha de ser un valor para comparar con la salida del comando
        3. El tercer valor será un comando que se ejecutará en caso de coincidir los anteriores valores
        4. El cuarto valor, opcional, será el comando que se ejecutará en caso de no coincidir los valores

El archivo [config.json](config.json), imita al [instalador.sh](../instalador/instalador.sh)
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