#Elaborado por: Jimena Acuña Parra y Guideon Montero Vargas
#Fecha de elaboración: 11/06/2026 11:24 am
#Última fecha de modificación: 29/04/2026 7:47 pm
#Versión: 3.14.3

#Funciones
def construirCatalogos(listasUnicas):
    """
    Funcionalidad:
    Construye los catalogos de marcas, colores y tipos a partir de las
    listas unicas obtenidas del API, asignando un codigo numerico
    consecutivo a cada valor.
    Entrada:
    - listasUnicas (dict): Diccionario con las llaves marcas, colores y
      tipos, cada una con una lista de valores unicos.
    Salida:
    - catalogos (dict): Diccionario con las llaves marcas, colores y
      tipos, cada una con un diccionario de codigo a texto.
    """
    catalogos = {
        "marcas": {},
        "colores": {},
        "tipos": {}
    }
    codigo = 1
    for marca in listasUnicas["marcas"]:
        catalogos["marcas"][codigo] = marca
        codigo = codigo + 1
    codigo = 1
    for color in listasUnicas["colores"]:
        catalogos["colores"][codigo] = color
        codigo = codigo + 1
    codigo = 1
    for tipo in listasUnicas["tipos"]:
        catalogos["tipos"][codigo] = tipo
        codigo = codigo + 1
    return catalogos

def obtenerCodigoPorTexto(catalogo, texto):
    """
    Funcionalidad:
    Busca el codigo numerico correspondiente a un texto dentro de un
    catalogo. Si el texto no existe, lo agrega como un nuevo codigo.
    Entrada:
    - catalogo (dict): Diccionario de codigo a texto (marcas, colores o tipos).
    - texto (str): Texto a buscar o agregar en el catalogo.
    Salida:
    - codigo (int): Codigo numerico correspondiente al texto.
    """
    for codigo in catalogo:
        if catalogo[codigo] == texto:
            return codigo
    nuevoCodigo = len(catalogo) + 1
    catalogo[nuevoCodigo] = texto
    return nuevoCodigo

def obtenerTextoPorCodigo(catalogo, codigo):
    """
    Funcionalidad:
    Busca el texto correspondiente a un codigo numerico dentro de un
    catalogo.
    Entrada:
    - catalogo (dict): Diccionario de codigo a texto (marcas, colores o tipos).
    - codigo (int): Codigo numerico a buscar.
    Salida:
    - texto (str): Texto correspondiente al codigo, o "Desconocido" si no existe.
    """
    if codigo in catalogo:
        return catalogo[codigo]
    return "Desconocido"

def construirCatalogoPagos():
    """
    Funcionalidad:
    Construye el catalogo fijo de tipos de pago disponibles en el sistema.
    Entrada:
    - Ninguna.
    Salida:
    - catalogoPagos (dict): Diccionario con los codigos 1, 2 y 3 asociados
      a Efectivo, SINPE y Tarjeta respectivamente.
    """
    catalogoPagos = {
        1: "Efectivo",
        2: "SINPE",
        3: "Tarjeta"
    }
    return catalogoPagos