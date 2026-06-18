def calcularEspeciales(tamano):
    especiales = (tamano * 5 + 99) // 100
    if especiales < 2:
        especiales = 2
    return especiales

def calcularPorAsignar(tamano, especiales, tieneElectrico):
    porAsignar = tamano - especiales
    if tieneElectrico:
        porAsignar = porAsignar - 1
    return porAsignar

def calcularTopeMasivo(porAsignar):
    reservaNuevos = (porAsignar * 5 + 99) // 100
    topeMasivo = porAsignar - reservaNuevos
    return topeMasivo

def calcularDistribucionEspacios(tamano, tieneElectrico):
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

def obtenerUbicacionesOcupadas(listaObjetos):
    ubicacionesOcupadas = set()
    for objeto in listaObjetos:
        if objeto.fechaHoraSalida == "":
            ubicacionesOcupadas.add(objeto.ubicacion)
    return ubicacionesOcupadas

def buscarObjetoPorUbicacion(listaObjetos, ubicacion):
    for objeto in listaObjetos:
        if objeto.ubicacion == ubicacion and objeto.fechaHoraSalida == "":
            return objeto
    return None