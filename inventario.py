import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

def abrir_inventario():

    ventana = tk.Toplevel()
    ventana.title("Inventario")
    ventana.geometry("700x550")

    # =========================
    # CAMPOS
    # =========================

    ttk.Label(ventana, text="Nombre del producto").pack()
    entrada_nombre = ttk.Entry(ventana)
    entrada_nombre.pack()

    ttk.Label(ventana, text="Cantidad").pack()
    entrada_cantidad = ttk.Entry(ventana)
    entrada_cantidad.pack()

    ttk.Label(ventana, text="Precio").pack()
    entrada_precio = ttk.Entry(ventana)
    entrada_precio.pack()

    ttk.Label(ventana, text="Cantidad por medida").pack()
    entrada_cantidad_medida = ttk.Entry(ventana)
    entrada_cantidad_medida.pack()

    ttk.Label(ventana, text="Tipo de medida").pack()
    medidas = ["Kilogramo", "Libra", "Unidad"]
    combo_medida = ttk.Combobox(ventana, values=medidas)
    combo_medida.pack()
    combo_medida.current(0)

    # =========================
    # TABLA VISUAL
    # =========================

    tabla = ttk.Treeview(ventana)
    tabla["columns"] = ("Nombre", "Cantidad", "Precio", "Medida", "Cantidad_Medida") # se agrego cantidad_medida

    tabla.heading("#0", text="")
    tabla.column("#0", width=0)

    for col in tabla["columns"]:
        tabla.heading(col, text=col)
        tabla.column(col, width=130)

    tabla.pack(fill="both", expand=True)

    # =========================
    # FUNCIÓN CARGAR
    # =========================

    def cargar_productos():
        for fila in tabla.get_children():
            tabla.delete(fila)

        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="puesto_comida"
        )

        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, cantidad, precio, medida, cantidad_medida FROM productos")# Aqui tambien se agrego el cantidad_medida

        for fila in cursor.fetchall():
            tabla.insert("", "end", values=fila)

        conexion.close()

    # =========================
    # FUNCIÓN GUARDAR
    # =========================

    def guardar_producto():
        nombre = entrada_nombre.get()
        cantidad = entrada_cantidad.get()
        precio = entrada_precio.get()
        cantidad_medida = entrada_cantidad_medida.get()
        medida = combo_medida.get()

        if nombre == "" or cantidad == "" or precio == "" or cantidad_medida == "":
            messagebox.showwarning("Error", "Todos los campos son obligatorios")
            return

        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="puesto_comida"
        )

        cursor = conexion.cursor()

        sql = """
        INSERT INTO productos (nombre, cantidad, precio, medida, cantidad_medida)
        VALUES (%s, %s, %s, %s, %s)
        """

        valores = (nombre, cantidad, precio, medida, cantidad_medida)

        cursor.execute(sql, valores)
        conexion.commit()
        conexion.close()

        messagebox.showinfo("Éxito", "Producto guardado correctamente")

        entrada_nombre.delete(0, tk.END)
        entrada_cantidad.delete(0, tk.END)
        entrada_precio.delete(0, tk.END)
        entrada_cantidad_medida.delete(0, tk.END)

        cargar_productos()

    ttk.Button(ventana, text="Agregar Producto", command=guardar_producto).pack(pady=10)

    cargar_productos()