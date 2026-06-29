import datetime
import random

def cerrarVehiculosPendientes(listaObjetos):
    """
    Funcionalidad:
    Recorre la lista de objetos y a los vehiculos sin hora de salida les
    asigna la hora actual como salida y un tipo de pago aleatorio, simulando
    el cierre del dia. No guarda la BD, eso lo hace el llamador.
    Entrada:
    - listaObjetos (list): Lista de objetos Estacionamiento.
    Salida:
    - None
    """
    horaSalida = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    for objeto in listaObjetos:
        if objeto.fechaHoraSalida == "":
            objeto.fechaHoraSalida = horaSalida
            objeto.tipoPago = random.randint(1, 3)
    return


def calcularMontoObjeto(objeto, montoHora, tiempoGracia):
    """
    Funcionalidad:
    Calcula el monto a cobrar de un objeto segun su tiempo de estadia,
    respetando el tiempo de gracia. Si el monto del objeto ya fue
    registrado (distinto de 0), retorna ese monto directamente.
    Entrada:
    - objeto (Estacionamiento): Objeto con fechaHoraEntrada y fechaHoraSalida.
    - montoHora (int): Monto por hora en colones.
    - tiempoGracia (int): Minutos de gracia sin cobro.
    Salida:
    - monto (int): Monto total a cobrar en colones.
    """
    if objeto.monto != 0:
        return objeto.monto
    entrada = datetime.datetime.strptime(objeto.fechaHoraEntrada, "%d-%m-%Y %H:%M")
    salida  = datetime.datetime.strptime(objeto.fechaHoraSalida,  "%d-%m-%Y %H:%M")
    minutosTotal = int((salida - entrada).total_seconds() / 60)
    if minutosTotal <= tiempoGracia:
        return 0
    horasCobrar = (minutosTotal + 59) // 60
    return horasCobrar * montoHora


def agruparPorTipoPago(listaObjetos):
    """
    Funcionalidad:
    Agrupa los objetos de la lista segun su tipo de pago en un diccionario
    con tres llaves: 1 (Efectivo), 2 (SINPE) y 3 (Tarjeta).
    Entrada:
    - listaObjetos (list): Lista de objetos Estacionamiento con salida registrada.
    Salida:
    - grupos (dict): Diccionario con listas de objetos por tipo de pago.
    """
    grupos = {1: [], 2: [], 3: []}
    for objeto in listaObjetos:
        if objeto.tipoPago in grupos:
            grupos[objeto.tipoPago].append(objeto)
    return grupos
