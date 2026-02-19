import tkinter as tk
from tkinter import ttk
import mysql.connector

def abrir_historial():
    ventana = tk.Toplevel()
    ventana.title("Historial de Movimientos")
    ventana.geometry("700x400")

    tabla = ttk.Treeview(ventana)
    tabla["columns"] = ("Fecha", "Tipo", "Categoria", "Descripcion", "Monto")

    for col in tabla["columns"]:
        tabla.heading(col, text=col)

    tabla.pack(fill="both", expand=True)

    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="puesto_comida"
    )

    cursor = conexion.cursor()
    cursor.execute("SELECT fecha, tipo, categoria, descripcion, monto FROM registros")

    for fila in cursor.fetchall():
        tabla.insert("", "end", values=fila)

    conexion.close()
