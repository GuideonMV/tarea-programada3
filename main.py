import tkinter as tk
import tkinter as tk
from tkinter import messagebox

from funcionamiento.baseDatos import guardarConfig, cargarConfig, existeConfig, guardarBD, guardarCatalogos, cargarCatalogos, cargarBD
from funcionamiento.api import obtenerDatosMockaroo, filtrarRegistros, obtenerListasUnicas
from funcionamiento.calculosParqueo import calcularDistribucionEspacios, obtenerUbicacionesOcupadas, buscarObjetoPorUbicacion
from funcionamiento.catalogos import construirCatalogos
from funcionamiento.llenadoMasivo import generarUbicacionesGenerales, construirListaObjetos, generarTodasLasUbicaciones

def obtenerVehiculos():
    messagebox.showinfo("Info", "Proximamente: Obtener vehiculos")

def verEstacionamiento():
    messagebox.showinfo("Info", "Proximamente: Ver estacionamiento")

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

def acercaDe():
    messagebox.showinfo("Info", "Proximamente: Acerca de")

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
        ("Obtener vehiculos", obtenerVehiculos),
        ("Ver estacionamiento", verEstacionamiento),
        ("Reportes", reportes),
        ("Configuracion", lambda: configuracion(ventana)),
        ("Acerca de", acercaDe),
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