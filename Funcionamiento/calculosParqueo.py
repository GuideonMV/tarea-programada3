#Elaborado por: Jimena Acuña Parra y Guideon Montero Vargas
#Fecha de elaboración: 11/06/2026 11:24 am
#Última fecha de modificación: 29/04/2026 7:47 pm
#Versión: 3.14.3

#Librerías
import datetime

#Funciones
def calcularEspeciales(tamano):
    """
    Funcionalidad:
    Calcula la cantidad de espacios reservados especiales segun el 5%
    del tamano del estacionamiento, respetando el minimo de 2 espacios
    exigido por ley para parqueos pequenios.
    Entrada:
    - tamano (int): Tamano total del estacionamiento.
    Salida:
    - especiales (int): Cantidad de espacios especiales a reservar.
    """
    especiales = (tamano * 5 + 99) // 100
    if especiales < 2:
        especiales = 2
    return especiales

def calcularPorAsignar(tamano, especiales, tieneElectrico):
    """
    Funcionalidad:
    Calcula la cantidad de espacios disponibles para asignar (generales),
    restando los espacios especiales y el espacio electrico si corresponde.
    Entrada:
    - tamano (int): Tamano total del estacionamiento.
    - especiales (int): Cantidad de espacios especiales reservados.
    - tieneElectrico (bool): True si el parqueo tiene espacio electrico.
    Salida:
    - porAsignar (int): Cantidad de espacios generales disponibles para asignar.
    """
    porAsignar = tamano - especiales
    if tieneElectrico:
        porAsignar = porAsignar - 1
    return porAsignar

def calcularTopeMasivo(porAsignar):
    """
    Funcionalidad:
    Calcula el tope maximo de vehiculos que pueden asignarse en el
    llenado masivo, reservando el 5% de los espacios generales para
    clientes nuevos.
    Entrada:
    - porAsignar (int): Cantidad de espacios generales disponibles.
    Salida:
    - topeMasivo (int): Cantidad maxima de espacios a llenar masivamente.
    """
    reservaNuevos = (porAsignar * 5 + 99) // 100
    topeMasivo = porAsignar - reservaNuevos
    return topeMasivo

def calcularDistribucionEspacios(tamano, tieneElectrico):
    """
    Funcionalidad:
    Calcula la distribucion completa de espacios del estacionamiento:
    especiales, electrico, por asignar y tope masivo, segun el tamano
    y si el parqueo tiene espacio electrico.
    Entrada:
    - tamano (int): Tamano total del estacionamiento.
    - tieneElectrico (bool): True si el parqueo tiene espacio electrico.
    Salida:
    - distribucion (dict): Diccionario con las cantidades de especiales,
      electrico, porAsignar y topeMasivo.
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

def obtenerUbicacionesOcupadas(listaObjetos):
    """
    Funcionalidad:
    Obtiene el conjunto de ubicaciones actualmente ocupadas, es decir,
    las que pertenecen a vehiculos sin hora de salida registrada.
    Entrada:
    - listaObjetos (list): Lista de objetos Estacionamiento.
    Salida:
    - ubicacionesOcupadas (set): Conjunto de ubicaciones ocupadas.
    """
    ubicacionesOcupadas = set()
    for objeto in listaObjetos:
        if objeto.fechaHoraSalida == "":
            ubicacionesOcupadas.add(objeto.ubicacion)
    return ubicacionesOcupadas

def buscarObjetoPorUbicacion(listaObjetos, ubicacion):
    """
    Funcionalidad:
    Busca el objeto Estacionamiento que ocupa actualmente una ubicacion
    especifica del parqueo.
    Entrada:
    - listaObjetos (list): Lista de objetos Estacionamiento.
    - ubicacion (str): Identificador de la ubicacion a buscar.
    Salida:
    - objeto (Estacionamiento): Objeto encontrado, o None si la
      ubicacion esta libre.
    """
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