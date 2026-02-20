import mysql.connector
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from datetime import datetime

def generar_excel():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="puesto_comida"
    )

    cursor = conexion.cursor()
    cursor.execute("SELECT fecha, tipo, categoria, descripcion, monto FROM registros")
    datos = cursor.fetchall()

    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"

    ws.append(["Fecha", "Tipo", "Categoría", "Descripción", "Monto"])

    for fila in datos:
        ws.append(fila)

    # Crear gráfica
    chart = BarChart()
    chart.title = "Movimientos"

    data = Reference(ws, min_col=5, min_row=1, max_row=len(datos)+1)
    chart.add_data(data, titles_from_data=True)
    ws.add_chart(chart, "G2")

    nombre_archivo = f"Reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(nombre_archivo)

    conexion.close()
