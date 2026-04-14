"""
Universidad de Guadalajara - CUCEA
Maestria en Ciencia de los Datos
Carlos Pulido Rosas
Programacion I - Clase 10

EJERCICIO: INTERFAZ GRAFICA CON TKINTER
Sistema de Registro de Clientes - Tienda de Tecnologia

Directrices cumplidas:
1. Nombre completo
2. CURP
3. RFC
4. Sexo (Radio buttons)
5. Tres opciones de servicios (Check buttons)
6. Imagen e icono
"""

from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def crear_imagen_logo():
    """Crea una imagen de logo si no existe"""
    if not os.path.exists('logo_tech.png'):
        try:
            # Crear imagen de 150x150 con fondo azul
            img = Image.new('RGB', (150, 150), color='#2E86C1')
            draw = ImageDraw.Draw(img)
            
            # Dibujar rectangulo interno
            draw.rectangle([20, 20, 130, 130], outline='white', width=5)
            
            # Agregar texto (usando fuente por defecto)
            draw.text((45, 60), "TECH", fill='white')
            draw.text((40, 85), "STORE", fill='white')
            
            img.save('logo_tech.png')
            print("Logo creado exitosamente")
            return True
        except Exception as e:
            print(f"Error al crear logo: {e}")
            return False
    return True

def validar_curp(curp):
    """Valida formato basico de CURP (18 caracteres)"""
    return len(curp) == 18 and curp.isalnum()

def validar_rfc(rfc):
    """Valida formato basico de RFC (12-13 caracteres)"""
    return len(rfc) in [12, 13] and rfc.isalnum()

def registrar_cliente():
    """Procesa y registra la informacion del cliente"""
    
    # Obtener valores de los campos
    nombre = entry_nombre.get().strip()
    curp = entry_curp.get().strip().upper()
    rfc = entry_rfc.get().strip().upper()
    sexo = var_sexo.get()
    
    # Obtener servicios seleccionados
    servicios = []
    if var_servicio1.get():
        servicios.append("Reparacion de Computadoras")
    if var_servicio2.get():
        servicios.append("Venta de Software")
    if var_servicio3.get():
        servicios.append("Asesoria Tecnologica")
    
    # Validaciones
    errores = []
    
    if not nombre:
        errores.append("- El nombre es obligatorio")
    
    if not curp:
        errores.append("- El CURP es obligatorio")
    elif not validar_curp(curp):
        errores.append("- El CURP debe tener 18 caracteres alfanumericos")
    
    if not rfc:
        errores.append("- El RFC es obligatorio")
    elif not validar_rfc(rfc):
        errores.append("- El RFC debe tener 12 o 13 caracteres alfanumericos")
    
    if not sexo:
        errores.append("- Debe seleccionar el sexo")
    
    if not servicios:
        errores.append("- Debe seleccionar al menos un servicio de interes")
    
    # Mostrar errores o confirmar registro
    if errores:
        mensaje_error = "Errores encontrados:\n\n" + "\n".join(errores)
        messagebox.showerror("Error de Validacion", mensaje_error)
    else:
        # Crear mensaje de confirmacion
        mensaje = f"""
REGISTRO EXITOSO

Datos del Cliente:
-----------------------------------
Nombre:    {nombre}
CURP:      {curp}
RFC:       {rfc}
Sexo:      {sexo}

Servicios de Interes:
-----------------------------------
"""
        for servicio in servicios:
            mensaje += f"  • {servicio}\n"
        
        mensaje += "\n¿Desea confirmar el registro?"
        
        # Confirmar con el usuario
        if messagebox.askyesno("Confirmar Registro", mensaje):
            # Guardar en archivo
            with open('clientes_registrados.txt', 'a', encoding='utf-8') as f:
                f.write("="*50 + "\n")
                f.write(f"Nombre: {nombre}\n")
                f.write(f"CURP: {curp}\n")
                f.write(f"RFC: {rfc}\n")
                f.write(f"Sexo: {sexo}\n")
                f.write(f"Servicios: {', '.join(servicios)}\n")
                f.write("="*50 + "\n\n")
            
            messagebox.showinfo("Exito", "Cliente registrado correctamente!\n\nLos datos se han guardado en 'clientes_registrados.txt'")
            limpiar_formulario()

def limpiar_formulario():
    """Limpia todos los campos del formulario"""
    entry_nombre.delete(0, END)
    entry_curp.delete(0, END)
    entry_rfc.delete(0, END)
    var_sexo.set("")
    var_servicio1.set(False)
    var_servicio2.set(False)
    var_servicio3.set(False)
    entry_nombre.focus()

def salir_aplicacion():
    """Cierra la aplicacion con confirmacion"""
    if messagebox.askyesno("Salir", "¿Esta seguro que desea salir?"):
        raiz.quit()

# ============================================================
# CONFIGURACION DE LA VENTANA PRINCIPAL
# ============================================================

raiz = Tk()
raiz.title("Sistema de Registro de Clientes - Tech Store")
raiz.geometry("700x650")
raiz.resizable(False, False)
raiz.config(bg="#ECF0F1")

# Intentar crear el logo
crear_imagen_logo()

# ============================================================
# HEADER - ENCABEZADO
# ============================================================

frame_header = Frame(raiz, bg="#2E86C1", height=100)
frame_header.pack(fill=X)

# Logo en el header
try:
    if os.path.exists('logo_tech.png'):
        img_logo = Image.open('logo_tech.png')
        img_logo = img_logo.resize((80, 80))
        photo_logo = ImageTk.PhotoImage(img_logo)
        label_logo = Label(frame_header, image=photo_logo, bg="#2E86C1")
        label_logo.image = photo_logo  # Mantener referencia
        label_logo.pack(side=LEFT, padx=20, pady=10)
except:
    # Alternativa si no se puede cargar la imagen
    label_logo_text = Label(frame_header, 
                           text="TECH\nSTORE", 
                           font=("Arial", 16, "bold"),
                           bg="#2E86C1", 
                           fg="white",
                           justify=CENTER)
    label_logo_text.pack(side=LEFT, padx=20, pady=10)

# Titulo principal
label_titulo = Label(frame_header,
                    text="SISTEMA DE REGISTRO DE CLIENTES",
                    font=("Arial", 20, "bold"),
                    bg="#2E86C1",
                    fg="white")
label_titulo.pack(side=LEFT, padx=20)

# ============================================================
# FRAME PRINCIPAL - FORMULARIO
# ============================================================

frame_formulario = Frame(raiz, bg="#ECF0F1")
frame_formulario.pack(pady=20, padx=30, fill=BOTH, expand=True)

# Subtitulo
label_subtitulo = Label(frame_formulario,
                       text="Complete los siguientes datos:",
                       font=("Arial", 12, "bold"),
                       bg="#ECF0F1",
                       fg="#2C3E50")
label_subtitulo.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=W)

# ============================================================
# CAMPOS DEL FORMULARIO
# ============================================================

# 1. NOMBRE COMPLETO
Label(frame_formulario, 
      text="Nombre Completo:",
      font=("Arial", 11),
      bg="#ECF0F1",
      fg="#2C3E50").grid(row=1, column=0, sticky=W, pady=10)

entry_nombre = Entry(frame_formulario, 
                    font=("Arial", 11),
                    width=40)
entry_nombre.grid(row=1, column=1, sticky=W, padx=10, pady=10)

# 2. CURP
Label(frame_formulario,
      text="CURP:",
      font=("Arial", 11),
      bg="#ECF0F1",
      fg="#2C3E50").grid(row=2, column=0, sticky=W, pady=10)

entry_curp = Entry(frame_formulario,
                  font=("Arial", 11),
                  width=40)
entry_curp.grid(row=2, column=1, sticky=W, padx=10, pady=10)

Label(frame_formulario,
      text="(18 caracteres)",
      font=("Arial", 9, "italic"),
      bg="#ECF0F1",
      fg="#7F8C8D").grid(row=2, column=2, sticky=W, padx=5)

# 3. RFC
Label(frame_formulario,
      text="RFC:",
      font=("Arial", 11),
      bg="#ECF0F1",
      fg="#2C3E50").grid(row=3, column=0, sticky=W, pady=10)

entry_rfc = Entry(frame_formulario,
                 font=("Arial", 11),
                 width=40)
entry_rfc.grid(row=3, column=1, sticky=W, padx=10, pady=10)

Label(frame_formulario,
      text="(12-13 caracteres)",
      font=("Arial", 9, "italic"),
      bg="#ECF0F1",
      fg="#7F8C8D").grid(row=3, column=2, sticky=W, padx=5)

# 4. SEXO (RADIO BUTTONS)
Label(frame_formulario,
      text="Sexo:",
      font=("Arial", 11, "bold"),
      bg="#ECF0F1",
      fg="#2C3E50").grid(row=4, column=0, sticky=W, pady=15)

var_sexo = StringVar()

frame_sexo = Frame(frame_formulario, bg="#ECF0F1")
frame_sexo.grid(row=4, column=1, sticky=W, padx=10, pady=15)

Radiobutton(frame_sexo,
           text="Femenino",
           variable=var_sexo,
           value="Femenino",
           font=("Arial", 10),
           bg="#ECF0F1",
           fg="#2C3E50").pack(side=LEFT, padx=(0, 20))

Radiobutton(frame_sexo,
           text="Masculino",
           variable=var_sexo,
           value="Masculino",
           font=("Arial", 10),
           bg="#ECF0F1",
           fg="#2C3E50").pack(side=LEFT)

# 5. SERVICIOS DE INTERES (CHECK BUTTONS)
Label(frame_formulario,
      text="Servicios de Interes:",
      font=("Arial", 11, "bold"),
      bg="#ECF0F1",
      fg="#2C3E50").grid(row=5, column=0, sticky=NW, pady=15)

frame_servicios = Frame(frame_formulario, bg="#ECF0F1")
frame_servicios.grid(row=5, column=1, sticky=W, padx=10, pady=15)

var_servicio1 = BooleanVar()
var_servicio2 = BooleanVar()
var_servicio3 = BooleanVar()

Checkbutton(frame_servicios,
           text="Reparacion de Computadoras",
           variable=var_servicio1,
           font=("Arial", 10),
           bg="#ECF0F1",
           fg="#2C3E50").pack(anchor=W, pady=5)

Checkbutton(frame_servicios,
           text="Venta de Software",
           variable=var_servicio2,
           font=("Arial", 10),
           bg="#ECF0F1",
           fg="#2C3E50").pack(anchor=W, pady=5)

Checkbutton(frame_servicios,
           text="Asesoria Tecnologica",
           variable=var_servicio3,
           font=("Arial", 10),
           bg="#ECF0F1",
           fg="#2C3E50").pack(anchor=W, pady=5)

# ============================================================
# BOTONES DE ACCION
# ============================================================

frame_botones = Frame(raiz, bg="#ECF0F1")
frame_botones.pack(pady=20)

btn_registrar = Button(frame_botones,
                      text="Registrar Cliente",
                      font=("Arial", 12, "bold"),
                      bg="#27AE60",
                      fg="white",
                      padx=20,
                      pady=10,
                      cursor="hand2",
                      command=registrar_cliente)
btn_registrar.pack(side=LEFT, padx=10)

btn_limpiar = Button(frame_botones,
                    text="Limpiar Formulario",
                    font=("Arial", 12, "bold"),
                    bg="#F39C12",
                    fg="white",
                    padx=20,
                    pady=10,
                    cursor="hand2",
                    command=limpiar_formulario)
btn_limpiar.pack(side=LEFT, padx=10)

btn_salir = Button(frame_botones,
                  text="Salir",
                  font=("Arial", 12, "bold"),
                  bg="#E74C3C",
                  fg="white",
                  padx=20,
                  pady=10,
                  cursor="hand2",
                  command=salir_aplicacion)
btn_salir.pack(side=LEFT, padx=10)

# ============================================================
# FOOTER
# ============================================================

frame_footer = Frame(raiz, bg="#34495E", height=40)
frame_footer.pack(side=BOTTOM, fill=X)

label_footer = Label(frame_footer,
                    text="Carlos Pulido Rosas - Sistema de Gestion de Clientes | v1.0",
                    font=("Arial", 9),
                    bg="#34495E",
                    fg="white")
label_footer.pack(pady=10)

# ============================================================
# CONFIGURACIONES FINALES
# ============================================================

# Establecer foco inicial
entry_nombre.focus()

# Mensaje de bienvenida
print("="*60)
print("SISTEMA DE REGISTRO DE CLIENTES - TECH STORE")
print("="*60)
print("\nGiro del negocio: Tienda de Tecnologia")
print("\nServicios ofrecidos:")
print("  1. Reparacion de Computadoras")
print("  2. Venta de Software")
print("  3. Asesoria Tecnologica")
print("\nDirectrices cumplidas:")
print("  [X] 1. Campo Nombre completo")
print("  [X] 2. Campo CURP")
print("  [X] 3. Campo RFC")
print("  [X] 4. Sexo con Radio buttons")
print("  [X] 5. Tres opciones con Check buttons")
print("  [X] 6. Imagen y logo incluidos")
print("\nLa interfaz esta lista para usarse.")
print("="*60)

# Iniciar aplicacion
raiz.mainloop()