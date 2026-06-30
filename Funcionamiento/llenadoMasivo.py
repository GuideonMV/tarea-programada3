#Elaborado por: Jimena Acuña Parra y Guideon Montero Vargas
#Fecha de elaboración: 11/06/2026 11:24 am
#Última fecha de modificación: 29/04/2026 7:47 pm
#Versión: 3.14.3

#Librerías
import random
import datetime

#Importación de funciones
from modelos.estacionamiento import Estacionamiento
from funcionamiento.catalogos import obtenerCodigoPorTexto

#Funciones
def generarUbicacionesGenerales(cantidad):
    """
    Funcionalidad:
    Genera la lista de identificadores de ubicaciones generales del
    parqueo, numeradas consecutivamente con el prefijo G.
    Entrada:
    - cantidad (int): Cantidad de ubicaciones generales a generar.
    Salida:
    - ubicaciones (list): Lista de strings con los identificadores generados.
    """
    ubicaciones = []
    for numero in range(1, cantidad + 1):
        ubicaciones.append("G" + str(numero))
    return ubicaciones

def generarHoraEntradaAleatoria():
    """
    Funcionalidad:
    Genera una hora de entrada aleatoria entre las 7:00 am y la hora
    actual del sistema, simulando que el vehiculo ingreso en algun
    momento del dia.
    Entrada:
    - Ninguna.
    Salida:
    - fechaHoraTexto (str): Fecha y hora generada en formato DD-MM-YYYY HH:MM.
    """
    ahora = datetime.datetime.now()
    apertura = ahora.replace(hour=7, minute=0, second=0, microsecond=0)
    segundosTotales = int((ahora - apertura).total_seconds())
    if segundosTotales < 0:
        segundosTotales = 0
    segundosAleatorios = random.randint(0, segundosTotales)
    horaEntrada = apertura + datetime.timedelta(seconds=segundosAleatorios)
    fechaHoraTexto = horaEntrada.strftime("%d-%m-%Y %H:%M")
    return fechaHoraTexto

def construirListaObjetos(diccionarioPlacas, ubicacionesDisponibles, catalogos):
    """
    Funcionalidad:
    Construye la lista de objetos Estacionamiento a partir del
    diccionario de placas obtenido del API, asignando una ubicacion
    disponible y una hora de entrada aleatoria a cada vehiculo.
    Entrada:
    - diccionarioPlacas (dict): Diccionario con placa como llave y los
      datos del vehiculo (marca, color, tipo) como valor.
    - ubicacionesDisponibles (list): Lista de ubicaciones libres a asignar.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    Salida:
    - listaObjetos (list): Lista de objetos Estacionamiento creados.
    """
    listaObjetos = []
    contadorId = 1
    for placa in diccionarioPlacas:
        if contadorId > len(ubicacionesDisponibles):
            break
        datosVehiculo = diccionarioPlacas[placa]
        ubicacion = ubicacionesDisponibles[contadorId - 1]
        horaEntrada = generarHoraEntradaAleatoria()
        codigoMarca = obtenerCodigoPorTexto(catalogos["marcas"], datosVehiculo["marca"])
        codigoColor = obtenerCodigoPorTexto(catalogos["colores"], datosVehiculo["color"])
        codigoTipo = obtenerCodigoPorTexto(catalogos["tipos"], datosVehiculo["tipo"])
        nuevoObjeto = Estacionamiento(contadorId,placa,codigoMarca,codigoColor,codigoTipo,ubicacion,horaEntrada,"",0,0)
        listaObjetos.append(nuevoObjeto)
        contadorId = contadorId + 1
    return listaObjetos

def generarTodasLasUbicaciones(distribucion):
    """
    Funcionalidad:
    Genera el diccionario completo de todas las ubicaciones del parqueo
    (generales, especiales y electrico) segun la distribucion calculada.
    Entrada:
    - distribucion (dict): Diccionario con las cantidades de especiales,
      electrico y porAsignar (generales).
    Salida:
    - todasUbicaciones (dict): Diccionario con las llaves generales,
      especiales y electrico, cada una con su lista de identificadores.
    """
    ubicacionesGenerales = generarUbicacionesGenerales(distribucion["porAsignar"])
    ubicacionesEspeciales = []
    for numero in range(1, distribucion["especiales"] + 1):
        ubicacionesEspeciales.append("E" + str(numero))
    ubicacionesElectrico = []
    if distribucion["electrico"] == 1:
        ubicacionesElectrico.append("V1")
    todasUbicaciones = {
        "generales": ubicacionesGenerales,
        "especiales": ubicacionesEspeciales,
        "electrico": ubicacionesElectrico
    }
    return todasUbicaciones