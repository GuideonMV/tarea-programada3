def construirCatalogos(listasUnicas):
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
    for codigo in catalogo:
        if catalogo[codigo] == texto:
            return codigo
    nuevoCodigo = len(catalogo) + 1
    catalogo[nuevoCodigo] = texto
    return nuevoCodigo

def obtenerTextoPorCodigo(catalogo, codigo):
    if codigo in catalogo:
        return catalogo[codigo]
    return "Desconocido"

def construirCatalogoPagos():
    catalogoPagos = {
        1: "Efectivo",
        2: "SINPE",
        3: "Tarjeta"
    }
    return catalogoPagos