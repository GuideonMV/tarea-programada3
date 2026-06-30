#Elaborado por: Jimena Acuña Parra y Guideon Montero Vargas
#Fecha de elaboración: 11/06/2026 11:24 am
#Última fecha de modificación: 29/04/2026 7:47 pm
#Versión: 3.14.3

#Clase de objeto
class Estacionamiento:
    """
    Funcionalidad: Representa un vehiculo estacionado en un espacio del parqueo.
    Entrada:
    - id (int): Numero del espacio en el parqueo.
    - placa (str): Placa del vehiculo.
    - marca (int): Codigo numerico de la marca del vehiculo.
    - color (int): Codigo numerico del color del vehiculo.
    - tipo (int): Codigo numerico del tipo de vehiculo.
    - ubicacion (str): Identificador del espacio asignado.
    - fechaHoraEntrada (str): Fecha y hora de entrada al parqueo.
    - fechaHoraSalida (str): Fecha y hora de salida del parqueo.
    - monto (int): Monto cobrado por la estadia.
    - tipoPago (int): 1=Efectivo, 2=SINPE, 3=Tarjeta.
    Salida:
    - Objeto Estacionamiento instanciado.
    """
    #Funcion Init
    
    def __init__(self, id, placa, marca, color, tipo, ubicacion, fechaHoraEntrada, fechaHoraSalida, monto, tipoPago):
        self.id = id                
        self.placa = placa             
        self.marca = marca             
        self.color = color            
        self.tipo = tipo              
        self.ubicacion = ubicacion         
        self.fechaHoraEntrada = fechaHoraEntrada  
        self.fechaHoraSalida = fechaHoraSalida   
        self.monto = monto             
        self.tipoPago = tipoPago