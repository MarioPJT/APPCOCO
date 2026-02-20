from tkinter import ttk

def aplicar_estilo():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TButton",
                    font=("Arial", 11),
                    padding=6)

    style.configure("TLabel",
                    font=("Arial", 11))
