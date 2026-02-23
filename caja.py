import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import matplotlib.pyplot as plt

# 🔄 ACTUALIZADO: imports para PDF profesional
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from datetime import datetime


def abrir_caja():

    ventana = tk.Toplevel()
    ventana.title("Control de Caja")
    ventana.geometry("900x650")  # 🔄 ACTUALIZADO tamaño mejorado

    # =========================
    # CONEXIÓN BD
    # =========================

    def conectar():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="puesto_comida"
        )

    # =========================
    # CAMPOS
    # =========================

    ttk.Label(ventana, text="Descripción").pack()
    entrada_descripcion = ttk.Entry(ventana, width=40)
    entrada_descripcion.pack()

    ttk.Label(ventana, text="Monto").pack()
    entrada_monto = ttk.Entry(ventana, width=20)
    entrada_monto.pack()

    ttk.Label(ventana, text="Tipo").pack()
    combo_tipo = ttk.Combobox(ventana, values=["Ingreso", "Egreso"], state="readonly")
    combo_tipo.pack()
    combo_tipo.current(0)

    ttk.Label(ventana, text="Método de Pago").pack()
    combo_metodo = ttk.Combobox(
        ventana,
        values=["Efectivo", "Nequi", "Banco"],
        state="readonly"
    )
    combo_metodo.pack()
    combo_metodo.current(0)

    # =========================
    # TABLA
    # =========================

    columnas = ("ID", "Fecha", "Tipo", "Metodo", "Descripcion", "Monto")

    tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=130)

    tabla.pack(fill="both", expand=True, pady=10)

    # =========================
    # RESUMEN
    # =========================

    label_efectivo = ttk.Label(ventana, text="Total Efectivo: $0")
    label_efectivo.pack()

    label_nequi = ttk.Label(ventana, text="Total Nequi: $0")
    label_nequi.pack()

    label_banco = ttk.Label(ventana, text="Total Banco: $0")
    label_banco.pack()

    label_total = ttk.Label(ventana, text="Total General: $0")
    label_total.pack(pady=5)

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
        total_banco = 0

        # 🔄 ACTUALIZADO: cálculo ahora correctamente dentro del for
        for fila in cursor.fetchall():

            tabla.insert("", "end", values=fila)

            tipo = fila[2]
            metodo = fila[3]
            monto = float(fila[5])

            if tipo == "Ingreso":

                if metodo == "Efectivo":
                    total_efectivo += monto

                elif metodo == "Nequi":
                    total_nequi += monto

                elif metodo == "Banco":
                    total_banco += monto

            else:  # Egreso

                if metodo == "Efectivo":
                    total_efectivo -= monto

                elif metodo == "Nequi":
                    total_nequi -= monto

                elif metodo == "Banco":
                    total_banco -= monto

        label_efectivo.config(text=f"Total Efectivo: ${total_efectivo:,.2f}")
        label_nequi.config(text=f"Total Nequi: ${total_nequi:,.2f}")
        label_banco.config(text=f"Total Banco: ${total_banco:,.2f}")

        total_general = total_efectivo + total_nequi + total_banco
        label_total.config(text=f"Total General: ${total_general:,.2f}")

        conexion.close()

    # =========================
    # GUARDAR MOVIMIENTO
    # =========================

    def guardar_movimiento():

        descripcion = entrada_descripcion.get()
        monto = entrada_monto.get()
        tipo = combo_tipo.get()
        metodo = combo_metodo.get()

        if descripcion == "" or monto == "":
            messagebox.showwarning("Error", "Todos los campos son obligatorios")
            return

        try:
            monto = float(monto)  # 🔄 ACTUALIZADO validación numérica
        except:
            messagebox.showerror("Error", "El monto debe ser numérico")
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

    # =========================
    # GRÁFICA
    # =========================

    def mostrar_grafica():

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT metodo, SUM(monto)
            FROM caja
            WHERE tipo='Ingreso'
            GROUP BY metodo
        """)

        datos = cursor.fetchall()
        conexion.close()

        if not datos:
            messagebox.showinfo("Info", "No hay datos para mostrar")
            return

        metodos = [fila[0] for fila in datos]
        montos = [float(fila[1]) for fila in datos]

        plt.figure()
        plt.bar(metodos, montos)
        plt.title("Ingresos por Método de Pago")
        plt.xlabel("Método")
        plt.ylabel("Monto")
        plt.tight_layout()
        plt.show()

    # =========================
    # PDF PROFESIONAL
    # =========================

    def generar_pdf():

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT fecha, tipo, metodo, descripcion, monto FROM caja")

            datos = cursor.fetchall()
            conexion.close()

            if not datos:
                messagebox.showinfo("Info", "No hay datos para generar el PDF")
                return

            nombre_archivo = f"Reporte_Caja_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("<b>REPORTE DE CAJA</b>", styles["Title"]))
            elements.append(Spacer(1, 20))

            data = [["Fecha", "Tipo", "Método", "Descripción", "Monto"]]

            total_general = 0

            for fila in datos:
                data.append([
                    str(fila[0]),
                    fila[1],
                    fila[2],
                    fila[3],
                    f"${float(fila[4]):,.2f}"
                ])
                total_general += float(fila[4])

            table = Table(data, repeatRows=1)

            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('ALIGN', (-1,1), (-1,-1), 'RIGHT'),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 20))

            elements.append(
                Paragraph(f"<b>Total General: ${total_general:,.2f}</b>", styles["Heading2"])
            )

            doc.build(elements)

            messagebox.showinfo("PDF", f"Reporte generado: {nombre_archivo}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # BOTONES
    # =========================

    ttk.Button(ventana, text="Registrar Movimiento", command=guardar_movimiento).pack(pady=5)
    ttk.Button(ventana, text="Ver Gráfica", command=mostrar_grafica).pack(pady=5)
    ttk.Button(ventana, text="Generar PDF", command=generar_pdf).pack(pady=5)

    cargar_datos()