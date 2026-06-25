import datetime

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


def obtenerUbicacionesLibres(todasUbicaciones, ubicacionesOcupadas):
    """
    Funcionalidad: Calcula la lista de ubicaciones libres del parqueo, recorriendo
    las tres categorias (generales, especiales y electrico) y descartando las
    que ya estan ocupadas.
    Entrada:
    - todasUbicaciones (dict): Diccionario con las llaves generales, especiales
      y electrico, cada una con una lista de ubicaciones.
    - ubicacionesOcupadas (set): Conjunto de ubicaciones actualmente ocupadas.
    Salida:
    - ubicacionesLibres (list): Lista de ubicaciones disponibles para estacionar.
    """
    ubicacionesLibres = []
    for categoria in ("generales", "especiales", "electrico"):
        for ubicacion in todasUbicaciones[categoria]:
            if ubicacion not in ubicacionesOcupadas:
                ubicacionesLibres.append(ubicacion)
    return ubicacionesLibres

def calcularMonto(fechaHoraEntrada, montoHora, tiempoGracia):
    """
    Funcionalidad:
    Calcula el monto a cobrar segun el tiempo de estadia, respetando
    el tiempo de gracia configurado.
    Entrada:
    fechaHoraEntrada (str): Fecha y hora de entrada en formato DD-MM-YYYY HH:MM.
    montoHora (int): Monto cobrado por hora en colones.
    tiempoGracia (int): Minutos de gracia sin cobro.
    Salida:
    monto (int): Monto total a cobrar en colones.
    """
    entrada = datetime.datetime.strptime(fechaHoraEntrada, "%d-%m-%Y %H:%M")
    ahora = datetime.datetime.now()
    minutosTotal = int((ahora - entrada).total_seconds() / 60)
    if minutosTotal <= tiempoGracia:
        return 0
    horasCobrar = (minutosTotal + 59) // 60
    return horasCobrar * montoHora