"""
EJEMPLO AVANZADO DE SELENIUM
Demuestra técnicas avanzadas:
- Scraping de datos
- Manejo de múltiples pestañas
- JavaScript execution
- Scroll y elementos dinámicos
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

def ejemplo_avanzado():
    """Ejemplo avanzado con técnicas múltiples"""
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    print(" Iniciando ejemplo avanzado de Selenium...")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # ==========================================
        # 1. EJECUTAR JAVASCRIPT
        # ==========================================
        print("\n 1. Navegando a Wikipedia...")
        driver.get("https://www.wikipedia.org")
        
        # Ejecutar JavaScript para obtener información
        print("\n Ejecutando JavaScript en la página...")
        page_height = driver.execute_script("return document.body.scrollHeight")
        print(f"   Altura de la página: {page_height}px")
        
        num_links = driver.execute_script("return document.querySelectorAll('a').length")
        print(f"   Número de enlaces: {num_links}")
        
        # ==========================================
        # 2. BUSCAR Y EXTRAER DATOS
        # ==========================================
        print("\n 2. Extrayendo datos de la página...")
        
        # Buscar el campo de búsqueda
        search_input = wait.until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_input.send_keys("Selenium (software)")
        
        # Hacer clic en el botón de búsqueda
        search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        search_button.click()
        
        time.sleep(2)
        
        # Extraer el título del artículo
        try:
            article_title = wait.until(
                EC.presence_of_element_located((By.ID, "firstHeading"))
            )
            print(f"   Título del artículo: {article_title.text}")
        except:
            print("   No se pudo encontrar el título")
        
        # ==========================================
        # 3. SCROLL EN LA PÁGINA
        # ==========================================
        print("\n 3. Haciendo scroll en la página...")
        
        # Scroll gradual
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {(i+1)*300})")
            time.sleep(0.5)
            print(f"   Scroll {i+1}/3 completado")
        
        # Scroll al final
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        print("   Scroll al final completado")
        
        # ==========================================
        # 4. TOMAR SCREENSHOT DE PÁGINA COMPLETA
        # ==========================================
        print("\n 4. Tomando screenshot...")
        driver.save_screenshot("C:\\Users\\carlo\\OneDrive\\Documentos\\GitHub\\MCD_Programacion_1\\presentation\\Selenium\\screenshots\\wikipedia_selenium.png")
        print("   Screenshot guardado")
        
        # ==========================================
        # 5. OBTENER INFORMACIÓN DE LA PÁGINA
        # ==========================================
        print("\n 5. Información de la página:")
        print(f"   URL: {driver.current_url}")
        print(f"   Título: {driver.title}")
        
        # Contar párrafos
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        print(f"   Número de párrafos: {len(paragraphs)}")
        
        # ==========================================
        # 6. MANEJO DE COOKIES
        # ==========================================
        print("\n 6. Información de cookies:")
        cookies = driver.get_cookies()
        print(f"   Número de cookies: {len(cookies)}")
        if cookies:
            print(f"   Primera cookie: {cookies[0]['name']}")
        
        # ==========================================
        # 7. INFORMACIÓN DEL NAVEGADOR
        # ==========================================
        print("\n 7. Información del navegador:")
        print(f"   User Agent: {driver.execute_script('return navigator.userAgent')}")
        print(f"   Idioma: {driver.execute_script('return navigator.language')}")
        
        # ==========================================
        # 8. RESUMEN FINAL
        # ==========================================
        print("\n" + "="*50)
        print(" EJEMPLO AVANZADO COMPLETADO EXITOSAMENTE")
        print("="*50)
        print("\nTécnicas demostradas:")
        print("  ✓ Ejecución de JavaScript")
        print("  ✓ Búsqueda y extracción de datos")
        print("  ✓ Scroll automático")
        print("  ✓ Captura de screenshots")
        print("  ✓ Manejo de cookies")
        print("  ✓ Información del navegador")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n🔚 Cerrando navegador...")
        driver.quit()

if __name__ == "__main__":
    ejemplo_avanzado()