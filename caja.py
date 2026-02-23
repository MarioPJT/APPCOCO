import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

def abrir_caja():

    ventana = tk.Toplevel()
    ventana.title("Control de Caja")
    ventana.geometry("800x600")

    # =========================
    # CAMPOS
    # =========================

    ttk.Label(ventana, text="Descripción").pack()
    entrada_descripcion = ttk.Entry(ventana)
    entrada_descripcion.pack()

    ttk.Label(ventana, text="Monto").pack()
    entrada_monto = ttk.Entry(ventana)
    entrada_monto.pack()

    ttk.Label(ventana, text="Tipo").pack()
    combo_tipo = ttk.Combobox(ventana, values=["Ingreso", "Egreso"])
    combo_tipo.pack()
    combo_tipo.current(0)

    ttk.Label(ventana, text="Método de Pago").pack()
    combo_metodo = ttk.Combobox(ventana, values=["Efectivo", "Nequi", "Banco"])
    combo_metodo.pack()
    combo_metodo.current(0)

    # =========================
    # TABLA
    # =========================

    columnas = ("ID", "Fecha", "Tipo", "Metodo", "Descripcion", "Monto")

    tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=120)

    tabla.pack(fill="both", expand=True)

    # =========================
    # RESUMEN
    # =========================

    label_efectivo = ttk.Label(ventana, text="Total Efectivo: $0")
    label_efectivo.pack()

    label_nequi = ttk.Label(ventana, text="Total Nequi/Banco: $0")
    label_nequi.pack()

    label_total = ttk.Label(ventana, text="Total General: $0")
    label_total.pack()

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
    # CARGAR DATOS
    # =========================

    def cargar_datos():
        for fila in tabla.get_children():
            tabla.delete(fila)

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, fecha, tipo, metodo, descripcion, monto FROM caja")

        total_efectivo = 0
        total_nequi = 0

        for fila in cursor.fetchall():
            tabla.insert("", "end", values=fila)

            tipo = fila[2]
            metodo = fila[3]
            monto = float(fila[5])

            if tipo == "Ingreso":
                if metodo == "Efectivo":
                    total_efectivo += monto
                else:
                    total_nequi += monto
            else:
                if metodo == "Efectivo":
                    total_efectivo -= monto
                else:
                    total_nequi -= monto

        total_general = total_efectivo + total_nequi

        label_efectivo.config(text=f"Total Efectivo: ${total_efectivo:,.2f}")
        label_nequi.config(text=f"Total Nequi/Banco: ${total_nequi:,.2f}")
        label_total.config(text=f"Total General: ${total_general:,.2f}")

        conexion.close()

    # =========================
    # GUARDAR
    # =========================

    def guardar_movimiento():

        descripcion = entrada_descripcion.get()
        monto = entrada_monto.get()
        tipo = combo_tipo.get()
        metodo = combo_metodo.get()

        if descripcion == "" or monto == "":
            messagebox.showwarning("Error", "Todos los campos son obligatorios")
            return

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO caja (tipo, metodo, descripcion, monto)
            VALUES (%s, %s, %s, %s)
        """, (tipo, metodo, descripcion, monto))

        conexion.commit()
        conexion.close()

        entrada_descripcion.delete(0, tk.END)
        entrada_monto.delete(0, tk.END)

        cargar_datos()

    ttk.Button(ventana, text="Registrar Movimiento", command=guardar_movimiento).pack(pady=10)

    cargar_datos()