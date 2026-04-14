"""
GUÍA DE REFERENCIA RÁPIDA DE SELENIUM
Comandos y técnicas más comunes
"""

# ============================================================
# CONFIGURACIÓN INICIAL
# ============================================================

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Configurar opciones del navegador
chrome_options = Options()
chrome_options.add_argument('--headless')  # Sin interfaz gráfica
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Iniciar driver
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

# ============================================================
# NAVEGACIÓN
# ============================================================

driver.get("https://www.ejemplo.com")           # Navegar a URL
driver.back()                                    # Ir atrás
driver.forward()                                 # Ir adelante
driver.refresh()                                 # Refrescar página
driver.current_url                               # Obtener URL actual
driver.title                                     # Obtener título

# ============================================================
# LOCALIZAR ELEMENTOS
# ============================================================

# Por ID
elemento = driver.find_element(By.ID, "mi-id")

# Por nombre
elemento = driver.find_element(By.NAME, "username")

# Por clase CSS
elemento = driver.find_element(By.CLASS_NAME, "mi-clase")

# Por selector CSS
elemento = driver.find_element(By.CSS_SELECTOR, ".clase #id")

# Por XPath
elemento = driver.find_element(By.XPATH, "//div[@class='contenedor']")

# Por texto del enlace
elemento = driver.find_element(By.LINK_TEXT, "Haz clic aquí")
elemento = driver.find_element(By.PARTIAL_LINK_TEXT, "clic")

# Por etiqueta
elemento = driver.find_element(By.TAG_NAME, "h1")

# Múltiples elementos
elementos = driver.find_elements(By.CLASS_NAME, "item")

# ============================================================
# INTERACCIÓN CON ELEMENTOS
# ============================================================

# Hacer clic
elemento.click()

# Escribir texto
elemento.send_keys("Texto a escribir")

# Limpiar campo
elemento.clear()

# Enviar tecla especial
elemento.send_keys(Keys.RETURN)     # Enter
elemento.send_keys(Keys.TAB)        # Tab
elemento.send_keys(Keys.ESCAPE)     # Escape
elemento.send_keys(Keys.CONTROL, 'a')  # Ctrl+A

# Obtener texto
texto = elemento.text

# Obtener atributo
valor = elemento.get_attribute("value")
href = elemento.get_attribute("href")

# Verificar si está visible/habilitado/seleccionado
elemento.is_displayed()
elemento.is_enabled()
elemento.is_selected()

# ============================================================
# ESPERAS
# ============================================================

import time

# Espera implícita (global)
driver.implicitly_wait(10)

# Espera explícita
elemento = wait.until(
    EC.presence_of_element_located((By.ID, "mi-id"))
)

# Esperas más comunes:
EC.title_is("Título esperado")
EC.title_contains("parte del título")
EC.presence_of_element_located((By.ID, "id"))
EC.visibility_of_element_located((By.ID, "id"))
EC.element_to_be_clickable((By.ID, "id"))
EC.text_to_be_present_in_element((By.ID, "id"), "texto")

# Espera simple (no recomendado en producción)
time.sleep(2)

# ============================================================
# ACCIONES AVANZADAS
# ============================================================

actions = ActionChains(driver)

# Mover el mouse a un elemento
actions.move_to_element(elemento).perform()

# Clic derecho
actions.context_click(elemento).perform()

# Doble clic
actions.double_click(elemento).perform()

# Drag and drop
actions.drag_and_drop(origen, destino).perform()

# Mantener tecla presionada
actions.key_down(Keys.CONTROL).click(elemento).key_up(Keys.CONTROL).perform()

# ============================================================
# JAVASCRIPT
# ============================================================

# Ejecutar JavaScript
resultado = driver.execute_script("return document.title")

# Hacer scroll
driver.execute_script("window.scrollTo(0, 500)")
driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

# Scroll a elemento
driver.execute_script("arguments[0].scrollIntoView()", elemento)

# Hacer clic con JavaScript (útil si el clic normal falla)
driver.execute_script("arguments[0].click()", elemento)

# ============================================================
# VENTANAS Y PESTAÑAS
# ============================================================

# Obtener handle de ventana actual
ventana_actual = driver.current_window_handle

# Obtener todos los handles
todas_ventanas = driver.window_handles

# Cambiar a otra ventana
driver.switch_to.window(todas_ventanas[1])

# Abrir nueva pestaña
driver.execute_script("window.open('');")
driver.switch_to.window(driver.window_handles[-1])

# Cerrar pestaña actual
driver.close()

# ============================================================
# FRAMES E IFRAMES
# ============================================================

# Cambiar a frame
driver.switch_to.frame("nombre_frame")
driver.switch_to.frame(0)  # Por índice
driver.switch_to.frame(elemento_frame)  # Por elemento

# Volver al contenido principal
driver.switch_to.default_content()

# ============================================================
# ALERTAS
# ============================================================

# Cambiar a alerta
alerta = driver.switch_to.alert

# Obtener texto de alerta
texto_alerta = alerta.text

# Aceptar alerta
alerta.accept()

# Rechazar alerta
alerta.dismiss()

# Enviar texto a alerta (prompt)
alerta.send_keys("texto")

# ============================================================
# COOKIES
# ============================================================

# Obtener todas las cookies
cookies = driver.get_cookies()

# Obtener cookie específica
cookie = driver.get_cookie("nombre_cookie")

# Agregar cookie
driver.add_cookie({"name": "nombre", "value": "valor"})

# Eliminar cookie
driver.delete_cookie("nombre_cookie")

# Eliminar todas las cookies
driver.delete_all_cookies()

# ============================================================
# SCREENSHOTS
# ============================================================

# Screenshot de página completa
driver.save_screenshot("captura.png")

# Screenshot de elemento específico
elemento.screenshot("elemento.png")

# Screenshot como bytes
screenshot_bytes = driver.get_screenshot_as_png()

# ============================================================
# SELECT (DROPDOWNS)
# ============================================================

from selenium.webdriver.support.ui import Select

select = Select(driver.find_element(By.ID, "dropdown"))

# Seleccionar por texto visible
select.select_by_visible_text("Opción 1")

# Seleccionar por valor
select.select_by_value("valor1")

# Seleccionar por índice
select.select_by_index(0)

# Obtener opciones seleccionadas
opciones = select.all_selected_options

# Deseleccionar (solo para múltiple)
select.deselect_all()

# ============================================================
# INFORMACIÓN DEL NAVEGADOR
# ============================================================

# Dimensiones de ventana
driver.get_window_size()
driver.set_window_size(1920, 1080)

# Maximizar ventana
driver.maximize_window()

# Posición de ventana
driver.get_window_position()
driver.set_window_position(0, 0)

# User agent
user_agent = driver.execute_script("return navigator.userAgent")

# ============================================================
# MANEJO DE ERRORES
# ============================================================

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException
)

try:
    elemento = driver.find_element(By.ID, "no-existe")
except NoSuchElementException:
    print("Elemento no encontrado")

try:
    elemento = wait.until(EC.presence_of_element_located((By.ID, "id")))
except TimeoutException:
    print("Tiempo de espera agotado")

# ============================================================
# CERRAR EL NAVEGADOR
# ============================================================

driver.quit()  # Cierra todas las ventanas y termina el proceso
driver.close()  # Cierra solo la ventana actual

print("Guía de referencia lista para usar!")