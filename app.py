import tkinter as tk
from tkinter import ttk
from styles import aplicar_estilo
from excel import generar_excel
from historial import abrir_historial
from inventario import abrir_inventario

# =========================
# VENTANA PRINCIPAL
# =========================

root = tk.Tk()
root.title("Puesto de Comida")
root.geometry("400x300")

aplicar_estilo()

# =========================
# BOTONES PRINCIPALES
# =========================

ttk.Button(root, text="Generar Excel", command=generar_excel).pack(pady=10)
ttk.Button(root, text="Ver Historial", command=abrir_historial).pack(pady=10)
ttk.Button(root, text="Inventario", command=abrir_inventario).pack(pady=10)

root.mainloop()