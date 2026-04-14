# 🎓 Ejemplos de Selenium para Clase de Programación

Este repositorio contiene ejemplos prácticos de **Selenium WebDriver** en Python, organizados por nivel de dificultad.

## 📋 Contenido

### 1. **ejemplo_basico_selenium.py**
Introducción a Selenium con un ejemplo simple de búsqueda en Google.

**Conceptos que cubre:**
- Configuración básica del driver
- Navegación a una página web
- Localizar elementos (By.NAME)
- Enviar texto a campos de entrada
- Simular presionar teclas (Enter)
- Obtener información de la página

**Ideal para:** Principiantes que recién empiezan con Selenium

---

### 2. **ejemplo_intermedio_selenium.py**
Interacción con formularios y esperas explícitas.

**Conceptos que cubre:**
- Esperas explícitas (WebDriverWait)
- Llenar múltiples tipos de campos (texto, password, textarea)
- Interactuar con dropdowns
- Marcar checkboxes y radio buttons
- Tomar screenshots
- Manejo de excepciones (TimeoutException)

**Ideal para:** Estudiantes con conocimientos básicos que quieren practicar formularios

---

### 3. **ejemplo_avanzado_selenium.py**
Técnicas avanzadas de web scraping y automatización.

**Conceptos que cubre:**
- Ejecución de JavaScript
- Extracción de datos de páginas web
- Scroll automático
- Manejo de cookies
- Obtención de información del navegador
- Técnicas de scraping

**Ideal para:** Estudiantes avanzados que quieren dominar Selenium

---

### 4. **guia_referencia_selenium.py**
Guía completa de referencia rápida con todos los comandos y técnicas comunes.

**Incluye:**
- Navegación
- Localización de elementos (todos los métodos)
- Interacción con elementos
- Esperas (implícitas y explícitas)
- Acciones avanzadas
- JavaScript
- Ventanas y pestañas
- Frames e iframes
- Alertas
- Cookies
- Screenshots
- Select/Dropdowns
- Manejo de errores

**Ideal para:** Referencia rápida durante el desarrollo

---

## 🚀 Requisitos

```bash
pip install selenium
```

**Nota:** Se necesita tener Chrome instalado en el sistema.

---

## 💻 Cómo Usar

### Ejecutar un ejemplo:

```bash
python ejemplo_basico_selenium.py
```

```bash
python ejemplo_intermedio_selenium.py
```

```bash
python ejemplo_avanzado_selenium.py
```

---

## 🎯 Estructura de los Ejemplos

Todos los ejemplos siguen una estructura similar:

1. **Importaciones** necesarias
2. **Configuración** del driver con opciones
3. **Bloque try-except-finally** para manejo seguro
4. **Acciones** específicas del ejemplo
5. **Mensajes informativos** con emojis para mejor comprensión
6. **Cierre adecuado** del navegador

---

## 📚 Conceptos Clave

### Localizadores (By)
```python
By.ID            # Por ID del elemento
By.NAME          # Por atributo name
By.CLASS_NAME    # Por clase CSS
By.CSS_SELECTOR  # Por selector CSS
By.XPATH         # Por expresión XPath
By.TAG_NAME      # Por etiqueta HTML
By.LINK_TEXT     # Por texto exacto del enlace
By.PARTIAL_LINK_TEXT  # Por texto parcial del enlace
```

### Esperas
```python
# Espera implícita (no recomendada)
time.sleep(2)

# Espera explícita (recomendada)
wait = WebDriverWait(driver, 10)
elemento = wait.until(
    EC.presence_of_element_located((By.ID, "id"))
)
```

### Opciones del Chrome
```python
chrome_options = Options()
chrome_options.add_argument('--headless')  # Sin interfaz gráfica
chrome_options.add_argument('--window-size=1920,1080')  # Tamaño ventana
chrome_options.add_argument('--disable-gpu')  # Deshabilitar GPU
```

---

## ⚠️ Buenas Prácticas

1. **Siempre usar try-finally** para cerrar el navegador
2. **Preferir esperas explícitas** sobre `time.sleep()`
3. **Usar selectores CSS o ID** cuando sea posible (más rápidos que XPath)
4. **Manejar excepciones** apropiadamente
5. **Cerrar el navegador** con `driver.quit()`
6. **Usar modo headless** para ejecución más rápida en producción

---

## 🔧 Solución de Problemas Comunes

### Error: "ChromeDriver not found"
```bash
# Instalar webdriver-manager
pip install webdriver-manager

# Usar en el código:
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
```

### Error: "Element not interactable"
- Usar esperas explícitas
- Verificar que el elemento esté visible
- Intentar scroll al elemento

### Error: "NoSuchElementException"
- Verificar el selector
- Usar esperas
- Comprobar que el elemento existe en la página

---

## 📖 Recursos Adicionales

- [Documentación oficial de Selenium](https://www.selenium.dev/documentation/)
- [Selenium con Python](https://selenium-python.readthedocs.io/)
- [Expected Conditions](https://selenium-python.readthedocs.io/waits.html)

---

## 🎓 Ejercicios Sugeridos

1. **Básico:** Modificar el ejemplo básico para buscar otros términos
2. **Intermedio:** Crear un script que llene un formulario de registro
3. **Avanzado:** Hacer un scraper que extraiga datos de múltiples páginas
4. **Desafío:** Automatizar login en un sitio y realizar acciones

---

## 📝 Notas para la Clase

- Todos los ejemplos incluyen comentarios explicativos
- Los mensajes usan emojis para facilitar el seguimiento
- Los ejemplos son progresivos en dificultad
- Se incluye manejo de errores en todos los casos
- Los screenshots se guardan para verificación visual

---

## 👨‍💻 Autor

Carlos Pulido Rosas - Clase de Programación 1 - Maestria en Ciencia de los Datos

---

## 📄 Licencia

Estos ejemplos son de uso libre para fines educativos.