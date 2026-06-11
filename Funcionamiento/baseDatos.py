import pickle

archivoBD     = "datos/bdParqueo.pkl"
archivoConfig = "datos/configParqueo.pkl"

def guardarBD(lista):
    """
    Funcionalidad:
    Guarda la lista de objetos Estacionamiento en memoria secundaria.
    Entrada:
    - lista (list): Lista de objetos Estacionamiento.
    Salida:
    - None
    """
    with open(archivoBD, "wb") as f:
        pickle.dump(lista, f)
    return

def cargarBD():
    """
    Funcionalidad:
    Carga la lista de objetos Estacionamiento desde memoria secundaria.
    Entrada:
    - Ninguna.
    Salida:
    - lista (list): Lista de objetos Estacionamiento, o lista vacia si no existe.
    """
    try:
        with open(archivoBD, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []

def guardarConfig(config):
    """
    Funcionalidad:
    Guarda el diccionario de configuracion del parqueo en disco.
    Entrada:
    - config (dict): Diccionario con tamano, tiempo de gracia y monto por hora.
    Salida:
    - None
    """
    with open(archivoConfig, "wb") as f:
        pickle.dump(config, f)
    return

def cargarConfig():
    """
    Funcionalidad:
    Carga el diccionario de configuracion desde disco.
    Entrada:
    - Ninguna.
    Salida:
    - config (dict): Diccionario de configuracion, o None si no existe.
    """
    try:
        with open(archivoConfig, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def existeBD():
    """
    Funcionalidad:
    Verifica si ya existe una base de datos guardada en disco.
    Entrada:
    - Ninguna.
    Salida:
    - resultado (bool): True si existe el archivo, False si no.
    """
    try:
        with open(archivoBD, "rb") as f:
            pass
        return True
    except FileNotFoundError:
        return False

def existeConfig():
    """
    Funcionalidad:
    Verifica si ya existe una configuracion guardada en disco.
    Entrada:
    - Ninguna.
    Salida:
    - resultado (bool): True si existe el archivo, False si no.
    """
    try:
        with open(archivoConfig, "rb") as f:
            pass
        return True
    except FileNotFoundError:
        return False