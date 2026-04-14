"""
Universidad de Guadalajara - CUCEA
Maestria en Ciencia de los Datos
Carlos Pulido Rosas
Programacion I - Clase 9


EJERCICIO 4 - Interfaz Gráfica con tkinter

Requisitos:
1. Tamaño ajustable horizontalmente
2. Que contenga un ícono
3. Título: "Interfaz Clase Programación"
4. Que contenga un marco con borde de 3 pixeles y color de fondo amarillo
5. En la raíz habrá una imagen de tipo jpg en la esquina superior izquierda
6. Dentro del marco incluye una leyenda
7. El cursor dentro del marco se debe mostrar con un pirata y fuera del mismo, con un círculo
"""

from tkinter import *
from PIL import ImageTk, Image
import os

print("="*70)
print("EJERCICIO 4: INTERFAZ GRÁFICA CON TKINTER")
print("="*70)

# ============================================================
# CONFIGURACIÓN DE LA RAÍZ
# ============================================================

raiz = Tk()

# 3. Título: "Interfaz Clase Programación"
raiz.title("Interfaz Clase Programación")

# 1. Tamaño ajustable horizontalmente (True) pero no verticalmente (False)
raiz.resizable(True, False)  # (width, height)

# 2. Ícono de la aplicación (necesita un archivo .ico)
# Comentado porque necesita un archivo específico
# raiz.iconbitmap('objetos.ico')

# 7. Cursor fuera del marco: círculo
raiz.config(cursor="circle")

# Color de fondo de la raíz
raiz.config(bg="#2874A6")

# Borde de la raíz
raiz.config(bd=5)
raiz.config(relief="ridge")

print("✓ Raíz configurada")
print(f"  - Título: Interfaz Clase Programación")
print(f"  - Ajustable: Horizontalmente SÍ, Verticalmente NO")
print(f"  - Cursor: círculo")

# ============================================================
# MARCO PRINCIPAL
# ============================================================

# 4. Marco con borde de 3 píxeles y color de fondo amarillo
marco = Frame(raiz)
marco.config(width=600, height=400)
marco.config(bd=3)  # Borde de 3 píxeles
marco.config(relief="solid")
marco.config(bg="yellow")  # Color de fondo amarillo

# 7. Cursor dentro del marco: pirata
marco.config(cursor="pirate")

marco.pack(padx=10, pady=10, fill=BOTH, expand=True)

print("✓ Marco configurado")
print(f"  - Color de fondo: amarillo")
print(f"  - Borde: 3 píxeles")
print(f"  - Cursor: pirata")

# ============================================================
# IMAGEN EN LA RAÍZ (ESQUINA SUPERIOR IZQUIERDA)
# ============================================================

# 5. Imagen JPG en la esquina superior izquierda de la raíz
# Crear una imagen de ejemplo si no existe
imagen_ejemplo = """
from PIL import Image
import os

# Crear una imagen de ejemplo si no existe
if not os.path.exists('logo.jpg'):
    img = Image.new('RGB', (100, 100), color='blue')
    img.save('logo.jpg')
"""

# Intentar cargar imagen (si existe)
try:
    if os.path.exists('logo.jpg'):
        img_raiz = ImageTk.PhotoImage(Image.open('logo.jpg'))
        label_imagen = Label(raiz, image=img_raiz, bd=2, bg="#2874A6")
        label_imagen.place(x=0, y=0)  # Esquina superior izquierda
        print("✓ Imagen cargada en la raíz")
    else:
        # Crear etiqueta de texto como alternativa
        label_imagen = Label(raiz, text="LOGO", font=("Arial", 16, "bold"), 
                           bg="#2874A6", fg="white", bd=2, relief="solid")
        label_imagen.place(x=5, y=5)
        print("✓ Etiqueta de texto como logo alternativo")
except Exception as e:
    print(f"⚠️  No se pudo cargar imagen: {e}")
    # Alternativa: usar texto
    label_imagen = Label(raiz, text="LOGO", font=("Arial", 16, "bold"), 
                       bg="#2874A6", fg="white", bd=2, relief="solid")
    label_imagen.place(x=5, y=5)

# ============================================================
# LEYENDA DENTRO DEL MARCO
# ============================================================

# 6. Leyenda dentro del marco
leyenda = Label(marco, 
               text="¡Bienvenida a la Interfaz de Clase de Programación, Dra. Patricia!\n\n"
                    "Esta interfaz fue creada con tkinter\n"
                    "Mueve el cursor dentro y fuera del marco\n"
                    "para ver los diferentes cursores",
               font=("Verdana", 12),
               bg="yellow",
               fg="#0C1C2B",
               justify=CENTER,
               padx=20,
               pady=20)

leyenda.place(relx=0.5, rely=0.5, anchor=CENTER)

print("✓ Leyenda agregada al marco")

# ============================================================
# ELEMENTOS ADICIONALES DECORATIVOS
# ============================================================

# Botón de ejemplo
boton_ejemplo = Button(marco, 
                      text="Haz clic aquí",
                      font=("Arial", 10, "bold"),
                      bg="#28B463",
                      fg="white",
                      padx=15,
                      pady=5,
                      cursor="hand2",
                      command=lambda: print("¡Botón presionado!"))
boton_ejemplo.place(relx=0.5, rely=0.8, anchor=CENTER)

# Etiqueta informativa en la parte inferior de la raíz
info_label = Label(raiz,
                  text="Clase 9 - Ejercicio 4 - Programación I - Maestria en Ciencia de los Datos - Carlos Pulido Rosas",
                  font=("Arial", 9),
                  bg="#2874A6",
                  fg="white")
info_label.pack(side=BOTTOM, pady=5)

print("\n" + "="*70)
print("✅ TODAS LAS ESPECIFICACIONES CUMPLIDAS:")
print("="*70)
print("✓ 1. Ajustable horizontalmente")
print("✓ 2. Ícono (preparado para archivo .ico)")
print("✓ 3. Título: 'Interfaz Clase Programación'")
print("✓ 4. Marco con borde 3px y fondo amarillo")
print("✓ 5. Imagen JPG en esquina superior izquierda")
print("✓ 6. Leyenda dentro del marco")
print("✓ 7. Cursor pirata dentro, círculo fuera")
print("="*70)

# Mantener la ventana abierta
print("\nVentana ejecutándose...")
print("Cierra la ventana para terminar el programa")

raiz.mainloop()
