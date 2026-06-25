import tkinter as tk
import tkinter as tk
from tkinter import messagebox

from funcionamiento.baseDatos import guardarConfig, cargarConfig, existeConfig, guardarBD, guardarCatalogos, cargarCatalogos, cargarBD
from funcionamiento.api import obtenerDatosMockaroo, filtrarRegistros, obtenerListasUnicas
from funcionamiento.calculosParqueo import calcularDistribucionEspacios, obtenerUbicacionesOcupadas, buscarObjetoPorUbicacion
from funcionamiento.catalogos import construirCatalogos
from funcionamiento.llenadoMasivo import generarUbicacionesGenerales, construirListaObjetos, generarTodasLasUbicaciones
from funcionamiento.vouchers import generarVouchersListaObjetos

def obtenerVehiculos():
    """
    Funcionalidad:
    Llena masivamente el parqueo consultando el API de Mockaroo,
    actualiza la base de datos en disco y genera los vouchers PDF
    con codigo QR en memoria para cada vehiculo estacionado.
    Solo se ejecuta si el parqueo no ha sido llenado previamente.
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
    if listaExistente:
        messagebox.showwarning(
            "Parqueo ocupado",
            "El parqueo ya tiene " + str(len(listaExistente)) + " vehiculos registrados.\n"
            "Para volver a llenarlo debe reiniciar el sistema."
        )
        return
    respuesta = messagebox.askyesno(
        "Obtener vehiculos",
        "Esto llenara el parqueo masivamente y generara los vouchers.\n¿Desea continuar?"
    )
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
        messagebox.showinfo(
            "Completado",
            "Se estacionaron " + str(len(listaObjetos)) + " vehiculos.\nVouchers guardados en la carpeta vouchers/"
        )
    else:
        messagebox.showwarning(
            "Completado con advertencias",
            "Vehiculos estacionados: " + str(len(listaObjetos)) + "\n" +
            "Vouchers con error: " + str(errores)
        )
    return

def manejarClicEspacio(ventanaPrincipal, ubicacion, listaObjetos, catalogos):
    """
    Funcionalidad: Maneja el clic sobre un espacio del parqueo. Si esta ocupado
    muestra info del vehiculo, si esta libre permite estacionar.
    Entrada:
    - ventanaPrincipal (Tk): Ventana principal del sistema.
    - ubicacion (str): Identificador del espacio clickeado.
    - listaObjetos (list): Lista de objetos Estacionamiento.
    - catalogos (dict): Diccionario de catalogos de marcas, colores y tipos.
    Salida:
    - None
    """
    objeto = buscarObjetoPorUbicacion(listaObjetos, ubicacion)
    if objeto is None:
        messagebox.showinfo("Espacio libre", "Espacio " + ubicacion + " esta libre, proximamente: Estacionar")
    else:
        messagebox.showinfo("Espacio ocupado", "Espacio " + ubicacion + " ocupado por placa " + objeto.placa + ", proximamente: Observar espacio")
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
        boton = tk.Button(
            ventana,
            text=ubicacion,
            width=8,
            height=3,
            bg=color,
            command=lambda u=ubicacion: manejarClicEspacio(ventanaPrincipal, u, listaObjetos, catalogos)
        )
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
    tk.Label(ventana, text="Bano sanitario", font=("Arial", 11, "bold"), bg="#B3E0FF", highlightbackground="#6699CC", highlightthickness=3, width=20, height=3).grid(row=filaServicios, column=2, columnspan=2, padx=15, pady=(25, 10))
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

def reportes():
    messagebox.showinfo("Info", "Proximamente: Reportes")

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

def ejecutarLlenadoInicial(config):
    """
    Funcionalidad: Ejecuta el llenado masivo inicial: calcula distribucion, consulta
    el API, construye catalogos y guarda la lista de objetos en disco.
    Entrada:
    - config (dict): Diccionario con tamano y tieneElectrico.
    Salida:
    - None
    """
    tamano = config["tamano"]
    tieneElectrico = config["tieneElectrico"]
    distribucion = calcularDistribucionEspacios(tamano, tieneElectrico)
    registrosExploracion = obtenerDatosMockaroo(100)
    listasUnicas = obtenerListasUnicas(registrosExploracion)
    catalogos = construirCatalogos(listasUnicas)
    guardarCatalogos(catalogos)
    registrosLlenado = obtenerDatosMockaroo(distribucion["topeMasivo"])
    diccionarioPlacas = filtrarRegistros(registrosLlenado)
    ubicaciones = generarUbicacionesGenerales(distribucion["porAsignar"])
    listaObjetos = construirListaObjetos(diccionarioPlacas, ubicaciones, catalogos)
    guardarBD(listaObjetos)
    return

def guardarConfiguracion(ventana, entradaTamano, entradaGracia, entradaMonto, variableElectrico, esConfiguracionNueva):
    """
    Funcionalidad: Valida y guarda los datos de configuracion. Si es la primera vez,
    ejecuta el llenado masivo. Si ya existia, pide confirmacion.
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
    if not esConfiguracionNueva:
        respuesta = messagebox.askyesno("Confirmar", "Desea actualizar la configuracion del parqueo")
        if not respuesta:
            return
    config = {
        "tamano": int(tamanoTexto),
        "tiempoGracia": int(graciaTexto),
        "montoHora": int(montoTexto),
        "tieneElectrico": variableElectrico.get()
    }
    guardarConfig(config)
    if esConfiguracionNueva:
        ejecutarLlenadoInicial(config)
        messagebox.showinfo("Configuracion", "Configuracion guardada y parqueo inicializado")
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
        entradaTamano.config(state="disabled")
    tk.Button(ventana,text="Guardar",command=lambda: guardarConfiguracion(ventana, entradaTamano, entradaGracia, entradaMonto, variableElectrico, esConfiguracionNueva)).grid(row=5, column=0, columnspan=2, pady=15)
    ventana.grab_set()
    ventana.wait_window()
    return

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
        ("Reportes", reportes),
        ("Configuracion", lambda: configuracion(ventana)),
        ("Acerca de", lambda: acercaDe(ventana)),
    ]
    for texto, comando in listaBotones:
        tk.Button(ventana, text=texto, command=comando, width=28, height=2, font=("Arial", 11)).pack(pady=5)
    return

def main():
    """
    Funcionalidad: Punto de entrada del sistema. Verifica la configuracion inicial
    y construye la ventana principal con el menu de botones.
    Entrada:
    - Ninguna.
    Salida:
    - None
    """
    ventana = tk.Tk()
    ventana.title("Sistema de Parqueo")
    ventana.geometry("400x450")
    ventana.resizable(False, False)
    configuracionLista = verificarConfiguracionInicial(ventana)
    if configuracionLista:
        construirInterfaz(ventana)
        ventana.mainloop()
    return

main()