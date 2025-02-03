import tkinter as tk

inicio = tk.Tk()
inicio.attributes('-fullscreen', True, )
salir = tk.Button(inicio, text="Salir", command=inicio.quit)
salir.pack()
inicio.mainloop()