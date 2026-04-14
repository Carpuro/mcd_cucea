"""
EJEMPLO BÁSICO DE SELENIUM
Muestra cómo automatizar una búsqueda en Google
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

def ejemplo_basico():
    """Ejemplo básico: búsqueda en Google"""
    
    # Configurar opciones del navegador
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Ejecutar sin interfaz gráfica
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    print(" Iniciando navegador Chrome...")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 1. Navegar a Google
        print("\n Navegando a Google...")
        driver.get("https://www.google.com")
        print(f"   Título de la página: {driver.title}")
        
        # 2. Encontrar el campo de búsqueda
        print("\n Buscando el campo de búsqueda...")
        search_box = driver.find_element(By.NAME, "q")
        
        # 3. Escribir en el campo de búsqueda
        print("   Escribiendo 'Selenium WebDriver'...")
        search_box.send_keys("Selenium WebDriver")
        
        # 4. Presionar Enter
        print("   Presionando Enter...")
        search_box.send_keys(Keys.RETURN)
        
        # 5. Esperar a que cargue la página
        time.sleep(2)
        
        # 6. Obtener el título de la página de resultados
        print(f"\n Búsqueda completada!")
        print(f"   Título de resultados: {driver.title}")
        print(f"   URL actual: {driver.current_url}")
        
    except Exception as e:
        print(f"\n Error: {e}")
    
    finally:
        # Cerrar el navegador
        print("\n Cerrando navegador...")
        driver.quit()

if __name__ == "__main__":
    ejemplo_basico()