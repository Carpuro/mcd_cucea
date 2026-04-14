# 📥 Guía de Instalación de Selenium

## 🖥️ Requisitos del Sistema

Para usar Selenium necesitas:
1. Python 3.x instalado
2. pip (gestor de paquetes de Python)
3. Un navegador web (Chrome, Firefox, Edge, etc.)
4. El driver correspondiente al navegador

---

## 📦 Instalación Paso a Paso

### 1. Instalar Selenium

```bash
pip install selenium
```

---

### 2. Opción A: Instalación Automática del Driver (Recomendado)

La forma más fácil es usar `webdriver-manager` que descarga automáticamente el driver correcto:

```bash
pip install webdriver-manager
```

Luego en tu código:

```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

---

### 2. Opción B: Instalación Manual del Driver

#### Para Chrome:

**Windows:**
1. Descarga ChromeDriver desde: https://chromedriver.chromium.org/
2. Descomprime el archivo
3. Agrega la carpeta al PATH o especifica la ruta en el código

**macOS:**
```bash
brew install chromedriver
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install chromium-chromedriver
```

#### Para Firefox:

**Windows/Mac/Linux:**
1. Descarga geckodriver desde: https://github.com/mozilla/geckodriver/releases
2. Descomprime y agrega al PATH

O con gestores de paquetes:
```bash
# macOS
brew install geckodriver

# Linux
sudo apt-get install firefox-geckodriver
```

---

## 🔧 Verificar Instalación

Crea un archivo `test_selenium.py`:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')

try:
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.google.com")
    print(f"✅ Selenium funciona! Título: {driver.title}")
    driver.quit()
except Exception as e:
    print(f"❌ Error: {e}")
```

Ejecuta:
```bash
python test_selenium.py
```

---

## 🌐 Drivers Disponibles

| Navegador | Driver | URL |
|-----------|--------|-----|
| Chrome | ChromeDriver | https://chromedriver.chromium.org/ |
| Firefox | GeckoDriver | https://github.com/mozilla/geckodriver |
| Edge | EdgeDriver | https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/ |
| Safari | SafariDriver | Incluido en macOS |

---

## 🐛 Solución de Problemas Comunes

### Error: "selenium-manager: 65"
**Problema:** No se puede descargar el driver automáticamente por restricciones de red.

**Solución:**
1. Descarga manualmente el driver
2. Especifica la ruta en el código:

```python
from selenium.webdriver.chrome.service import Service

service = Service('/ruta/a/chromedriver')
driver = webdriver.Chrome(service=service)
```

### Error: "ChromeDriver version mismatch"
**Problema:** La versión del driver no coincide con la del navegador.

**Solución:**
- Usa `webdriver-manager` para actualización automática
- O descarga la versión correcta manualmente

### Error: "Session not created"
**Problema:** Configuración incorrecta del driver.

**Solución:**
```python
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)
```

### Error: "Element not found"
**Problema:** El elemento no está cargado aún.

**Solución:** Usar esperas explícitas:
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
elemento = wait.until(EC.presence_of_element_located((By.ID, "mi-id")))
```

---

## 📚 Paquetes Adicionales Útiles

```bash
# Para testing
pip install pytest pytest-selenium

# Para captura de screenshots
pip install pillow

# Para manejo de datos
pip install pandas

# Para análisis de HTML
pip install beautifulsoup4
```

---

## 🔐 Configuraciones de Seguridad

Para evitar problemas de seguridad en producción:

```python
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
```

---

## 🎯 Configuraciones Comunes

### Modo Headless (sin ventana visual)
```python
chrome_options.add_argument('--headless')
```

### Tamaño de ventana personalizado
```python
chrome_options.add_argument('--window-size=1920,1080')
```

### Deshabilitar imágenes (más rápido)
```python
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
```

### User Agent personalizado
```python
chrome_options.add_argument('user-agent=Mozilla/5.0 ...')
```

---

## 📱 Entornos Especiales

### Docker
```dockerfile
FROM python:3.9

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver

RUN pip install selenium

COPY . /app
WORKDIR /app

CMD ["python", "mi_script.py"]
```

### GitHub Actions
```yaml
- name: Setup Chrome
  uses: browser-actions/setup-chrome@latest

- name: Install dependencies
  run: pip install selenium webdriver-manager
```

---

## 🎓 Recursos de Aprendizaje

- **Documentación oficial:** https://www.selenium.dev/documentation/
- **Python Selenium docs:** https://selenium-python.readthedocs.io/
- **Tutorials:** https://www.selenium.dev/documentation/webdriver/getting_started/

---

## ✅ Checklist de Instalación

- [ ] Python 3.x instalado
- [ ] pip actualizado (`pip install --upgrade pip`)
- [ ] Selenium instalado (`pip install selenium`)
- [ ] webdriver-manager instalado (recomendado)
- [ ] Navegador instalado (Chrome/Firefox)
- [ ] Test de verificación ejecutado con éxito

---

## 📞 Soporte

Si tienes problemas:
1. Verifica las versiones: `pip show selenium`
2. Actualiza pip: `pip install --upgrade pip`
3. Reinstala selenium: `pip uninstall selenium && pip install selenium`
4. Consulta la documentación oficial

---

¡Listo para empezar a automatizar! 🚀