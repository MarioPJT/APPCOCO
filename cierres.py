import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime, date
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


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
# 🔐 GUARDAR CIERRE DEL DÍA
# =========================

def guardar_cierre_dia():

    conexion = conectar()
    cursor = conexion.cursor()

    # Verificar si ya existe
    cursor.execute("SELECT COUNT(*) FROM cierre_caja WHERE fecha = CURDATE()")
    if cursor.fetchone()[0] > 0:
        messagebox.showwarning("Aviso", "Ya existe cierre hoy.")
        conexion.close()
        return

    cursor.execute("""
        SELECT tipo, metodo, monto
        FROM caja
        WHERE DATE(fecha) = CURDATE()
    """)

    movimientos = cursor.fetchall()

    if not movimientos:
        messagebox.showinfo("Info", "No hay movimientos hoy.")
        conexion.close()
        return

    efectivo = nequi = banco = 0

    for tipo, metodo, monto in movimientos:
        monto = float(monto)

        if tipo == "Ingreso":
            if metodo == "Efectivo":
                efectivo += monto
            elif metodo == "Nequi":
                nequi += monto
            elif metodo == "Banco":
                banco += monto
        else:
            if metodo == "Efectivo":
                efectivo -= monto
            elif metodo == "Nequi":
                nequi -= monto
            elif metodo == "Banco":
                banco -= monto

    total = efectivo + nequi + banco

    cursor.execute("""
        INSERT INTO cierre_caja
        (fecha, total_efectivo, total_nequi, total_banco, total_general)
        VALUES (CURDATE(), %s, %s, %s, %s)
    """, (efectivo, nequi, banco, total))

    conexion.commit()
    conexion.close()

    messagebox.showinfo("OK", "Cierre guardado correctamente.")


# =========================
# 📊 VENTANA HISTORIAL
# =========================

def ver_historial_cierres():

    ventana = tk.Toplevel()
    ventana.title("Historial de Cierres")
    ventana.geometry("1000x600")

    # FILTROS
    frame_filtro = tk.Frame(ventana)
    frame_filtro.pack(pady=10)

    tk.Label(frame_filtro, text="Desde (YYYY-MM-DD)").grid(row=0, column=0)
    entrada_desde = tk.Entry(frame_filtro)
    entrada_desde.grid(row=0, column=1)

    tk.Label(frame_filtro, text="Hasta").grid(row=0, column=2)
    entrada_hasta = tk.Entry(frame_filtro)
    entrada_hasta.grid(row=0, column=3)

    columnas = ("ID", "Fecha", "Efectivo", "Nequi", "Banco", "Total")
    tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=150)

    tabla.pack(fill="both", expand=True)

    # =========================
    # CARGAR
    # =========================

    def cargar(desde=None, hasta=None):

        for fila in tabla.get_children():
            tabla.delete(fila)

        conexion = conectar()
        cursor = conexion.cursor()

        if desde and hasta:
            cursor.execute("""
                SELECT * FROM cierre_caja
                WHERE fecha BETWEEN %s AND %s
            """, (desde, hasta))
        else:
            cursor.execute("SELECT * FROM cierre_caja")

        for fila in cursor.fetchall():
            tabla.insert("", "end", values=fila)

        conexion.close()

    # =========================
    # DOBLE CLIC EDITAR
    # =========================

    def editar(event):

        seleccionado = tabla.selection()
        if not seleccionado:
            return

        datos = tabla.item(seleccionado)["values"]
        id_cierre = datos[0]
        fecha_cierre = datos[1]

        # 🔒 Bloquear si tiene más de 3 días
        if (date.today() - fecha_cierre).days > 3:
            messagebox.showwarning("Bloqueado", "No se puede editar cierres antiguos.")
            return

        ventana_edit = tk.Toplevel()
        ventana_edit.title("Editar")

        e1 = tk.Entry(ventana_edit)
        e1.insert(0, datos[2])
        e1.pack()

        e2 = tk.Entry(ventana_edit)
        e2.insert(0, datos[3])
        e2.pack()

        e3 = tk.Entry(ventana_edit)
        e3.insert(0, datos[4])
        e3.pack()

        def actualizar():
            efectivo = float(e1.get())
            nequi = float(e2.get())
            banco = float(e3.get())
            total = efectivo + nequi + banco

            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE cierre_caja
                SET total_efectivo=%s,
                    total_nequi=%s,
                    total_banco=%s,
                    total_general=%s
                WHERE id=%s
            """, (efectivo, nequi, banco, total, id_cierre))
            conexion.commit()
            conexion.close()

            ventana_edit.destroy()
            cargar()

        tk.Button(ventana_edit, text="Actualizar", command=actualizar).pack()

    tabla.bind("<Double-1>", editar)

    # =========================
    # EXPORTAR EXCEL
    # =========================

    def exportar_excel():

        wb = Workbook()
        ws = wb.active
        ws.append(columnas)

        for row in tabla.get_children():
            ws.append(tabla.item(row)["values"])

        nombre = f"Cierres_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        wb.save(nombre)

        messagebox.showinfo("Excel", "Archivo exportado.")

    # =========================
    # PDF INDIVIDUAL
    # =========================

    def generar_pdf():

        seleccionado = tabla.selection()
        if not seleccionado:
            return

        datos = tabla.item(seleccionado)["values"]

        nombre = f"Cierre_{datos[1]}.pdf"
        doc = SimpleDocTemplate(nombre, pagesize=letter)
        styles = getSampleStyleSheet()

        elements = []
        elements.append(Paragraph("Reporte de Cierre", styles["Title"]))
        elements.append(Spacer(1, 20))

        tabla_pdf = Table([
            ["Fecha", datos[1]],
            ["Efectivo", datos[2]],
            ["Nequi", datos[3]],
            ["Banco", datos[4]],
            ["Total", datos[5]],
        ])

        elements.append(tabla_pdf)
        doc.build(elements)

        messagebox.showinfo("PDF", "PDF generado.")

    # BOTONES
    tk.Button(frame_filtro, text="Filtrar", command=lambda: cargar(
        entrada_desde.get(), entrada_hasta.get()
    )).grid(row=0, column=4, padx=5)

    tk.Button(ventana, text="Exportar Excel", command=exportar_excel).pack(pady=5)
    tk.Button(ventana, text="Generar PDF", command=generar_pdf).pack(pady=5)

    cargar()