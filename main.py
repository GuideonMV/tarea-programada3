import tkinter as tk
from tkinter import messagebox

def obtenerVehiculos():
    messagebox.showinfo("Info", "Proximamente: Obtener vehiculos")

def verEstacionamiento():
    messagebox.showinfo("Info", "Proximamente: Ver estacionamiento")

def reportes():
    messagebox.showinfo("Info", "Proximamente: Reportes")

def configuracion():
    messagebox.showinfo("Info", "Proximamente: Configuracion")

def acercaDe():
    messagebox.showinfo("Info", "Proximamente: Acerca de")

def construirInterfaz(ventana):
    tk.Label(ventana, text="Sistema de Parqueo", font=("Arial", 18, "bold")).pack(pady=20)
    listaBotones = [
        ("Obtener vehiculos", obtenerVehiculos),
        ("Ver estacionamiento", verEstacionamiento),
        ("Reportes", reportes),
        ("Configuracion", configuracion),
        ("Acerca de",acercaDe),
    ]
    for texto, comando in listaBotones:
        tk.Button(ventana, text=texto, command=comando, width=28, height=2, font=("Arial", 11)).pack(pady=5)
    return

def main():
    ventana = tk.Tk()
    ventana.title("Sistema de Parqueo")
    ventana.geometry("400x450")
    ventana.resizable(False, False)
    construirInterfaz(ventana)
    ventana.mainloop()

main()