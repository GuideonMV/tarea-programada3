import datetime
import random

from funcionamiento.catalogos import obtenerTextoPorCodigo
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

carpetaReportes = "reportes"
catalogoPagos = {1: "Efectivo", 2: "SINPE", 3: "Tarjeta"}

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


def crearEncabezadoPDF(pdf, altoPagina, fecha):
    """
    Funcionalidad:
    Dibuja el titulo, la fecha y los encabezados de la tabla en el PDF.
    Entrada:
    - pdf (Canvas): Objeto canvas de reportlab.
    - altoPagina (float): Altura de la pagina en puntos.
    - fecha (str): Fecha del cierre en formato DD-MM-YYYY.
    Salida:
    - posicionY (float): Posicion Y lista para empezar a dibujar filas.
    """
    pdf.setFillColorRGB(0.1, 0.2, 0.6)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, altoPagina - 50, "Cierre Diario del Parqueo")
    pdf.setFillColorRGB(0.4, 0.4, 0.4)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, altoPagina - 75, "Fecha: " + fecha)
    encabezados = ["Ubicacion", "Placa", "Entrada", "Salida", "Pago", "Monto"]
    posicionesX = [50, 110, 185, 285, 370, 440]
    posicionY = altoPagina - 110
    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica-Bold", 10)
    for i in range(len(encabezados)):
        pdf.drawString(posicionesX[i], posicionY, encabezados[i])
    posicionY = posicionY - 5
    pdf.line(50, posicionY, 550, posicionY)
    posicionY = posicionY - 15
    return posicionY

def procesarGrupoPDF(pdf, objetosGrupo, tipoPago, config, posicionY, altoPagina):
    """
    Funcionalidad:
    Dibuja las filas de un grupo de tipo de pago y su subtotal.
    Entrada:
    - pdf (Canvas): Objeto canvas de reportlab.
    - objetosGrupo (list): Lista de objetos del mismo tipo de pago.
    - tipoPago (int): Codigo del tipo de pago.
    - config (dict): Configuracion con montoHora y tiempoGracia.
    - posicionY (float): Posicion Y de inicio.
    - altoPagina (float): Altura de la pagina en puntos.
    Salida:
    - posicionY (float): Nueva posicion Y tras dibujar.
    - subtotal (int): Monto subtotal del grupo.
    """
    posicionesX = [50, 110, 185, 285, 370, 440]
    subtotal = 0
    for objeto in objetosGrupo:
        monto = calcularMontoObjeto(objeto, config["montoHora"], config["tiempoGracia"])
        objeto.monto = monto
        subtotal = subtotal + monto
        if posicionY < 80:
            pdf.showPage()
            posicionY = altoPagina - 50
        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(posicionesX[0], posicionY, objeto.ubicacion)
        pdf.drawString(posicionesX[1], posicionY, objeto.placa)
        pdf.drawString(posicionesX[2], posicionY, objeto.fechaHoraEntrada)
        pdf.drawString(posicionesX[3], posicionY, objeto.fechaHoraSalida)
        pdf.drawString(posicionesX[4], posicionY, catalogoPagos[objeto.tipoPago])
        pdf.drawString(posicionesX[5], posicionY, "{:,}".format(monto))
        posicionY = posicionY - 14
    if posicionY < 80:
        pdf.showPage()
        posicionY = altoPagina - 50
    pdf.setFillColorRGB(0.0, 0.5, 0.0)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(300, posicionY, "Subtotal " + catalogoPagos[tipoPago] + ":")
    pdf.drawString(440, posicionY, "{:,}".format(subtotal) + " colones")
    posicionY = posicionY - 8
    pdf.line(50, posicionY, 550, posicionY)
    posicionY = posicionY - 15
    return posicionY, subtotal

def generarCierreDiarioPDF(listaObjetos, catalogos, config):
    """
    Funcionalidad:
    Genera el reporte de cierre diario en formato PDF con una tabla que
    incluye ubicacion, placa, hora de entrada, hora de salida, tipo de
    pago y monto. Muestra subtotales por tipo de pago y total del dia.
    Usa 3 colores y 3 tamanios de letra.
    Entrada:
    - listaObjetos (list): Lista de objetos Estacionamiento del dia.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    - config (dict): Configuracion con montoHora y tiempoGracia.
    Salida:
    - rutaReporte (str): Ruta del archivo PDF generado.
    """
    fecha = datetime.datetime.now().strftime("%d-%m-%Y")
    rutaReporte = carpetaReportes + "/cierre_diario_" + fecha + ".pdf"
    pdf = canvas.Canvas(rutaReporte, pagesize=letter)
    anchoPagina, altoPagina = letter
    posicionY = crearEncabezadoPDF(pdf, altoPagina, fecha)
    grupos = agruparPorTipoPago(listaObjetos)
    totalDia = 0
    for tipoPago in [1, 2, 3]:
        if not grupos[tipoPago]:
            continue
        posicionY, subtotal = procesarGrupoPDF(pdf, grupos[tipoPago], tipoPago, config, posicionY, altoPagina)
        totalDia = totalDia + subtotal
    if posicionY < 80:
        pdf.showPage()
        posicionY = altoPagina - 50
    pdf.setFillColorRGB(0.7, 0.0, 0.0)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(300, posicionY, "TOTAL DEL DIA:")
    pdf.drawString(440, posicionY, "{:,}".format(totalDia) + " colones")
    pdf.save()
    return rutaReporte

def generarCierrePorTipoPagoXML(listaObjetos, catalogos, config):
    """
    Funcionalidad:
    Genera un archivo XML con tres secciones (efectivo, sinpe, tarjeta),
    donde cada seccion contiene la informacion completa y plana de cada
    objeto con ese tipo de pago. Lo guarda en memoria secundaria.
    Entrada:
    - listaObjetos (list): Lista de objetos Estacionamiento del dia.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    - config (dict): Configuracion con montoHora y tiempoGracia.
    Salida:
    - rutaXML (str): Ruta del archivo XML generado.
    """
    fecha = datetime.datetime.now().strftime("%d-%m-%Y")
    nombreArchivo = "cierre_tipo_pago_" + fecha + ".xml"
    rutaXML = carpetaReportes + "/" + nombreArchivo
    grupos = agruparPorTipoPago(listaObjetos)
    nombresSecciones = {1: "efectivo", 2: "sinpe", 3: "tarjeta"}
    lineas = []
    lineas.append('<?xml version="1.0" encoding="UTF-8"?>')
    lineas.append("<cierrePorTipoPago>")
    lineas.append("<fecha>" + fecha + "</fecha>")
    for tipoPago in [1, 2, 3]:
        seccion = nombresSecciones[tipoPago]
        lineas.append("<" + seccion + ">")
        for objeto in grupos[tipoPago]:
            monto = calcularMontoObjeto(objeto, config["montoHora"], config["tiempoGracia"])
            textoMarca = obtenerTextoPorCodigo(catalogos["marcas"], objeto.marca)
            textoColor = obtenerTextoPorCodigo(catalogos["colores"], objeto.color)
            textoTipo  = obtenerTextoPorCodigo(catalogos["tipos"],   objeto.tipo)
            lineas.append("<vehiculo>")
            lineas.append("<id>" + str(objeto.id) + "</id>")
            lineas.append("<placa>" + objeto.placa + "</placa>")
            lineas.append("<marca>" + textoMarca + "</marca>")
            lineas.append("<color>" + textoColor + "</color>")
            lineas.append("<tipo>" + textoTipo + "</tipo>")
            lineas.append("<ubicacion>" + objeto.ubicacion + "</ubicacion>")
            lineas.append("<fechaHoraEntrada>" + objeto.fechaHoraEntrada + "</fechaHoraEntrada>")
            lineas.append("<fechaHoraSalida>" + objeto.fechaHoraSalida + "</fechaHoraSalida>")
            lineas.append("<tipoPago>" + catalogoPagos[tipoPago] + "</tipoPago>")
            lineas.append("<monto>" + str(monto) + "</monto>")
            lineas.append("</vehiculo>")
        lineas.append("</" + seccion + ">")
    lineas.append("</cierrePorTipoPago>")
    with open(rutaXML, "w", encoding="utf-8") as archivo:
        for linea in lineas:
            archivo.write(linea + "\n")
    return rutaXML

def generarCierreDiarioCSV(listaObjetos, config):
    """
    Funcionalidad:
    Exporta el cierre diario a un archivo CSV sin titulos, con las
    columnas: ubicacion, placa, hora de entrada, hora de salida,
    tipo de pago y monto. Solo incluye vehiculos con salida registrada.
    Listo para abrir en Excel.
    Entrada:
    - listaObjetos (list): Lista de objetos Estacionamiento del dia.
    - config (dict): Configuracion con montoHora y tiempoGracia.
    Salida:
    - rutaCSV (str): Ruta del archivo CSV generado.
    """
    fecha = datetime.datetime.now().strftime("%d-%m-%Y")
    nombreArchivo = "cierre_diario_" + fecha + ".csv"
    rutaCSV = carpetaReportes + "/" + nombreArchivo
    with open(rutaCSV, "w", encoding="utf-8", newline="") as archivo:
        archivo.write("sep=;\r\n")
        for objeto in listaObjetos:
            if objeto.fechaHoraSalida == "":
                continue
            monto = calcularMontoObjeto(objeto, config["montoHora"], config["tiempoGracia"])
            textoPago = catalogoPagos[objeto.tipoPago]
            linea = (objeto.ubicacion + ";" +objeto.placa + ";" +objeto.fechaHoraEntrada + ";" +objeto.fechaHoraSalida + ";" +textoPago + ";" + str(monto))
            archivo.write(linea + "\r\n")
    return rutaCSV