"""
EJEMPLO INTERMEDIO DE SELENIUM
Demuestra:
- Llenar formularios
- Esperas explícitas
- Manejo de elementos
- Captura de screenshots
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time

def ejemplo_intermedio():
    """Ejemplo intermedio: interacción con formularios y esperas"""
    
    # Configurar opciones
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    print(" Iniciando navegador...")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)  # Espera máxima de 10 segundos
    
    try:
        # Navegar a una página de práctica
        print("\n Navegando a página de ejemplo...")
        driver.get("https://www.selenium.dev/selenium/web/web-form.html")
        
        print(f"   Título: {driver.title}")
        
        # 1. Llenar campo de texto
        print("\n Llenando formulario...")
        text_input = wait.until(
            EC.presence_of_element_located((By.ID, "my-text-id"))
        )
        text_input.send_keys("¡Hola desde Selenium!")
        print("   ✓ Campo de texto llenado")
        
        # 2. Llenar campo de contraseña
        password_input = driver.find_element(By.NAME, "my-password")
        password_input.send_keys("password123")
        print("   ✓ Campo de contraseña llenado")
        
        # 3. Llenar campo de textarea
        textarea = driver.find_element(By.NAME, "my-textarea")
        textarea.send_keys("Este es un ejemplo de Selenium WebDriver para mi clase de programación.")
        print("   ✓ Textarea llenado")
        
        # 4. Seleccionar de dropdown
        dropdown = driver.find_element(By.NAME, "my-select")
        dropdown.click()
        time.sleep(0.5)
        option = driver.find_element(By.CSS_SELECTOR, "option[value='2']")
        option.click()
        print("   ✓ Opción de dropdown seleccionada")
        
        # 5. Marcar checkbox
        checkbox = driver.find_element(By.ID, "my-check-2")
        checkbox.click()
        print("   ✓ Checkbox marcado")
        
        # 6. Seleccionar radio button
        radio = driver.find_element(By.ID, "my-radio-2")
        radio.click()
        print("   ✓ Radio button seleccionado")
        
        # 7. Tomar screenshot antes de enviar
        print("\n Tomando screenshot...")
        driver.save_screenshot("C:\\Users\\carlo\\OneDrive\\Documentos\\GitHub\\MCD_Programacion_1\\presentation\\Selenium\\screenshots\\formulario_antes.png")
        print("   ✓ Screenshot guardado")
        
        # 8. Hacer clic en el botón de submit
        print("\n Haciendo clic en Submit...")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # 9. Esperar a que aparezca el mensaje de confirmación
        try:
            success_message = wait.until(
                EC.presence_of_element_located((By.ID, "message"))
            )
            print(f"\n Formulario enviado exitosamente!")
            print(f"   Mensaje: {success_message.text}")
            
            # Tomar screenshot después de enviar
            driver.save_screenshot("/mnt/user-data/outputs/formulario_despues.png")
            
        except TimeoutException:
            print("\n  No se encontró el mensaje de confirmación")
        
        # 10. Información adicional
        print(f"\n Información de la página:")
        print(f"   URL actual: {driver.current_url}")
        print(f"   Dimensiones de ventana: {driver.get_window_size()}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        driver.save_screenshot("/mnt/user-data/outputs/error.png")
    
    finally:
        print("\n Cerrando navegador...")
        driver.quit()

if __name__ == "__main__":
    ejemplo_intermedio()