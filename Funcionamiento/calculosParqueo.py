def calcularEspeciales(tamano):
    """
    Funcionalidad: Calcula la cantidad de espacios especiales segun el 5% del tamano,
    respetando el minimo legal de 2 espacios para parqueos pequenos.
    Entrada:
    - tamano (int): Cantidad total de espacios del parqueo.
    Salida:
    - especiales (int): Cantidad de espacios especiales a reservar.
    """
    especiales = (tamano * 5 + 99) // 100
    if especiales < 2:
        especiales = 2
    return especiales


def calcularPorAsignar(tamano, especiales, tieneElectrico):
    """
    Funcionalidad:Calcula la cantidad de espacios disponibles para alquilar,
    restando los especiales y el espacio electrico si corresponde.
    Entrada:
    - tamano (int): Cantidad total de espacios del parqueo.
    - especiales (int): Cantidad de espacios especiales reservados.
    - tieneElectrico (bool): Indica si el parqueo tiene espacio para vehiculos electricos.
    Salida:
    - porAsignar (int): Cantidad de espacios disponibles para alquilar.
    """
    porAsignar = tamano - especiales
    if tieneElectrico:
        porAsignar = porAsignar - 1
    return porAsignar


def calcularTopeMasivo(porAsignar):
    """
    Funcionalidad:
    Calcula el tope maximo de espacios que se pueden llenar
    en el llenado masivo, dejando un 5% libre para clientes nuevos.
    Entrada:
    - porAsignar (int): Cantidad de espacios disponibles para alquilar.
    Salida:
    - topeMasivo (int): Cantidad maxima de espacios a llenar masivamente.
    """
    reservaNuevos = (porAsignar * 5 + 99) // 100
    topeMasivo = porAsignar - reservaNuevos
    return topeMasivo


def calcularDistribucionEspacios(tamano, tieneElectrico):
    """
    Funcionalidad:
    Calcula la distribucion completa de espacios del parqueo:
    especiales, electrico, por asignar y tope maximo masivo.
    Entrada:
    - tamano (int): Cantidad total de espacios del parqueo.
    - tieneElectrico (bool): Indica si el parqueo tiene espacio para vehiculos electricos.
    Salida:
    - distribucion (dict): Diccionario con las llaves especiales, electrico,
      porAsignar y topeMasivo.
    """
    especiales = calcularEspeciales(tamano)
    porAsignar = calcularPorAsignar(tamano, especiales, tieneElectrico)
    topeMasivo = calcularTopeMasivo(porAsignar)
    cantidadElectrico = 0
    if tieneElectrico:
        cantidadElectrico = 1
    distribucion = {
        "especiales": especiales,
        "electrico": cantidadElectrico,
        "porAsignar": porAsignar,
        "topeMasivo": topeMasivo
    }
    return distribucion