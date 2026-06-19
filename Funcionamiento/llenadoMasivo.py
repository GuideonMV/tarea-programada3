import random
import datetime

from modelos.estacionamiento import Estacionamiento
from funcionamiento.catalogos import obtenerCodigoPorTexto

def generarUbicacionesGenerales(cantidad):
    ubicaciones = []
    for numero in range(1, cantidad + 1):
        ubicaciones.append("G" + str(numero))
    return ubicaciones

def generarHoraEntradaAleatoria():
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
        nuevoObjeto = Estacionamiento(
            contadorId,
            placa,
            codigoMarca,
            codigoColor,
            codigoTipo,
            ubicacion,
            horaEntrada,
            "",
            0,
            0
        )
        listaObjetos.append(nuevoObjeto)
        contadorId = contadorId + 1
    return listaObjetos

def generarTodasLasUbicaciones(distribucion):
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