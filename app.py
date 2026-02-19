import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import mysql.connector

# Conexión MySQL
def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # En XAMPP normalmente está vacío
        database="puesto_comida"
    )

def guardar_datos():
    try:
        ventas = float(entry_ventas.get())
        gastos = float(entry_gastos.get())
        ganancia = ventas - gastos
        fecha = datetime.now().date()

        conexion = conectar_db()
        cursor = conexion.cursor()

        sql = "INSERT INTO registros (fecha, ventas, gastos, ganancia) VALUES (%s, %s, %s, %s)"
        valores = (fecha, ventas, gastos, ganancia)

        cursor.execute(sql, valores)
        conexion.commit()

        cursor.close()
        conexion.close()

        label_resultado.config(text=f"Ganancia del día: ${ganancia:,.0f}")
        messagebox.showinfo("Éxito", "Datos guardados en la base de datos")

        entry_ventas.delete(0, tk.END)
        entry_gastos.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

# Ventana principal
ventana = tk.Tk()
ventana.title("Control Puesto de Comida 🍔")
ventana.geometry("400x350")
ventana.configure(bg="#f4f4f4")

titulo = tk.Label(ventana, text="Registro Diario", font=("Arial", 18, "bold"), bg="#f4f4f4")
titulo.pack(pady=20)

tk.Label(ventana, text="Ventas del día ($)", bg="#f4f4f4").pack()
entry_ventas = tk.Entry(ventana)
entry_ventas.pack(pady=5)

tk.Label(ventana, text="Gastos del día ($)", bg="#f4f4f4").pack()
entry_gastos = tk.Entry(ventana)
entry_gastos.pack(pady=5)

btn_guardar = tk.Button(
    ventana,
    text="Guardar",
    bg="#ff6b00",
    fg="white",
    command=guardar_datos
)
btn_guardar.pack(pady=15)

label_resultado = tk.Label(
    ventana,
    text="Ganancia del día: $0",
    font=("Arial", 12),
    bg="#f4f4f4"
)
label_resultado.pack(pady=10)

ventana.mainloop()
