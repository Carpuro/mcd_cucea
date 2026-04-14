"""
CASOS DE USO PRÁCTICOS DE SELENIUM
Ejemplos reales de automatización web
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv

# ============================================================
# CASO 1: AUTOMATIZAR LOGIN EN UN SITIO WEB
# ============================================================

def caso_login():
    """
    Automatiza el proceso de login en un sitio web
    Útil para: Testing, automatización de tareas, scraping autenticado
    """
    print("\n" + "="*60)
    print("CASO 1: AUTOMATIZAR LOGIN")
    print("="*60)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Navegar a la página de login
        driver.get("https://practicetestautomation.com/practice-test-login/")
        print("✓ Página de login cargada")
        
        # Esperar a que la página cargue completamente
        time.sleep(1)
        
        # Encontrar campos de usuario y contraseña - esperar que sean clickeables
        username_field = wait.until(
            EC.element_to_be_clickable((By.ID, "username"))
        )
        password_field = wait.until(
            EC.element_to_be_clickable((By.ID, "password"))
        )
        
        # Ingresar credenciales
        username_field.clear()
        username_field.send_keys("student")
        password_field.clear()
        password_field.send_keys("Password123")
        print("✓ Credenciales ingresadas")
        
        # Esperar y hacer clic en submit - usar JavaScript si falla el clic normal
        submit_button = wait.until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        
        try:
            submit_button.click()
        except:
            # Si el clic normal falla, usar JavaScript
            driver.execute_script("arguments[0].click();", submit_button)
        
        print("✓ Formulario enviado")
        
        # Verificar login exitoso
        try:
            success_message = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "post-title"))
            )
            print(f"✅ Login exitoso! Mensaje: {success_message.text}")
        except TimeoutException:
            print("❌ Login fallido")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()


# ============================================================
# CASO 2: WEB SCRAPING DE PRODUCTOS
# ============================================================

def caso_scraping_productos():
    """
    Extrae información de productos de un sitio web
    Útil para: Comparación de precios, análisis de mercado, monitoreo
    """
    print("\n" + "="*60)
    print("CASO 2: WEB SCRAPING DE PRODUCTOS")
    print("="*60)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navegar a una página de productos de ejemplo
        driver.get("https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops")
        print("✓ Página de productos cargada")
        
        time.sleep(2)  # Esperar que cargue completamente
        
        # Encontrar todos los productos
        productos = driver.find_elements(By.CLASS_NAME, "card")
        print(f"✓ Se encontraron {len(productos)} productos")
        
        # Extraer información de cada producto
        datos_productos = []
        
        for i, producto in enumerate(productos[:5], 1):  # Solo primeros 5
            try:
                nombre = producto.find_element(By.CLASS_NAME, "title").text
                precio = producto.find_element(By.CLASS_NAME, "price").text
                descripcion = producto.find_element(By.CLASS_NAME, "description").text
                
                datos_productos.append({
                    'nombre': nombre,
                    'precio': precio,
                    'descripcion': descripcion
                })
                
                print(f"\n  Producto {i}:")
                print(f"    Nombre: {nombre}")
                print(f"    Precio: {precio}")
                print(f"    Descripción: {descripcion[:50]}...")
                
            except NoSuchElementException:
                print(f"  ⚠️  No se pudo extraer info del producto {i}")
        
        # Guardar en CSV (simulado)
        print(f"\n✅ Se extrajeron {len(datos_productos)} productos exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()


# ============================================================
# CASO 3: LLENAR FORMULARIO COMPLEJO
# ============================================================

def caso_formulario_complejo():
    """
    Automatiza el llenado de un formulario complejo
    Útil para: Testing de formularios, entrada de datos masiva
    """
    print("\n" + "="*60)
    print("CASO 3: LLENAR FORMULARIO COMPLEJO")
    print("="*60)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Navegar al formulario
        driver.get("https://www.selenium.dev/selenium/web/web-form.html")
        print("✓ Formulario cargado")
        
        time.sleep(1)  # Pequeña espera para asegurar carga completa
        
        # Datos del formulario
        datos_formulario = {
            'texto': 'Carlos Pulido Rosas',
            'password': 'MiPassword123!',
            'textarea': 'Este es un ejemplo de automatización de formularios con Selenium.',
            'dropdown': '2',
            'datalist': 'San Francisco'
        }
        
        # Llenar campo de texto
        campo_texto = wait.until(
            EC.element_to_be_clickable((By.ID, "my-text-id"))
        )
        campo_texto.clear()
        campo_texto.send_keys(datos_formulario['texto'])
        print(f"✓ Campo texto: {datos_formulario['texto']}")
        
        # Llenar password
        campo_password = wait.until(
            EC.element_to_be_clickable((By.NAME, "my-password"))
        )
        campo_password.send_keys(datos_formulario['password'])
        print("✓ Campo password llenado")
        
        # Llenar textarea
        campo_textarea = wait.until(
            EC.element_to_be_clickable((By.NAME, "my-textarea"))
        )
        campo_textarea.send_keys(datos_formulario['textarea'])
        print("✓ Textarea llenado")
        
        # Seleccionar del dropdown usando JavaScript para mayor confiabilidad
        dropdown = driver.find_element(By.NAME, "my-select")
        driver.execute_script("arguments[0].value = arguments[1];", dropdown, datos_formulario['dropdown'])
        print("✓ Dropdown seleccionado")
        
        # Marcar checkboxes usando JavaScript
        checkbox1 = driver.find_element(By.ID, "my-check-1")
        if not checkbox1.is_selected():
            driver.execute_script("arguments[0].click();", checkbox1)
            
        checkbox2 = driver.find_element(By.ID, "my-check-2")
        if not checkbox2.is_selected():
            driver.execute_script("arguments[0].click();", checkbox2)
        print("✓ Checkboxes marcados")
        
        # Seleccionar radio button usando JavaScript
        radio = driver.find_element(By.ID, "my-radio-2")
        driver.execute_script("arguments[0].click();", radio)
        print("✓ Radio button seleccionado")
        
        # Tomar screenshot del formulario llenado
        driver.save_screenshot("/mnt/user-data/outputs/formulario_llenado.png")
        print("✓ Screenshot guardado")
        
        # Enviar formulario usando JavaScript para evitar interceptores
        submit_button = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
        )
        driver.execute_script("arguments[0].click();", submit_button)
        print("✓ Formulario enviado")
        
        # Verificar envío exitoso
        time.sleep(1)
        try:
            mensaje = wait.until(
                EC.presence_of_element_located((By.ID, "message"))
            )
            print(f"\n✅ Formulario procesado exitosamente!")
            print(f"   Mensaje: {mensaje.text}")
        except (NoSuchElementException, TimeoutException):
            print("⚠️  No se encontró mensaje de confirmación")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()


# ============================================================
# CASO 4: MONITOREO DE PRECIOS
# ============================================================

def caso_monitoreo_precios():
    """
    Monitorea el precio de un producto en un sitio web
    Útil para: Alertas de precio, comparación de precios, análisis de tendencias
    """
    print("\n" + "="*60)
    print("CASO 4: MONITOREO DE PRECIOS")
    print("="*60)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navegar al sitio de e-commerce
        driver.get("https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops")
        print("✓ Página cargada")
        
        time.sleep(2)
        
        # Buscar productos con sus precios
        productos = driver.find_elements(By.CLASS_NAME, "card")
        
        print(f"\n📊 REPORTE DE PRECIOS")
        print("-" * 60)
        
        precios_productos = []
        
        for producto in productos[:5]:
            try:
                nombre = producto.find_element(By.CLASS_NAME, "title").text
                precio_texto = producto.find_element(By.CLASS_NAME, "price").text
                
                # Extraer el número del precio
                precio_numerico = float(precio_texto.replace('$', '').replace(',', ''))
                
                precios_productos.append({
                    'nombre': nombre,
                    'precio': precio_numerico
                })
                
                print(f"\n{nombre}")
                print(f"  Precio actual: ${precio_numerico:.2f}")
                
            except Exception as e:
                print(f"  ⚠️  Error extrayendo precio: {e}")
        
        # Análisis de precios
        if precios_productos:
            precios = [p['precio'] for p in precios_productos]
            precio_promedio = sum(precios) / len(precios)
            precio_max = max(precios)
            precio_min = min(precios)
            
            print("\n" + "="*60)
            print("ANÁLISIS DE PRECIOS")
            print(f"  Precio promedio: ${precio_promedio:.2f}")
            print(f"  Precio más alto: ${precio_max:.2f}")
            print(f"  Precio más bajo: ${precio_min:.2f}")
            print("="*60)
            
            # Encontrar mejor oferta
            mejor_oferta = min(precios_productos, key=lambda x: x['precio'])
            print(f"\n💰 MEJOR OFERTA:")
            print(f"  {mejor_oferta['nombre']}")
            print(f"  Precio: ${mejor_oferta['precio']:.2f}")
        
        print("\n✅ Monitoreo completado!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()


# ============================================================
# CASO 5: TESTING AUTOMATIZADO
# ============================================================

def caso_testing_automatizado():
    """
    Realiza pruebas automatizadas de una página web
    Útil para: QA, testing de regresión, validación de funcionalidad
    """
    print("\n" + "="*60)
    print("CASO 5: TESTING AUTOMATIZADO")
    print("="*60)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        # Test 1: Verificar que la página carga
        print("\n🧪 Test 1: Verificar carga de página")
        try:
            driver.get("https://www.selenium.dev/selenium/web/web-form.html")
            assert "Web form" in driver.title
            print("   ✅ PASS - Página cargada correctamente")
            tests_passed += 1
        except AssertionError:
            print("   ❌ FAIL - Título incorrecto")
            tests_failed += 1
        
        # Test 2: Verificar que el campo de texto existe
        print("\n🧪 Test 2: Verificar existencia de campo de texto")
        try:
            campo_texto = driver.find_element(By.ID, "my-text-id")
            assert campo_texto.is_displayed()
            print("   ✅ PASS - Campo de texto visible")
            tests_passed += 1
        except (NoSuchElementException, AssertionError):
            print("   ❌ FAIL - Campo de texto no encontrado")
            tests_failed += 1
        
        # Test 3: Verificar que se puede escribir en el campo
        print("\n🧪 Test 3: Verificar funcionalidad de escritura")
        try:
            campo_texto = driver.find_element(By.ID, "my-text-id")
            texto_prueba = "Test de Selenium"
            campo_texto.send_keys(texto_prueba)
            valor = campo_texto.get_attribute("value")
            assert valor == texto_prueba
            print("   ✅ PASS - Se puede escribir correctamente")
            tests_passed += 1
        except AssertionError:
            print("   ❌ FAIL - Error al escribir")
            tests_failed += 1
        
        # Test 4: Verificar que el botón submit funciona
        print("\n🧪 Test 4: Verificar funcionalidad del botón submit")
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Esperar mensaje de confirmación
            mensaje = wait.until(
                EC.presence_of_element_located((By.ID, "message"))
            )
            assert mensaje.is_displayed()
            print("   ✅ PASS - Submit funciona correctamente")
            tests_passed += 1
        except (NoSuchElementException, TimeoutException, AssertionError):
            print("   ❌ FAIL - Error en submit")
            tests_failed += 1
        
        # Test 5: Verificar URL después de submit
        print("\n🧪 Test 5: Verificar cambio de URL")
        try:
            assert "submitted" in driver.current_url.lower()
            print("   ✅ PASS - URL cambió correctamente")
            tests_passed += 1
        except AssertionError:
            print("   ❌ FAIL - URL no cambió como esperado")
            tests_failed += 1
        
        # Reporte final
        print("\n" + "="*60)
        print("REPORTE FINAL DE TESTS")
        print("="*60)
        print(f"Tests ejecutados: {tests_passed + tests_failed}")
        print(f"Tests exitosos: {tests_passed} ✅")
        print(f"Tests fallidos: {tests_failed} ❌")
        
        porcentaje = (tests_passed / (tests_passed + tests_failed)) * 100
        print(f"Tasa de éxito: {porcentaje:.1f}%")
        
        if tests_failed == 0:
            print("\n🎉 ¡Todos los tests pasaron!")
        else:
            print(f"\n⚠️  {tests_failed} test(s) fallaron")
        
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
    finally:
        driver.quit()


# ============================================================
# EJECUTAR TODOS LOS CASOS
# ============================================================

def ejecutar_todos_casos():
    """Ejecuta todos los casos de uso"""
    print("\n" + "="*60)
    print("EJEMPLOS PRÁCTICOS DE SELENIUM")
    print("Demostrando casos de uso reales")
    print("="*60)
    
    casos = [
        ("Login Automatizado", caso_login),
        ("Web Scraping de Productos", caso_scraping_productos),
        ("Formulario Complejo", caso_formulario_complejo),
        ("Monitoreo de Precios", caso_monitoreo_precios),
        ("Testing Automatizado", caso_testing_automatizado)
    ]
    
    print("\n📋 CASOS DISPONIBLES:")
    for i, (nombre, _) in enumerate(casos, 1):
        print(f"  {i}. {nombre}")
    
    print("\n" + "="*60)
    print("Ejecutando casos...")
    print("="*60)
    
    for nombre, funcion in casos:
        try:
            funcion()
            time.sleep(1)
        except Exception as e:
            print(f"\n❌ Error en {nombre}: {e}")
    
    print("\n" + "="*60)
    print("✅ TODOS LOS CASOS COMPLETADOS")
    print("="*60)


if __name__ == "__main__":
    # Puedes ejecutar un caso específico o todos
    
    # Ejecutar caso individual:
    # caso_login()
    # caso_scraping_productos()
    # caso_formulario_complejo()
    # caso_monitoreo_precios()
    # caso_testing_automatizado()
    
    # O ejecutar todos:
    ejecutar_todos_casos()