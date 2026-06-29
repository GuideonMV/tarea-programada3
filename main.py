import tkinter as tk
import re
import datetime
from tkinter import ttk
from tkinter import messagebox

from funcionamiento.baseDatos import guardarConfig, cargarConfig, existeConfig, guardarBD, guardarCatalogos, cargarCatalogos, cargarBD
from funcionamiento.api import obtenerDatosMockaroo, filtrarRegistros, obtenerListasUnicas
from funcionamiento.calculosParqueo import calcularDistribucionEspacios, obtenerUbicacionesOcupadas, buscarObjetoPorUbicacion, obtenerUbicacionesLibres, calcularMonto
from funcionamiento.catalogos import construirCatalogos, obtenerCodigoPorTexto, obtenerTextoPorCodigo
from funcionamiento.llenadoMasivo import generarUbicacionesGenerales, construirListaObjetos, generarTodasLasUbicaciones
from funcionamiento.vouchers import generarVoucherPDF
from modelos.estacionamiento import Estacionamiento
from funcionamiento.vouchers import generarVouchersListaObjetos

#Botón 1
def obtenerVehiculos():
    """
    Funcionalidad:
    Llena masivamente el parqueo consultando el API de Mockaroo,
    actualiza la base de datos en disco y genera los vouchers PDF
    con codigo QR en memoria para cada vehiculo estacionado.
    Solo se ejecuta si no hay vehiculos actualmente estacionados.
    Entrada:
    - Ninguna
    Salida:
    - None
    """
    config = cargarConfig()
    if config is None:
        messagebox.showerror("Error", "Debe configurar el parqueo primero")
        return
    listaExistente = cargarBD()
    vehiculosActivos = 0
    for objeto in listaExistente:
        if objeto.fechaHoraSalida == "":
            vehiculosActivos = vehiculosActivos + 1
    if vehiculosActivos > 0:
        messagebox.showwarning("Parqueo ocupado", "El parqueo tiene " + str(vehiculosActivos) + " vehiculos actualmente estacionados.\n Para volver a llenarlo debe hacer el cierre diario primero.")
        return
    respuesta = messagebox.askyesno("Obtener vehiculos", "Esto llenara el parqueo masivamente y generara los vouchers.\n¿Desea continuar?")
    if not respuesta:
        return
    distribucion = calcularDistribucionEspacios(config["tamano"], config["tieneElectrico"])
    registrosExploracion = obtenerDatosMockaroo(100)
    if not registrosExploracion:
        messagebox.showerror("Error de conexion", "No se pudo conectar al API de Mockaroo.\nVerifique su conexion a internet e intente de nuevo.")
        return
    registrosLlenado = obtenerDatosMockaroo(distribucion["topeMasivo"])
    if not registrosLlenado:
        messagebox.showerror("Error de conexion", "No se pudo obtener los vehiculos del API.\nVerifique su conexion a internet e intente de nuevo.")
        return
    listasUnicas = obtenerListasUnicas(registrosExploracion)
    catalogos = construirCatalogos(listasUnicas)
    guardarCatalogos(catalogos)
    diccionarioPlacas = filtrarRegistros(registrosLlenado)
    ubicaciones = generarUbicacionesGenerales(distribucion["porAsignar"])
    listaObjetos = construirListaObjetos(diccionarioPlacas, ubicaciones, catalogos)
    guardarBD(listaObjetos)
    if not listaObjetos:
        messagebox.showerror("Error", "El API no devolvio vehiculos validos.")
        return
    errores = generarVouchersListaObjetos(listaObjetos, catalogos, config["montoHora"])
    if errores == 0:
        messagebox.showinfo("Completado","Se estacionaron " + str(len(listaObjetos)) + " vehiculos.\nVouchers guardados en la carpeta vouchers/")
    else:
        messagebox.showwarning("Completado con advertencias", "Vehiculos estacionados: " + str(len(listaObjetos)) + "\n" +"Vouchers con error: " + str(errores))
    return

#Botón 2
def manejarClicEspacio(ventanaPrincipal, ventanaEstacionamiento, ubicacion, listaObjetos, catalogos):
    """
    Funcionalidad: Maneja el clic sobre un espacio del parqueo. Si esta ocupado
    muestra info del vehiculo, si esta libre abre la ventana para estacionar.
    Entrada:
    - ventanaPrincipal (Tk): Ventana principal del sistema.
    - ventanaEstacionamiento (Toplevel): Ventana de "Ver estacionamiento" abierta.
    - ubicacion (str): Identificador del espacio clickeado.
    - listaObjetos (list): Lista de objetos Estacionamiento.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    Salida:
    - None
    """
    objeto = buscarObjetoPorUbicacion(listaObjetos, ubicacion)
    if objeto is None:
        ventanaEstacionarVehiculo(ventanaPrincipal, ventanaEstacionamiento, ubicacion, listaObjetos, catalogos)
    else:
        ventanaObservarEspacio(ventanaPrincipal, ventanaEstacionamiento, objeto, listaObjetos, catalogos)
    return

def obtenerSiguienteId(listaObjetos):
    """
    Funcionalidad: Calcula el siguiente id disponible para un nuevo objeto
    Estacionamiento, en funcion del id maximo ya usado en la lista.
    Entrada:
    - listaObjetos (list): Lista de objetos Estacionamiento.
    Salida:
    - siguienteId (int): Id consecutivo a utilizar para el proximo registro.
    """
    idMaximo = 0
    for objeto in listaObjetos:
        if objeto.id > idMaximo:
            idMaximo = objeto.id
    return idMaximo + 1

def validarPlaca(placa, listaObjetos):
    """
    Funcionalidad: Valida que la placa no este vacia, tenga un formato
    razonable (letras y numeros, con o sin guion) y no corresponda a un
    vehiculo que ya se encuentra actualmente estacionado en el parqueo.
    Entrada:
    - placa (str): Texto de la placa ingresada por el usuario.
    - listaObjetos (list): Lista de objetos Estacionamiento actuales.
    Salida:
    - esValida (bool): True si la placa cumple el formato y no esta duplicada.
    """
    placa = placa.strip().upper()
    if placa == "":
        return False
    patron = r"^([A-Z]{3}\d{3,4}|\d{4,6})$"
    if not re.match(patron, placa):
        return False
    for objeto in listaObjetos:
        if objeto.placa.strip().upper() == placa and objeto.fechaHoraSalida == "":
            return None
    return True

def confirmarEstacionar(ventana, ventanaPrincipal, ventanaEstacionamiento, listaObjetos, catalogos, comboUbicacion, entradaPlaca, comboMarca, comboTipo, comboColor):
    """
    Funcionalidad: Valida los datos ingresados, confirma la accion con el usuario
    (pues implica un cobro), registra el nuevo vehiculo en la lista de objetos,
    actualiza la BD en memoria secundaria y genera el voucher en PDF con QR.
    Entrada:
    - ventana (Toplevel): Ventana de "Estacionar un vehiculo" a cerrar al finalizar.
    - ventanaPrincipal (Tk): Ventana principal del sistema.
    - ventanaEstacionamiento (Toplevel): Ventana de "Ver estacionamiento" a refrescar.
    - listaObjetos (list): Lista de objetos Estacionamiento.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    - comboUbicacion (Combobox): Combo con la ubicacion seleccionada.
    - entradaPlaca (Entry): Campo de texto con la placa.
    - comboMarca (Combobox): Combo con la marca seleccionada.
    - comboTipo (Combobox): Combo con el tipo de vehiculo seleccionado.
    - comboColor (Combobox): Combo (editable) con el color seleccionado.
    Salida:
    - None
    """
    ubicacion = comboUbicacion.get().strip()
    placa = entradaPlaca.get().strip().upper()
    textoMarca = comboMarca.get().strip()
    textoTipo = comboTipo.get().strip()
    textoColor = comboColor.get().strip()
    if ubicacion == "" or placa == "" or textoMarca == "" or textoTipo == "" or textoColor == "":
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return
    if validarPlaca(placa, listaObjetos)==None:
        messagebox.showerror("Error", "La placa ingresada ya se encuentra registrada en el estacionamiento")
        return
    if not validarPlaca(placa, listaObjetos):
        messagebox.showerror("Error", "La placa no es valida")
        return
    config = cargarConfig()
    respuesta = messagebox.askyesno("Confirmar estacionamiento", "Se reservara el espacio " + ubicacion + " para la placa " + placa + ".\nCosto por hora: " + str(config["montoHora"]) + " colones.\n¿Desea continuar?")
    if not respuesta:
        return
    codigoMarca = obtenerCodigoPorTexto(catalogos["marcas"], textoMarca)
    codigoColor = obtenerCodigoPorTexto(catalogos["colores"], textoColor)
    codigoTipo = obtenerCodigoPorTexto(catalogos["tipos"], textoTipo)
    horaEntrada = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    siguienteId = obtenerSiguienteId(listaObjetos)
    nuevoObjeto = Estacionamiento(siguienteId, placa, codigoMarca, codigoColor, codigoTipo, ubicacion, horaEntrada, "", 0,0)
    listaObjetos.append(nuevoObjeto)
    guardarBD(listaObjetos)
    guardarCatalogos(catalogos)
    rutaVoucher = generarVoucherPDF(nuevoObjeto, catalogos, config["montoHora"])
    messagebox.showinfo("Vehiculo estacionado", "Vehiculo estacionado en " + ubicacion + ".\nVoucher generado en: " + rutaVoucher)
    ventana.destroy()
    ventanaEstacionamiento.destroy()
    verEstacionamiento(ventanaPrincipal)
    return

def ventanaEstacionarVehiculo(ventanaPrincipal, ventanaEstacionamiento, ubicacion, listaObjetos, catalogos):
    """
    Funcionalidad:
    Abre la ventana para registrar y estacionar un vehiculo en un espacio
    libre del parqueo. El usuario escribe la placa y selecciona ubicacion,
    marca, tipo y color desde listas; la hora de entrada se llena automaticamente.
    Entrada:
    - ventanaPrincipal (Tk): Ventana principal del sistema.
    - ventanaEstacionamiento (Toplevel): Ventana de ver estacionamiento abierta.
    - ubicacion (str): Ubicacion del espacio libre clickeado (preseleccionada).
    - listaObjetos (list): Lista de objetos Estacionamiento.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    Salida:
    - None
    """
    config = cargarConfig()
    distribucion = calcularDistribucionEspacios(config["tamano"], config["tieneElectrico"])
    todasUbicaciones = generarTodasLasUbicaciones(distribucion)
    ubicacionesOcupadas = obtenerUbicacionesOcupadas(listaObjetos)
    ubicacionesLibres = obtenerUbicacionesLibres(todasUbicaciones, ubicacionesOcupadas)
    ventana = tk.Toplevel(ventanaPrincipal)
    ventana.title("Estacionar un vehiculo")
    ventana.geometry("380x320")
    ventana.resizable(False, False)
    ventana.columnconfigure(0, weight=1)
    ventana.columnconfigure(1, weight=1)
    tk.Label(ventana, text="Estacionar un vehiculo", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
    tk.Label(ventana, text="Ubicacion:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    comboUbicacion = ttk.Combobox(ventana, values=ubicacionesLibres, state="readonly")
    if ubicacion in ubicacionesLibres:
        comboUbicacion.set(ubicacion)
    elif len(ubicacionesLibres) > 0:
        comboUbicacion.set(ubicacionesLibres[0])
    comboUbicacion.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Placa:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entradaPlaca = tk.Entry(ventana)
    entradaPlaca.grid(row=2, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Marca:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    comboMarca = ttk.Combobox(ventana, values=list(catalogos["marcas"].values()), state="readonly")
    comboMarca.grid(row=3, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Tipo:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    comboTipo = ttk.Combobox(ventana, values=list(catalogos["tipos"].values()), state="readonly")
    comboTipo.grid(row=4, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Color:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
    coloresNormalizados = [c.capitalize() for c in catalogos["colores"].values()]
    comboColor = ttk.Combobox(ventana, values=coloresNormalizados, state="normal")
    comboColor.grid(row=5, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Hora de entrada:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
    horaActual = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    entradaHora = tk.Entry(ventana)
    entradaHora.insert(0, horaActual)
    entradaHora.config(state="readonly")
    entradaHora.grid(row=6, column=1, sticky="w", padx=5, pady=5)
    tk.Button(ventana, text="Estacionar", width=12, command=lambda: confirmarEstacionar(ventana, ventanaPrincipal, ventanaEstacionamiento, listaObjetos, catalogos, comboUbicacion, entradaPlaca, comboMarca, comboTipo, comboColor)).grid(row=7, column=0, pady=20)
    tk.Button(ventana, text="Regresar", width=12, command=ventana.destroy).grid(row=7, column=1, pady=20)
    ventana.grab_set()
    return

def construirBloques(todasUbicaciones):
    """
    Funcionalidad: Divide las ubicaciones de cada seccion en bloques de 16 espacios
    (4x4), conservando el titulo de la seccion en cada bloque.
    Entrada:
    - todasUbicaciones (dict): Diccionario con las llaves generales,
      especiales y electrico, cada una con una lista de ubicaciones.
    Salida:
    - bloques (list): Lista de diccionarios con titulo y ubicaciones.
    """
    espaciosPorBloque = 16
    secciones = [
        ("Generales", todasUbicaciones["generales"]),
        ("Especiales", todasUbicaciones["especiales"]),
        ("Vehiculo electrico", todasUbicaciones["electrico"])
    ]
    bloques = []
    for titulo, ubicaciones in secciones:
        inicio = 0
        while inicio < len(ubicaciones):
            fragmento = ubicaciones[inicio:inicio + espaciosPorBloque]
            bloques.append({"titulo": titulo, "ubicaciones": fragmento})
            inicio = inicio + espaciosPorBloque
    return bloques

def dibujarBloque(ventana, bloque, ubicacionesOcupadas, ventanaPrincipal, listaObjetos, catalogos):
    """
    Funcionalidad: Dibuja el titulo y la cuadricula 4x4 de un bloque del parqueo,
    coloreando cada espacio segun su estado de ocupacion.
    Entrada:
    - ventana (Toplevel): Ventana donde se dibuja el bloque.
    - bloque (dict): Diccionario con titulo y ubicaciones.
    - ubicacionesOcupadas (set): Conjunto de ubicaciones ocupadas.
    - ventanaPrincipal (Tk): Ventana principal del sistema.
    - listaObjetos (list): Lista de objetos Estacionamiento.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    Salida:
    - None
    """
    columnas = 4
    tk.Label(ventana, text=bloque["titulo"], font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=columnas, pady=(10, 5))
    fila = 1
    columna = 0
    for ubicacion in bloque["ubicaciones"]:
        if ubicacion in ubicacionesOcupadas:
            color = "#FFB3B3"
        else:
            color = "#B3FFB3"
        boton = tk.Button( ventana, text=ubicacion, width=8, height=3, bg=color, command=lambda u=ubicacion: manejarClicEspacio(ventanaPrincipal, ventana, u, listaObjetos, catalogos))
        boton.grid(row=fila, column=columna, padx=2, pady=2)
        columna = columna + 1
        if columna >= columnas:
            columna = 0
            fila = fila + 1
    return

def cambiarBloque(ventana, bloques, indiceActual, ubicacionesOcupadas, ventanaPrincipal, listaObjetos, catalogos, direccion):
    """
    Funcionalidad: Cambia al bloque anterior o siguiente, limpiando la ventana y
    redibujando el contenido correspondiente.
    Entrada:
    - ventana (Toplevel): Ventana del estacionamiento.
    - bloques (list): Lista de bloques del parqueo.
    - indiceActual (int): Indice del bloque actualmente mostrado.
    - ubicacionesOcupadas (set): Conjunto de ubicaciones ocupadas.
    - ventanaPrincipal (Tk): Ventana principal del sistema.
    - listaObjetos (list): Lista de objetos Estacionamiento.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    - direccion (int): -1 para retroceder, 1 para avanzar.
    Salida:
    - None
    """
    nuevoIndice = indiceActual + direccion
    if nuevoIndice < 0:
        nuevoIndice = 0
    if nuevoIndice >= len(bloques):
        nuevoIndice = len(bloques) - 1
    for widget in ventana.winfo_children():
        widget.destroy()
    mostrarBloque(ventana, bloques, nuevoIndice, ubicacionesOcupadas, ventanaPrincipal, listaObjetos, catalogos)
    return

def mostrarBloque(ventana, bloques, indiceActual, ubicacionesOcupadas, ventanaPrincipal, listaObjetos, catalogos):
    """
    Funcionalidad:Muestra el bloque actual con su cuadricula, barra de servicios
    y controles de navegacion.
    Entrada:
    - ventana (Toplevel): Ventana del estacionamiento.
    - bloques (list): Lista de bloques del parqueo.
    - indiceActual (int): Indice del bloque a mostrar.
    - ubicacionesOcupadas (set): Conjunto de ubicaciones ocupadas.
    - ventanaPrincipal (Tk): Ventana principal del sistema.
    - listaObjetos (list): Lista de objetos Estacionamiento.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    Salida:
    - None
    """
    dibujarBloque(ventana, bloques[indiceActual], ubicacionesOcupadas, ventanaPrincipal, listaObjetos, catalogos)
    filaServicios = 5
    filaControles = 6
    columnas = 4
    tk.Label(ventana, text="Casetilla de cobro", font=("Arial", 11, "bold"), bg="#FFE0B3", highlightbackground="#CC9966", highlightthickness=3, width=20, height=3).grid(row=filaServicios, column=0, columnspan=2, padx=15, pady=(25, 10))
    tk.Label(ventana, text="Baño sanitario", font=("Arial", 11, "bold"), bg="#B3E0FF", highlightbackground="#6699CC", highlightthickness=3, width=20, height=3).grid(row=filaServicios, column=2, columnspan=2, padx=15, pady=(25, 10))
    tk.Button(ventana, text="Anterior", command=lambda: cambiarBloque(ventana, bloques, indiceActual, ubicacionesOcupadas, ventanaPrincipal, listaObjetos, catalogos, -1)).grid(row=filaControles, column=0, pady=15)
    textoBloque = "Bloque " + str(indiceActual + 1) + " de " + str(len(bloques))
    tk.Label(ventana, text=textoBloque).grid(row=filaControles, column=1, columnspan=2)
    tk.Button(ventana, text="Siguiente", command=lambda: cambiarBloque(ventana, bloques, indiceActual, ubicacionesOcupadas, ventanaPrincipal, listaObjetos, catalogos, 1)).grid(row=filaControles, column=3, pady=15)
    tk.Button(ventana, text="Regresar", command=ventana.destroy).grid(row=filaControles + 1, column=0, columnspan=columnas, pady=10)
    return

def verEstacionamiento(ventanaPrincipal):
    """
    Funcionalidad: Abre la ventana que muestra el mapa visual del parqueo en bloques
    de 16 espacios con navegacion anterior/siguiente.
    Entrada:
    - ventanaPrincipal (Tk): Ventana principal del sistema.
    Salida:
    - None
    """
    config = cargarConfig()
    listaObjetos = cargarBD()
    catalogos = cargarCatalogos()
    distribucion = calcularDistribucionEspacios(config["tamano"], config["tieneElectrico"])
    todasUbicaciones = generarTodasLasUbicaciones(distribucion)
    ubicacionesOcupadas = obtenerUbicacionesOcupadas(listaObjetos)
    bloques = construirBloques(todasUbicaciones)
    ventana = tk.Toplevel(ventanaPrincipal)
    ventana.title("Ver estacionamiento")
    ventana.resizable(False, False)
    mostrarBloque(ventana, bloques, 0, ubicacionesOcupadas, ventanaPrincipal, listaObjetos, catalogos)
    return

def ventanaConfirmarPago(ventanaPadre, textoPago, monto):
    """
    Funcionalidad:
    Muestra una ventana de confirmacion de pago con botones en espanol
    y retorna True si el usuario confirmo, False si cancelo.
    Entrada:
    - ventanaPadre (Toplevel): Ventana padre sobre la que se abre.
    - textoPago (str): Tipo de pago seleccionado como texto.
    - monto (int): Monto calculado a cobrar en colones.
    Salida:
    - confirmado (bool): True si el usuario presiono Confirmar, False si cancelo.
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Confirmar pago")
    ventana.geometry("300x150")
    ventana.resizable(False, False)
    ventana.grab_set()
    resultado = tk.BooleanVar(value=False)
    tk.Label(ventana, text="Tipo de pago: " + textoPago + "\nMonto a cobrar: " + "{:,}".format(monto) + " colones.\n¿Confirmar pago?", font=("Arial", 11),justify="center").pack(pady=20)
    marcosBotones = tk.Frame(ventana)
    marcosBotones.pack()
    tk.Button(marcosBotones, text="Confirmar", width=12, command=lambda: [resultado.set(True), ventana.destroy()]).pack(side="left", padx=10)
    tk.Button(marcosBotones, text="Cancelar", width=12, command=ventana.destroy).pack(side="left", padx=10)
    ventana.wait_window()
    return resultado.get()

def confirmarPago(ventana, ventanaPrincipal, ventanaEstacionamiento, objeto, listaObjetos, catalogos, comboPago):
    """
    Funcionalidad:
    Procesa el pago de un vehiculo: valida el tipo de pago, calcula el monto,
    abre una ventana de confirmacion en espanol, registra hora de salida,
    tipo de pago y monto en el objeto, guarda la BD, genera la factura PDF
    y refresca el estacionamiento automaticamente.
    Entrada:
    - ventana (Toplevel): Ventana de observar espacio a cerrar al finalizar.
    - ventanaPrincipal (Tk): Ventana principal del sistema.
    - ventanaEstacionamiento (Toplevel): Ventana de ver estacionamiento a refrescar.
    - objeto (Estacionamiento): Objeto del vehiculo a pagar.
    - listaObjetos (list): Lista de objetos Estacionamiento.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    - comboPago (Combobox): Combo con el tipo de pago seleccionado.
    Salida:
    - None
    """
    textoPago = comboPago.get().strip()
    if textoPago == "":
        messagebox.showerror("Error", "Debe seleccionar un tipo de pago")
        return
    config = cargarConfig()
    catalogoPagos = {"Efectivo": 1, "SINPE": 2, "Tarjeta": 3}
    tipoPago = catalogoPagos[textoPago]
    monto = calcularMonto(objeto.fechaHoraEntrada, config["montoHora"], config["tiempoGracia"])
    confirmado = ventanaConfirmarPago(ventana, textoPago, monto)
    if not confirmado:
        return
    horaSalida = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    objeto.fechaHoraSalida = horaSalida
    objeto.tipoPago = tipoPago
    objeto.monto = monto
    guardarBD(listaObjetos)
    from funcionamiento.vouchers import generarFacturaPDF
    rutaFactura = generarFacturaPDF(objeto, catalogos, monto)
    messagebox.showinfo("Pago registrado", "Pago exitoso. El espacio " + objeto.ubicacion + " ha sido desocupado.\nFactura generada en: " + rutaFactura)
    ventana.destroy()
    ventanaEstacionamiento.destroy()
    verEstacionamiento(ventanaPrincipal)
    return

def ventanaObservarEspacio(ventanaPrincipal, ventanaEstacionamiento, objeto, listaObjetos, catalogos):
    """
    Funcionalidad:
    Abre la ventana para observar la informacion de un espacio ocupado.
    Muestra los datos del vehiculo en modo solo lectura y permite pagar
    o regresar.
    Entrada:
    - ventanaPrincipal (Tk): Ventana principal del sistema.
    - ventanaEstacionamiento (Toplevel): Ventana de ver estacionamiento abierta.
    - objeto (Estacionamiento): Objeto del vehiculo estacionado.
    - listaObjetos (list): Lista de objetos Estacionamiento.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    Salida:
    - None
    """
    config = cargarConfig()
    textoMarca = obtenerTextoPorCodigo(catalogos["marcas"], objeto.marca)
    textoColor = obtenerTextoPorCodigo(catalogos["colores"], objeto.color).capitalize()
    ventana = tk.Toplevel(ventanaPrincipal)
    ventana.title("Observar espacio")
    ventana.geometry("380x320")
    ventana.resizable(False, False)
    ventana.columnconfigure(0, weight=1)
    ventana.columnconfigure(1, weight=1)
    tk.Label(ventana, text="Informacion del espacio", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
    tk.Label(ventana, text="Campo:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    comboUbicacion = ttk.Combobox(ventana, values=[objeto.ubicacion], state="readonly")
    comboUbicacion.set(objeto.ubicacion)
    comboUbicacion.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Placa:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entradaPlaca = tk.Entry(ventana)
    entradaPlaca.insert(0, objeto.placa)
    entradaPlaca.config(state="readonly")
    entradaPlaca.grid(row=2, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Marca:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    comboMarca = ttk.Combobox(ventana, values=[textoMarca], state="readonly")
    comboMarca.set(textoMarca)
    comboMarca.grid(row=3, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Color:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    comboColor = ttk.Combobox(ventana, values=[textoColor], state="readonly")
    comboColor.set(textoColor)
    comboColor.grid(row=4, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Hora de entrada:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
    entradaHora = tk.Entry(ventana)
    entradaHora.insert(0, objeto.fechaHoraEntrada)
    entradaHora.config(state="readonly")
    entradaHora.grid(row=5, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Tipo de pago:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
    comboPago = ttk.Combobox(ventana, values=["Efectivo", "SINPE", "Tarjeta"], state="readonly")
    comboPago.grid(row=6, column=1, sticky="w", padx=5, pady=5)
    tk.Button(ventana, text="Pagar", width=12, command=lambda: confirmarPago(ventana, ventanaPrincipal, ventanaEstacionamiento, objeto, listaObjetos, catalogos, comboPago)).grid(row=7, column=0, pady=20)
    tk.Button(ventana, text="Regresar", width=12, command=ventana.destroy).grid(row=7, column=1, pady=20)
    ventana.grab_set()
    return

#Botón 3
def reportes():
    messagebox.showinfo("Info", "Proximamente: Reportes")

#Botón 4
def validarCamposConfiguracion(tamano, gracia, monto):
    """
    Funcionalidad: Valida que los campos de configuracion sean numeros enteros positivos.
    Entrada:
    - tamano (str): Texto ingresado para el tamano del estacionamiento.
    - gracia (str): Texto ingresado para el tiempo de gracia en minutos.
    - monto (str): Texto ingresado para el monto por hora.
    Salida:
    - esValido (bool): True si los tres campos son enteros positivos.
    """
    if not tamano.isdigit():
        return False
    if not gracia.isdigit():
        return False
    if not monto.isdigit():
        return False
    if int(tamano) <= 0:
        return False
    return True

def validarReduccionTamano(listaObjetos, nuevaDistribucion):
    """
    Funcionalidad: Verifica que todos los vehiculos actualmente estacionados
    sigan teniendo un espacio valido dentro de la nueva distribucion antes
    de permitir el cambio de tamano (o de configuracion electrica) del
    estacionamiento.
    Entrada:
    - listaObjetos (list): Lista de objetos Estacionamiento actualmente guardados.
    - nuevaDistribucion (dict): Distribucion calculada para el nuevo tamano.
    Salida:
    - esValido (bool): True si todas las ubicaciones ocupadas siguen existiendo
      en la nueva distribucion, False en caso contrario.
    """
    nuevasUbicaciones = generarTodasLasUbicaciones(nuevaDistribucion)
    todasNuevas = set(nuevasUbicaciones["generales"]) | set(nuevasUbicaciones["especiales"]) | set(nuevasUbicaciones["electrico"])
    ubicacionesOcupadas = obtenerUbicacionesOcupadas(listaObjetos)
    for ubicacion in ubicacionesOcupadas:
        if ubicacion not in todasNuevas:
            return False
    return True

def guardarConfiguracion(ventana, entradaTamano, entradaGracia, entradaMonto, variableElectrico, esConfiguracionNueva):
    """
    Funcionalidad: Valida y guarda los datos de configuracion. Si es la primera vez,
    ejecuta el llenado masivo. Si ya existia, permite modificar el tamano,
    tiempo de gracia, monto y espacio electrico, validando que un cambio de
    tamano o de espacio electrico no deje sin ubicacion valida a vehiculos
    ya estacionados, y pide confirmacion antes de aplicar los cambios.
    Entrada:
    - ventana (Toplevel): Ventana de configuracion a cerrar al finalizar.
    - entradaTamano (Entry): Campo del tamano del estacionamiento.
    - entradaGracia (Entry): Campo del tiempo de gracia.
    - entradaMonto (Entry): Campo del monto por hora.
    - variableElectrico (BooleanVar): Variable del checkbox electrico.
    - esConfiguracionNueva (bool): True si no existia configuracion previa.
    Salida:
    - None
    """
    tamanoTexto = entradaTamano.get()
    graciaTexto = entradaGracia.get()
    montoTexto = entradaMonto.get()
    if not validarCamposConfiguracion(tamanoTexto, graciaTexto, montoTexto):
        messagebox.showerror("Error", "Los campos deben ser numeros enteros validos")
        return
    nuevoTamano = int(tamanoTexto)
    nuevoTieneElectrico = variableElectrico.get()
    if not esConfiguracionNueva:
        configActual = cargarConfig()
        listaObjetos = cargarBD()
        cambioRelevante = (nuevoTamano != configActual["tamano"]) or (nuevoTieneElectrico != configActual["tieneElectrico"])
        if cambioRelevante and listaObjetos:
            nuevaDistribucion = calcularDistribucionEspacios(nuevoTamano, nuevoTieneElectrico)
            if not validarReduccionTamano(listaObjetos, nuevaDistribucion):
                messagebox.showerror(
                    "Cambio no permitido", "No se puede aplicar este cambio porque hay vehiculos estacionados\n" "en espacios que dejarian de existir con la nueva configuracion.\n" "Libere esos espacios o elija un tamano mayor.")
                return
        respuesta = messagebox.askyesno("Confirmar", "Desea actualizar la configuracion del parqueo")
        if not respuesta:
            return
    config = {
        "tamano": nuevoTamano,
        "tiempoGracia": int(graciaTexto),
        "montoHora": int(montoTexto),
        "tieneElectrico": nuevoTieneElectrico
    }
    guardarConfig(config)
    if esConfiguracionNueva:
        messagebox.showinfo("Configuracion", "Configuracion guardada correctamente.\nUtilice 'Obtener vehiculos' para llenar el parqueo.")
    else:
        messagebox.showinfo("Configuracion", "Configuracion actualizada correctamente")
    ventana.destroy()
    return

def configuracion(ventanaPrincipal):
    """
    Funcionalidad:Abre la ventana de configuracion del parqueo.
    Entrada:
    - ventanaPrincipal (Tk): Ventana principal del sistema.
    Salida:
    - None
    """
    esConfiguracionNueva = not existeConfig()
    configActual = cargarConfig()
    ventana = tk.Toplevel(ventanaPrincipal)
    ventana.title("Configuracion")
    ventana.geometry("350x250")
    ventana.resizable(False, False)
    tk.Label(ventana, text="Configuracion del parqueo", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
    tk.Label(ventana, text="Tamano del estacionamiento:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    entradaTamano = tk.Entry(ventana)
    entradaTamano.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Tiempo de gracia (minutos):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entradaGracia = tk.Entry(ventana)
    entradaGracia.grid(row=2, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Monto por hora (colones):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    entradaMonto = tk.Entry(ventana)
    entradaMonto.grid(row=3, column=1, sticky="w", padx=5, pady=5)
    tk.Label(ventana, text="Espacio para vehiculos electricos:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    variableElectrico = tk.BooleanVar()
    tk.Checkbutton(ventana, variable=variableElectrico).grid(row=4, column=1, sticky="w", padx=5, pady=5)
    if not esConfiguracionNueva:
        entradaTamano.insert(0, str(configActual["tamano"]))
        entradaGracia.insert(0, str(configActual["tiempoGracia"]))
        entradaMonto.insert(0, str(configActual["montoHora"]))
        variableElectrico.set(configActual["tieneElectrico"])
    tk.Button(ventana,text="Guardar",command=lambda: guardarConfiguracion(ventana, entradaTamano, entradaGracia, entradaMonto, variableElectrico, esConfiguracionNueva)).grid(row=5, column=0, columnspan=2, pady=15)
    ventana.grab_set()
    ventana.wait_window()
    return

#Botón 5
def acercaDe(ventanaPrincipal):
    """
    Funcionalidad:
    Muestra la ventana 'Acerca de' con la informacion del sistema
    y los desarrolladores del proyecto.
    Entrada:ventanaPrincipal (Tk): Ventana principal del sistema.
    Salida:None
    """
    ventana = tk.Toplevel(ventanaPrincipal)
    ventana.title("Acerca de")
    ventana.geometry("400x420")
    ventana.resizable(False, False)
    tk.Label(ventana, text="Sistema de Parqueo", font=("Arial", 18, "bold")).pack(pady=(20, 5))
    tk.Label(ventana, text="Version 1.0 - 2026", font=("Arial", 10), fg="gray").pack()
    tk.Frame(ventana, height=2, bg="#CCCCCC").pack(fill="x", padx=20, pady=15)
    tk.Label(ventana, text="Desarrollado por:", font=("Arial", 11, "bold")).pack()
    tk.Label(ventana, text="Jimena Acuña Parra", font=("Arial", 11)).pack(pady=3)
    tk.Label(ventana, text="Guideon Montero Vargas", font=("Arial", 11)).pack(pady=3)
    tk.Frame(ventana, height=2, bg="#CCCCCC").pack(fill="x", padx=20, pady=15)
    tk.Label(ventana, text="Escuela de Ingeniería en Computación", font=("Arial", 9), fg="gray").pack()
    tk.Label(ventana, text="Taller de Programación - I Semestre 2026", font=("Arial", 9), fg="gray").pack()
    tk.Button(ventana, text="Regresar", command=ventana.destroy, width=15, height=2).pack(pady=20)
    return

# Ventana principal
def verificarConfiguracionInicial(ventana):
    """
    Funcionalidad:Verifica si existe configuracion guardada. Si no existe, obliga
    al usuario a configurar el parqueo antes de continuar.
    Entrada:
    - ventana (Tk): Ventana principal del sistema.
    Salida:
    - configuracionLista (bool): True si se puede continuar, False si no.
    """
    if not existeConfig():
        configuracion(ventana)
        if not existeConfig():
            messagebox.showwarning("Configuracion requerida", "Debe configurar el parqueo para continuar")
            ventana.destroy()
            return False
    return True

def construirInterfaz(ventana):
    """
    Funcionalidad:Construye los botones del menu principal del sistema.
    Entrada:
    - ventana (Tk): Ventana principal donde se colocan los botones.
    Salida:
    - None
    """
    tk.Label(ventana, text="Sistema de Parqueo", font=("Arial", 18, "bold")).pack(pady=20)
    listaBotones = [
        ("Obtener vehiculos", lambda: obtenerVehiculos()),
        ("Ver estacionamiento", lambda: verEstacionamiento(ventana)),
        ("Reportes", lambda: reportes(ventana)),
        ("Configuracion", lambda: configuracion(ventana)),
        ("Acerca de", lambda: acercaDe(ventana)),
    ]
    for texto, comando in listaBotones:
        tk.Button(ventana, text=texto, command=comando, width=28, height=2, font=("Arial", 11)).pack(pady=5)
    return

def main():
    """
    Funcionalidad: Punto de entrada del sistema. Verifica la configuracion inicial
    y construye la ventana principal con el menu de botones. La ventana principal
    permanece oculta mientras se solicita la configuracion inicial, para que el
    usuario no vea una ventana vacia de fondo.
    Entrada:
    - Ninguna.
    Salida:
    - None
    """
    ventana = tk.Tk()
    ventana.title("Sistema de Parqueo")
    ventana.geometry("400x450")
    ventana.resizable(False, False)
    ventana.withdraw()
    configuracionLista = verificarConfiguracionInicial(ventana)
    if configuracionLista:
        construirInterfaz(ventana)
        ventana.deiconify()
        ventana.mainloop()
    return

main()