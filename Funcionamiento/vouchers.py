#Elaborado por: Jimena Acuña Parra y Guideon Montero Vargas
#Fecha de elaboración: 11/06/2026 11:24 am
#Última fecha de modificación: 29/04/2026 7:47 pm
#Versión: 3.14.3

#Librerías
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

#Importación de funciones
from funcionamiento.catalogos import obtenerTextoPorCodigo

#Inicialización de variables
carpetaVouchers = "vouchers"
archivoQRTemp   = carpetaVouchers + "/_temp_qr.png"

#Funciones
def construirNombreArchivoVoucher(objeto):
    """
    Funcionalidad:
    Construye el nombre del archivo del voucher a partir de la placa y la
    fecha/hora de entrada del vehiculo. Se reemplazan los ':' de la hora
    por '-' porque Windows no permite ':' en nombres de archivo.
    Entrada:
    - objeto (Estacionamiento): Objeto con los datos del vehiculo.
    Salida:
    - nombreArchivo (str): Nombre del archivo .pdf del voucher.
    """
    fechaHoraTexto = objeto.fechaHoraEntrada.replace(":", "-")
    nombreArchivo = "voucher_" + objeto.placa + "_" + fechaHoraTexto + ".pdf"
    return nombreArchivo

def generarImagenQR(objeto, catalogos):
    """
    Funcionalidad:
    Genera la imagen del codigo QR con la informacion Placa-Marca-Tipo-
    FechaHoraEntrada y la guarda temporalmente en disco usando open().
    No utiliza el modulo os.
    Entrada:
    - objeto (Estacionamiento): Objeto con los datos del vehiculo.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    Salida:
    - rutaImagenQR (str): Ruta del archivo .png temporal generado.
    """
    textoMarca = obtenerTextoPorCodigo(catalogos["marcas"], objeto.marca)
    textoTipo  = obtenerTextoPorCodigo(catalogos["tipos"],  objeto.tipo)
    contenidoQR = (objeto.placa + "-" + textoMarca + "-" + textoTipo + "-" + objeto.fechaHoraEntrada)
    imagenQR = qrcode.make(contenidoQR)
    imagenQR.save(archivoQRTemp)
    return archivoQRTemp

def eliminarQRTemp():
    """
    Funcionalidad:
    Elimina el contenido del archivo temporal del QR sobreescribiendolo
    con bytes vacios, sin usar el modulo os.
    Entrada:
    - Ninguna.
    Salida:
    - None
    """
    try:
        with open(archivoQRTemp, "wb") as archivo:
            archivo.write(b"")
    except Exception:
        pass
    return

def generarVoucherPDF(objeto, catalogos, montoHora):
    """
    Funcionalidad:
    Genera el voucher en formato PDF de un vehiculo recien estacionado,
    incluyendo su informacion y un codigo QR, y lo guarda en disco.
    No utiliza el modulo os.
    Entrada:
    - objeto (Estacionamiento): Objeto con los datos del vehiculo ya estacionado.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    - montoHora (int): Monto cobrado por hora en el parqueo.
    Salida:
    - rutaVoucher (str): Ruta del archivo .pdf generado.
    """
    textoMarca = obtenerTextoPorCodigo(catalogos["marcas"], objeto.marca)
    textoColor = obtenerTextoPorCodigo(catalogos["colores"], objeto.color)
    textoTipo  = obtenerTextoPorCodigo(catalogos["tipos"],  objeto.tipo)
    nombreArchivo = construirNombreArchivoVoucher(objeto)
    rutaVoucher   = carpetaVouchers + "/" + nombreArchivo
    rutaImagenQR  = generarImagenQR(objeto, catalogos)
    pdf = canvas.Canvas(rutaVoucher, pagesize=letter)
    anchoPagina, altoPagina = letter
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, altoPagina - 60, "Voucher de Estacionamiento")
    pdf.setFont("Helvetica", 11)
    lineas = [
        "Placa: " + objeto.placa,
        "Marca: " + textoMarca,
        "Color: " + textoColor,
        "Tipo: " + textoTipo,
        "Ubicacion: " + objeto.ubicacion,
        "Fecha y hora de entrada: " + objeto.fechaHoraEntrada,
        "Monto por hora: " + "{:,}".format(montoHora) + " colones",
    ]
    posicionY = altoPagina - 100
    for linea in lineas:
        pdf.drawString(50, posicionY, linea)
        posicionY = posicionY - 20
    pdf.drawImage(rutaImagenQR, 50, posicionY - 160, width=150, height=150)
    pdf.save()
    eliminarQRTemp()
    return rutaVoucher


def generarVouchersListaObjetos(listaObjetos, catalogos, montoHora):
    """
    Funcionalidad:
    Genera los vouchers PDF de todos los objetos de la lista. Se usa
    para el llenado masivo (opcion 1 del menu).
    Entrada:
    - listaObjetos (list): Lista de objetos Estacionamiento.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    - montoHora (int): Monto cobrado por hora en el parqueo.
    Salida:
    - errores (int): Cantidad de vouchers que no pudieron generarse.
    """
    errores = 0
    for objeto in listaObjetos:
        try:
            generarVoucherPDF(objeto, catalogos, montoHora)
        except Exception:
            errores = errores + 1
    return errores

def generarFacturaPDF(objeto, catalogos, monto):
    """
    Funcionalidad:
    Genera la factura en formato PDF de un vehiculo que acaba de pagar,
    incluyendo informacion completa de la estadia, monto cobrado y un
    codigo QR. No utiliza el modulo os.
    Entrada:
    - objeto (Estacionamiento): Objeto con los datos completos del vehiculo.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    - monto (int): Monto total cobrado en colones.
    Salida:
    - rutaFactura (str): Ruta del archivo .pdf generado.
    """
    textoMarca = obtenerTextoPorCodigo(catalogos["marcas"], objeto.marca)
    textoColor = obtenerTextoPorCodigo(catalogos["colores"], objeto.color)
    textoTipo  = obtenerTextoPorCodigo(catalogos["tipos"],  objeto.tipo)
    catalogoPagos = {1: "Efectivo", 2: "SINPE", 3: "Tarjeta"}
    textoPago = catalogoPagos[objeto.tipoPago]
    fechaHora     = objeto.fechaHoraEntrada.replace(":", "-").replace(" ", "_")
    nombreArchivo = "factura_#" + objeto.placa + "_" + fechaHora + ".pdf"
    rutaFactura   = carpetaVouchers + "/" + nombreArchivo
    rutaImagenQR  = generarImagenQR(objeto, catalogos)
    pdf = canvas.Canvas(rutaFactura, pagesize=letter)
    anchoPagina, altoPagina = letter
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, altoPagina - 60, "Factura de Estacionamiento")
    pdf.setFont("Helvetica", 11)
    lineas = [
        "Placa: " + objeto.placa,
        "Marca: " + textoMarca,
        "Color: " + textoColor,
        "Tipo: " + textoTipo,
        "Ubicacion: " + objeto.ubicacion,
        "Fecha y hora de entrada: " + objeto.fechaHoraEntrada,
        "Fecha y hora de salida: " + objeto.fechaHoraSalida,
        "Tipo de pago: " + textoPago,
        "Monto cobrado: " + "{:,}".format(monto) + " colones",
    ]
    posicionY = altoPagina - 100
    for linea in lineas:
        pdf.drawString(50, posicionY, linea)
        posicionY = posicionY - 20
    pdf.drawImage(rutaImagenQR, 50, posicionY - 160, width=150, height=150)
    pdf.save()
    eliminarQRTemp()
    return rutaFactura