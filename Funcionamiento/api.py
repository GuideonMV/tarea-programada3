import urllib.request
import json

urlBaseMockaroo = "https://api.mockaroo.com/api/7bca61f0?key=4a719e30"


def obtenerDatosMockaroo(cantidad):
    """
    Funcionalidad:
    Consulta el API de Mockaroo y obtiene una lista de registros de vehiculos.
    Entrada:
    - cantidad (int): Cantidad de registros a solicitar al API.
    Salida:
    - registros (list): Lista de diccionarios con los datos crudos del API,
      o lista vacia si ocurre un error de conexion.
    """
    url = urlBaseMockaroo + "&count=" + str(cantidad)
    encabezados = {"User-Agent": "Mozilla/5.0"}
    peticion = urllib.request.Request(url, headers=encabezados)
    try:
        respuesta = urllib.request.urlopen(peticion)
        datos = respuesta.read()
        registros = json.loads(datos)
        return registros
    except Exception:
        return []

def filtrarRegistros(registros):
    """
    Funcionalidad:
    Filtra los registros crudos del API y construye el diccionario
    de placas con la informacion relevante para el sistema.
    Entrada:
    - registros (list): Lista de diccionarios con los datos crudos del API.
    Salida:
    - diccionarioPlacas (dict): Diccionario donde cada llave es una placa
      y el valor es un diccionario con marca, color, tipo, ubicacion,
      fechaHoraEntrada, fechaHoraSalida, monto y tipoPago.
    """
    diccionarioPlacas = {}
    for registro in registros:
        placa = registro["placa"]
        datosVehiculo = {
            "marca": registro["marca"],
            "color": registro["color"],
            "tipo": registro["tipo"],
            "ubicacion": "",
            "fechaHoraEntrada": "",
            "fechaHoraSalida": "",
            "monto": 0,
            "tipoPago": 0
        }
        diccionarioPlacas[placa] = datosVehiculo
    return diccionarioPlacas

def obtenerListasUnicas(registros):
    """
    Funcionalidad:
    Extrae las marcas, colores y tipos unicos que aparecen en los
    registros del API, para usarlos como opciones iniciales en la
    interfaz grafica.
    Entrada:
    - registros (list): Lista de diccionarios con los datos crudos del API.
    Salida:
    - listasUnicas (dict): Diccionario con las llaves marcas, colores y
      tipos, cada una con una lista de valores unicos sin repetir.
    """
    marcas = []
    colores = []
    tipos = []
    for registro in registros:
        if registro["marca"] not in marcas:
            marcas.append(registro["marca"])
        if registro["color"] not in colores:
            colores.append(registro["color"])
        if registro["tipo"] not in tipos:
            tipos.append(registro["tipo"])
    listasUnicas = {
        "marcas": marcas,
        "colores": colores,
        "tipos": tipos
    }
    return listasUnicas