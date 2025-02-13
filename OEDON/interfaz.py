import tkinter as tk
from tkinter import Label
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mysql.connector


AREA_MIN = 20000  # Área mínima para detección (ajustar según resolución de cámara)
AREA_MAX = 67600  # Área máxima para detección
dimensiones_guardadas = []
PIXEL_TO_MM = 0.01  # Factor de conversión de píxeles a milímetros

def habilitar():
    if check_variable.get():
        boton_agregar_lote.config(state="normal")
        textbox_lote_nuevo.config(state="normal")
    else:
        boton_agregar_lote.config(state="disabled")
        textbox_lote_nuevo.config(state="disabled")

def setup_database():
    conn = mysql.connector.connect(
        host="localhost",  # Cambia a la dirección de tu servidor MySQL
        port=3306,
        user="root",  # Cambia a tu usuario de MySQL
        password="312614",  # Cambia a tu contraseña de MySQL
        database="gestion_piezas"  # Cambia al nombre de tu base de datos
    )
    cursor = conn.cursor()
    return conn, cursor

conn, cursor = setup_database()

def obtener_datos():
    cursor = conn.cursor()
    query = """
    SELECT 
    SUM(Valido = 1) AS TotalValidos, 
    SUM(Valido = 0) AS TotalNoValidos
    FROM piezas;
    """
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    return data

def actualizar(frame):
    datos = obtener_datos()
    if datos:
        buenos, defectuosos = datos
        categories = ['Buenos', 'Defectuosos']
        values = [buenos, defectuosos]
        colors = ['#4CAF50', '#FF5722']

        # Limpiar y redibujar el gráfico de barras
        plt.cla()
        plt.bar(categories, values, color=colors)
        plt.title("Cantidad de tuercas validas y No validas")
        plt.ylabel("Cantidad")
        plt.ylim(0, max(values) + 20)  # Ajustar el límite superior del eje Y

def iniciar_grafico():
    fig = plt.figure()
    ani = FuncAnimation(fig, actualizar, interval=1000, cache_frame_data=False)
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def camara_mostrar():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
    lbl_video.after(10, camara_mostrar)

def getContours(img, area_min, area_max, pixel_to_mm):
    dimensiones = []
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area_min < area < area_max:  # Filtrar áreas
            perimetro = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * perimetro, True)
            objCorner = len(approx)

            if objCorner == 6:  # Hexágono detectado
                x, y, w, h = cv2.boundingRect(approx)
                ancho_mm = round(w * pixel_to_mm, 2)
                alto_mm = round(h * pixel_to_mm, 2)
                dimensiones.append((ancho_mm, alto_mm))  # Guardar dimensiones en mm
                
                # Dibujar en el frame
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                texto = f"W: {ancho_mm}mm, H: {alto_mm}mm"
                cv2.putText(frame, texto, (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 2)
    
    return dimensiones

inicio = tk.Tk()
inicio.title("Reconocedor de piezas")

# Obtener la resolución de la pantalla
ancho_pantalla = inicio.winfo_screenwidth()
alto_pantalla = inicio.winfo_screenheight()

# Configurar la ventana para que use la resolución máxima
inicio.geometry(f"{ancho_pantalla}x{alto_pantalla}")

# Crear un frame para la cámara
frame_camara = tk.Frame(inicio)
frame_camara.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Crear un frame para la gráfica
frame_grafico = tk.Frame(inicio)
frame_grafico.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

# Configurar la cámara
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()



# Botón para salir
salir = tk.Button(inicio, text="Salir", command=inicio.quit)
salir.pack(before=frame_camara, side=tk.LEFT,anchor="nw")


# Crear un widget de etiqueta para mostrar el video
lbl_video = Label(frame_camara)
lbl_video.pack()




# Iniciar la visualización de la cámara
camara_mostrar()

# Iniciar la gráfica
iniciar_grafico()

area_min = 20000  # Área mínima para detección
area_max = 67600  # Área máxima para detección
dimensiones_guardadas = []  # Lista para guardar dimensiones
#tiempo_inicio = time.time()  # Tiempo de inicio

lits_lotes = []
check_nuevo_lote = False
check_variable = tk.BooleanVar()

combox_lotes = ttk.Combobox(inicio)
combox_lotes.pack(after=lbl_video)
check_nuevo_lote = tk.Checkbutton(inicio, text="Nuevo lote", variable=check_variable, command=habilitar)
check_nuevo_lote.pack(after=combox_lotes)
textbox_lote_nuevo = ttk.Entry(inicio, state="disabled")
textbox_lote_nuevo.pack(after=check_nuevo_lote)
boton_agregar_lote = tk.Button(inicio, text="Agregar lote", state="disabled")
boton_agregar_lote.pack(after=textbox_lote_nuevo)

inicio.mainloop()

# Liberar la cámara al cerrar la aplicación
cap.release()
cv2.destroyAllWindows()
cursor.close()
conn.close()