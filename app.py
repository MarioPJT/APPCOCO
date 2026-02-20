import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from styles import aplicar_estilo
from excel import generar_excel
from historial import abrir_historial

# =========================
# FUNCIÓN PARA GUARDAR
# =========================

def guardar_movimiento():
    descripcion = entrada_descripcion.get()
    monto = entrada_monto.get()
    categoria = combo_categoria.get()

    if descripcion == "" or monto == "":
        messagebox.showwarning("Error", "Todos los campos son obligatorios")
        return

    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="puesto_comida"
        )

        cursor = conexion.cursor()

        sql = "INSERT INTO registros (fecha, tipo, categoria, descripcion, monto) VALUES (NOW(), 'Gasto', %s, %s, %s)"
        valores = (categoria, descripcion, monto)

        cursor.execute(sql, valores)
        conexion.commit()

        conexion.close()

        messagebox.showinfo("Éxito", "Movimiento guardado correctamente")

        entrada_descripcion.delete(0, tk.END)
        entrada_monto.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("Error", str(e))


# =========================
# VENTANA PRINCIPAL
# =========================

root = tk.Tk()
root.title("Puesto de Comida")
root.geometry("500x500")

aplicar_estilo()

# =========================
# CAMPOS DE ENTRADA
# =========================

ttk.Label(root, text="Descripción").pack()
entrada_descripcion = ttk.Entry(root)
entrada_descripcion.pack()

ttk.Label(root, text="Monto").pack()
entrada_monto = ttk.Entry(root)
entrada_monto.pack()

ttk.Label(root, text="Categoría").pack()
categorias = ["Insumos", "Gas", "Renta", "Luz", "Transporte", "Otros"]
combo_categoria = ttk.Combobox(root, values=categorias)
combo_categoria.pack()
combo_categoria.current(0)  # Selecciona la primera opción

# Botón Guardar
ttk.Button(root, text="Guardar Movimiento", command=guardar_movimiento).pack(pady=10)

# =========================
# BOTONES EXTRA
# =========================

ttk.Button(root, text="Generar Excel", command=generar_excel).pack(pady=5)
ttk.Button(root, text="Ver Historial", command=abrir_historial).pack(pady=5)

root.mainloop()
