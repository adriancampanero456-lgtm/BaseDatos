import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import threading
import time
import platform
import math
import random
from PIL import Image, ImageTk

conexion_cancelada = False

def ejecutar_sin_ventana(cmd):
    if platform.system() == "Windows":
        return subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        return subprocess.run(cmd, capture_output=True, text=True)

def actualizar_texto(texto, color="black"):
    label.config(text=texto, fg=color)

def comprobar_ping():
    global conexion_cancelada
    actualizar_texto("Probando conexión con PC_HP...")
    for _ in range(3):
        if conexion_cancelada: return False
        time.sleep(1)
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            cmd = ["ping", param, "1", "100.108.176.120"]
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0)
            if result.returncode == 0:
                actualizar_texto("Respuesta recibida de PC_HP", "green")
                time.sleep(3)
                return True
        except:
            pass
    mostrar_error_ping()
    return False

def mostrar_error_ping():
    actualizar_texto("Error de conexión (ping)", "red")
    messagebox.showerror("Error de conexión", "El ping ha fallado. Posibles causas:\n"
                                              "- El dispositivo de destino está apagado.\n"
                                              "- No está conectado a Tailscale.\n"
                                              "- Fallo de red o Wi-Fi.")

def comprobar_conexion():
    if not comprobar_ping():
        return False
    return True

def abrir_ruta(usuario=None):
    if not comprobar_conexion():
        return

    destino = f"\\\\100.108.176.120\\tailscale"
    if usuario:
        destino += f"\\{usuario}"

    try:
        os.startfile(destino)
        actualizar_texto(f"Conectado a {usuario if usuario else 'Base de datos'}...")
    except Exception as e:
        actualizar_texto("Error de conexión", "red")
        print(f"Error: {e}")
        return

def ver_carpetas_tailscale():
    carpetas = ["Adrian", "Elena", "Carlos", "General"]
    mostrar_lista_carpetas(carpetas)

def mostrar_lista_carpetas(carpetas):
    lista_carpetas.delete(0, tk.END)
    for carpeta in carpetas:
        lista_carpetas.insert(tk.END, carpeta)

def agregar_carpeta():
    nueva_carpeta = entry_nueva_carpeta.get()
    if nueva_carpeta:
        messagebox.showinfo("Éxito", f"Carpeta '{nueva_carpeta}' agregada.")
        entry_nueva_carpeta.delete(0, tk.END)

def eliminar_carpeta():
    seleccion = lista_carpetas.curselection()
    if seleccion:
        carpeta_a_eliminar = lista_carpetas.get(seleccion)
        messagebox.showinfo("Éxito", f"Carpeta '{carpeta_a_eliminar}' eliminada.")
        lista_carpetas.delete(seleccion)

def crear_spinner(canvas, radio=20, puntos=8):
    canvas.delete("all")
    centro = 50
    for i in range(puntos):
        angle = (2 * math.pi / puntos) * i
        x = centro + radio * math.cos(angle)
        y = centro + radio * math.sin(angle)
        canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="black", tags=f"dot{i}")
    return puntos

def animar_spinner():
    global spinner_estado
    puntos = 8
    activo = (spinner_estado % puntos)
    for i in range(puntos):
        color = "black" if i == activo else "lightgray"
        spinner_canvas.itemconfig(f"dot{i}", fill=color)
    spinner_estado += 1
    if girando:
        root.after(100, animar_spinner)

def iniciar_spinner():
    global girando
    girando = True
    crear_spinner(spinner_canvas)
    animar_spinner()

def detener_spinner():
    global girando
    girando = False

# --- VENTANA INICIAL QUE ESPERA PULSAR TECLA ---
def ventana_inicial():
    ventana = tk.Tk()
    ventana.title("Inicio")
    ventana.geometry("400x150")
    ventana.resizable(False, False)
    ventana.configure(bg="white")

    label = tk.Label(ventana, text="Pulse tecla Enter para continuar", font=("Arial", 14), bg="white")
    label.pack(pady=40)

    def continuar(event=None):
        label.config(text="Leyendo archivo...")
        # Esperamos 3 segundos antes de cerrar la ventana y continuar
        ventana.after(3000, lambda: (ventana.destroy(), mostrar_barra_carga()))

    ventana.bind('<Return>', continuar)

    boton_continuar = tk.Button(ventana, text="Continuar", command=continuar, font=("Arial", 12), bg="gray", fg="white")
    boton_continuar.pack()

    ventana.mainloop()

# --- AVISO DE DESCONTINUACIÓN ---
def mostrar_aviso_con_desconexion(callback_continuar):
    aviso = tk.Toplevel()
    aviso.title("Aviso importante")
    aviso.geometry("400x320")
    aviso.resizable(False, False)
    aviso.configure(bg="white")
    aviso.grab_set()

    try:
        img = Image.open("advertencia.jpg")
        img = img.resize((80, 80), Image.Resampling.LANCZOS)
        foto = ImageTk.PhotoImage(img)
        label_imagen = tk.Label(aviso, image=foto, bg="white")
        label_imagen.image = foto
        label_imagen.pack(pady=10)
    except Exception as e:
        label_imagen = tk.Label(aviso, text="⚠️", font=("Arial", 50), bg="white")
        label_imagen.pack(pady=10)
        print("Error al cargar la imagen:", e)

    def parpadear():
        visible = label_imagen.winfo_ismapped()
        if visible:
            label_imagen.pack_forget()
        else:
            label_imagen.pack(pady=10)
        aviso.after(500, parpadear)
    parpadear()

    texto_aviso = ("Este servicio ha sido discontinuado.\n"
                   "El ordenador que manejó el servicio se dañó y no fue posible recuperar información.\n"
                   "Para evitar posibles problemas, no se restaurará el servicio.\n"
                   "Gracias por todo.")

    label_aviso = tk.Label(aviso, text=texto_aviso, font=("Arial", 14), bg="white", fg="red", justify="center")
    label_aviso.pack(pady=10)

    tiempo_restante = [15]

    label_tiempo = tk.Label(aviso, text=f"Continuar automáticamente en {tiempo_restante[0]} segundos",
                            font=("Arial", 12), bg="white", fg="black")
    label_tiempo.pack(pady=5)

    def cuenta_atras():
        if tiempo_restante[0] <= 0:
            cerrar_aviso()
            return
        tiempo_restante[0] -= 1
        label_tiempo.config(text=f"Continuar automáticamente en {tiempo_restante[0]} segundos")
        aviso.after(1000, cuenta_atras)

    def cerrar_aviso():
        aviso.destroy()
        callback_continuar()

    def boton_continuar():
        cerrar_aviso()

    boton = tk.Button(aviso, text="Continuar", command=boton_continuar, font=("Arial", 12), bg="gray", fg="white")
    boton.pack(pady=10)

    cuenta_atras()

# --- BARRA DE CARGA CON MENSAJES ---
mensajes = [
    (0, 25, "Inicializando programa..."),
    (25, 40, "Leyendo base de datos..."),
    (40, 70, "Buscando mensajes..."),
    (70, 85, "Conectando al servidor..."),
    (85, 100, "Buscando actualizaciones...")
]

progreso = 0.0
aviso_mostrado = False
aviso_pausado = False

def mostrar_barra_carga():
    global progreso, aviso_mostrado, aviso_pausado

    carga = tk.Toplevel()
    carga.title("Inicializando")
    carga.geometry("400x150")
    carga.resizable(False, False)
    carga.configure(bg="white")
    carga.grab_set()

    label_status = tk.Label(carga, text="Iniciando...", font=("Arial", 14), bg="white")
    label_status.pack(pady=10)

    progress_canvas = tk.Canvas(carga, width=350, height=30, bg="white", highlightthickness=1, highlightbackground="black")
    progress_canvas.pack(pady=10)

    barra = progress_canvas.create_rectangle(0, 0, 0, 30, fill="green")

    porcentaje_texto = tk.Label(carga, text="0.00%", font=("Arial", 12), bg="white")
    porcentaje_texto.pack()

    progreso = 0.0
    aviso_mostrado = False
    aviso_pausado = False

    def avanzar_barra():
        global progreso, aviso_mostrado, aviso_pausado

        if aviso_pausado:
            carga.after(100, avanzar_barra)
            return

        if progreso >= 100.0:
            carga.destroy()
            mostrar_ventana_principal()
            return

        incremento = random.uniform(0.1, 0.7)
        progreso = min(progreso + incremento, 100.0)

        ancho = (progreso / 100) * 350
        progress_canvas.coords(barra, 0, 0, ancho, 30)

        porcentaje_texto.config(text=f"{progreso:.2f}%")

        texto_actual = "..."
        for inicio, fin, msg in mensajes:
            if inicio <= progreso < fin:
                texto_actual = msg
                break
        label_status.config(text=texto_actual)

        if not aviso_mostrado and 40 <= progreso <= 70:
            aviso_mostrado = True
            aviso_pausado = True
            def continuar_carga():
                global aviso_pausado
                aviso_pausado = False
            mostrar_aviso_con_desconexion(continuar_carga)

        carga.after(50, avanzar_barra)

    avanzar_barra()

# --- VENTANA PRINCIPAL ---
root = tk.Tk()
root.title("Base de datos")
root.geometry("500x600")
root.configure(bg="white")
root.resizable(False, False)

root.update_idletasks()
ancho = 500
alto = 600
pantalla_ancho = root.winfo_screenwidth()
pantalla_alto = root.winfo_screenheight()
x = (pantalla_ancho // 2) - (ancho // 2)
y = (pantalla_alto // 2) - (alto // 2)
root.geometry(f"{ancho}x{alto}+{x}+{y}")

label = tk.Label(root, text="Selecciona usuario:", font=("Arial", 16), fg="black", bg="white")
label.pack(pady=15)

botones_frame = tk.Frame(root, bg="white")
botones_frame.pack(pady=5)

def mostrar_botones():
    tk.Button(botones_frame, text="Adrián", font=("Arial", 12), width=10, bg="blue", fg="white", command=lambda: abrir_ruta("Adrian")).grid(row=0, column=0, padx=10, pady=5)
    tk.Button(botones_frame, text="Elena", font=("Arial", 12), width=10, bg="green", fg="white", command=lambda: abrir_ruta("Elena")).grid(row=0, column=1, padx=10, pady=5)
    tk.Button(botones_frame, text="Carlos", font=("Arial", 12), width=10, bg="orange", fg="white", command=lambda: abrir_ruta("Carlos")).grid(row=0, column=2, padx=10, pady=5)
    tk.Button(botones_frame, text="General", font=("Arial", 12), width=32, bg="purple", fg="white", command=lambda: abrir_ruta()).grid(row=1, column=0, columnspan=3, pady=10)

mostrar_botones()

boton_ver_carpetas = tk.Button(root, text="Ver carpetas en Tailscale", font=("Arial", 12), bg="cyan", fg="white", command=ver_carpetas_tailscale)
boton_ver_carpetas.pack(pady=10)

lista_carpetas = tk.Listbox(root, width=40, height=6)
lista_carpetas.pack(pady=10)

label_nueva_carpeta = tk.Label(root, text="Nombre de la nueva carpeta:", font=("Arial", 12), bg="white")
label_nueva_carpeta.pack(pady=5)
entry_nueva_carpeta = tk.Entry(root, font=("Arial", 12), width=30)
entry_nueva_carpeta.pack(pady=5)

boton_agregar_carpeta = tk.Button(root, text="Agregar carpeta", font=("Arial", 12), bg="green", fg="white", command=agregar_carpeta)
boton_agregar_carpeta.pack(pady=5)

boton_eliminar_carpeta = tk.Button(root, text="Eliminar carpeta", font=("Arial", 12), bg="red", fg="white", command=eliminar_carpeta)
boton_eliminar_carpeta.pack(pady=5)

spinner_canvas = tk.Canvas(root, width=100, height=100, bg="white", highlightthickness=0)
spinner_canvas.pack()

boton_cancelar = tk.Button(root, text="Cancelar", command=root.quit, font=("Arial", 12), bg="gray", fg="white", width=10)
boton_cancelar.pack(pady=5)

spinner_estado = 0
girando = False
iniciar_spinner()

# Iniciar mostrando la ventana inicial que espera la tecla
ventana_inicial()

root.mainloop()
