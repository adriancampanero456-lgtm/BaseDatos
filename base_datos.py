import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import threading
import time
import platform
import math
import random
import urllib.request

conexion_cancelada = False

# Ejecutar comando sin mostrar ventana
def ejecutar_sin_ventana(cmd):
    if platform.system() == "Windows":
        return subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        return subprocess.run(cmd, capture_output=True, text=True)

# Actualizar el texto principal
def actualizar_texto(texto, color="black"):
    label.config(text=texto, fg=color)

# Mostrar error ping
def mostrar_error_ping():
    actualizar_texto("Error de conexión (ping)", "red")
    messagebox.showerror("Error de conexión", "No se pudo conectar a \\100.81.205.1.\n"
                                              "Posibles causas:\n"
                                              "- El dispositivo de destino está apagado.\n"
                                              "- No está conectado a la red.\n"
                                              "- Fallo de red o Wi-Fi.")

# Función principal al pulsar "Conectar"
def conectar():
    def tarea():
        actualizar_texto("Probando conexión con Base de datos...")
        param = "-n" if platform.system().lower() == "windows" else "-c"
        try:
            result = subprocess.run(
                ["ping", param, "1", "100.81.205.1"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            if result.returncode == 0:
                actualizar_texto("Conexión establecida", "green")
                time.sleep(0.5)
                try:
                    os.startfile(r"\\100.81.205.1")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo abrir la carpeta: {e}")
            else:
                mostrar_error_ping()
        except Exception as e:
            mostrar_error_ping()
    threading.Thread(target=tarea).start()

# --- Spinner ---
spinner_estado = 0
girando = False

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

# --- Barra de carga ---
mensajes = [
    (0, 25, "Inicializando programa..."),
    (25, 40, "Leyendo base de datos..."),
    (40, 70, "Buscando mensajes..."),
    (70, 85, "Conectando al servidor..."),
    (85, 100, "Verificando actualizaciones...")
]

progreso = 0.0
aviso_mostrado = False
aviso_pausado = False

codigo_remoto_leido = None
codigo_remoto_error = None

def verificar_codigo_remoto_async(callback):
    def tarea():
        global codigo_remoto_leido, codigo_remoto_error
        try:
            url = "https://raw.githubusercontent.com/adriancampanero456-lgtm/BaseDatos/main/base_datos.py"
            with urllib.request.urlopen(url, timeout=10) as response:
                contenido = response.read().decode("utf-8")
                if "404" in contenido or "<html" in contenido.lower() or len(contenido.strip().splitlines()) < 10:
                    raise ValueError("Contenido no válido o acceso denegado")
                codigo_remoto_leido = contenido
                codigo_remoto_error = None
        except Exception as e:
            codigo_remoto_error = str(e)
            codigo_remoto_leido = None
        root.after(0, callback)

    threading.Thread(target=tarea, daemon=True).start()

def mostrar_barra_carga():
    global progreso, aviso_mostrado, aviso_pausado

    carga = tk.Toplevel()
    carga.title("Inicializando")
    carga.geometry("400x150")
    carga.resizable(False, False)
    carga.configure(bg="white")
    carga.protocol("WM_DELETE_WINDOW", lambda: None)
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

    def continuar_carga():
        carga.destroy()
        root.deiconify()
        detener_spinner()

    def avanzar_barra():
        global progreso, aviso_mostrado, aviso_pausado

        if aviso_pausado:
            carga.after(100, avanzar_barra)
            return

        if progreso >= 100.0:
            continuar_carga()
            return

        incremento = random.uniform(2, 4)
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

        if 85 <= progreso < 100 and not aviso_mostrado:
            aviso_mostrado = True
            aviso_pausado = True

            def verificacion_terminada():
                global aviso_pausado
                if codigo_remoto_error:
                    messagebox.showerror("Error actualización", f"No se pudo leer el código remoto:\n{codigo_remoto_error}")
                else:
                    messagebox.showinfo("Actualización", "Se pudo leer el código remoto correctamente.")
                aviso_pausado = False

            verificar_codigo_remoto_async(verificacion_terminada)

        carga.after(50, avanzar_barra)

    avanzar_barra()

# --- Ventana principal ---
root = tk.Tk()
root.title("Base de datos")
root.geometry("400x300")
root.configure(bg="white")
root.resizable(False, False)
root.withdraw()  # Ocultamos al inicio

label = tk.Label(root, text="Conectar a Base de datos", font=("Arial", 16), fg="black", bg="white")
label.pack(pady=30)

boton_conectar = tk.Button(root, text="Conectar", font=("Arial", 14), bg="#4CAF50", fg="white", width=20, command=conectar)
boton_conectar.pack(pady=20)

boton_salir = tk.Button(root, text="Salir", font=("Arial", 12), bg="gray", fg="white", width=10, command=root.quit)
boton_salir.pack(pady=10)

spinner_canvas = tk.Canvas(root, width=100, height=100, bg="white", highlightthickness=0)
spinner_canvas.pack(pady=10)
iniciar_spinner()

# Mostrar barra de carga al inicio
mostrar_barra_carga()

root.mainloop()
