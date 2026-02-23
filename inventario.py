import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

def abrir_inventario():

    ventana = tk.Toplevel()
    ventana.title("Inventario")
    ventana.geometry("900x650")

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
    # TABLA (SELECCIÓN MÚLTIPLE)
    # =========================

    columnas = ("ID", "Nombre", "Cantidad", "Precio", "Medida", "Cantidad_Medida")

    tabla = ttk.Treeview(
        ventana,
        columns=columnas,
        show="headings",
        selectmode="extended"  # Permite seleccionar varios
    )

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=130)

    tabla.pack(fill="both", expand=True)

    # =========================
    # TOTALES
    # =========================

    label_total = ttk.Label(ventana, text="Valor Total Inventario: $0")
    label_total.pack(pady=5)

    label_seleccionado = ttk.Label(ventana, text="Total Seleccionado: $0")
    label_seleccionado.pack(pady=5)

    # =========================
    # CONEXIÓN
    # =========================

    def conectar():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="puesto_comida"
        )

    # =========================
    # CARGAR PRODUCTOS
    # =========================

    def cargar_productos():
        for fila in tabla.get_children():
            tabla.delete(fila)

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, cantidad, precio, medida, cantidad_medida FROM productos")

        total = 0

        for fila in cursor.fetchall():
            tabla.insert("", "end", values=fila)
            total += float(fila[2]) * float(fila[3])

        label_total.config(text=f"Valor Total Inventario: ${total:,.2f}")
        label_seleccionado.config(text="Total Seleccionado: $0")

        conexion.close()

    # =========================
    # CALCULAR TOTAL SELECCIONADO
    # =========================

    def calcular_total_seleccionado(event=None):
        seleccionados = tabla.selection()

        total = 0

        for item in seleccionados:
            valores = tabla.item(item)["values"]
            cantidad = float(valores[2])
            precio = float(valores[3])
            total += cantidad * precio

        label_seleccionado.config(
            text=f"Total Seleccionado: ${total:,.2f}"
        )

    # =========================
    # AGREGAR
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

        conexion = conectar()
        cursor = conexion.cursor()

        sql = """
        INSERT INTO productos (nombre, cantidad, precio, medida, cantidad_medida)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (nombre, cantidad, precio, medida, cantidad_medida))
        conexion.commit()
        conexion.close()

        limpiar_campos()
        cargar_productos()

    # =========================
    # ELIMINAR
    # =========================

    def eliminar_producto():
        seleccionados = tabla.selection()

        if not seleccionados:
            messagebox.showwarning("Error", "Selecciona uno o varios productos")
            return

        conexion = conectar()
        cursor = conexion.cursor()

        for item in seleccionados:
            producto_id = tabla.item(item)["values"][0]
            cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))

        conexion.commit()
        conexion.close()

        cargar_productos()

    # =========================
    # EDITAR
    # =========================

    def seleccionar_producto(event):
        seleccionado = tabla.selection()
        if seleccionado:
            item = tabla.item(seleccionado[0])
            datos = item["values"]

            entrada_nombre.delete(0, tk.END)
            entrada_nombre.insert(0, datos[1])

            entrada_cantidad.delete(0, tk.END)
            entrada_cantidad.insert(0, datos[2])

            entrada_precio.delete(0, tk.END)
            entrada_precio.insert(0, datos[3])

            entrada_cantidad_medida.delete(0, tk.END)
            entrada_cantidad_medida.insert(0, datos[5])

            combo_medida.set(datos[4])

    def actualizar_producto():
        seleccionado = tabla.selection()

        if not seleccionado:
            messagebox.showwarning("Error", "Selecciona un producto")
            return

        producto_id = tabla.item(seleccionado[0])["values"][0]

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE productos
            SET nombre=%s, cantidad=%s, precio=%s, medida=%s, cantidad_medida=%s
            WHERE id=%s
        """, (
            entrada_nombre.get(),
            entrada_cantidad.get(),
            entrada_precio.get(),
            combo_medida.get(),
            entrada_cantidad_medida.get(),
            producto_id
        ))

        conexion.commit()
        conexion.close()

        limpiar_campos()
        cargar_productos()

    # =========================
    # LIMPIAR
    # =========================

    def limpiar_campos():
        entrada_nombre.delete(0, tk.END)
        entrada_cantidad.delete(0, tk.END)
        entrada_precio.delete(0, tk.END)
        entrada_cantidad_medida.delete(0, tk.END)

    # =========================
    # BOTONES
    # =========================

    ttk.Button(ventana, text="Agregar Producto", command=guardar_producto).pack(pady=5)
    ttk.Button(ventana, text="Actualizar Producto", command=actualizar_producto).pack(pady=5)
    ttk.Button(ventana, text="Eliminar Producto", command=eliminar_producto).pack(pady=5)

    tabla.bind("<ButtonRelease-1>", seleccionar_producto)
    tabla.bind("<<TreeviewSelect>>", calcular_total_seleccionado)

    cargar_productos()