# 📝 Ejercicios Prácticos de Selenium

## 🎯 Objetivo
Estos ejercicios te ayudarán a practicar y dominar Selenium WebDriver paso a paso.

---

## 📚 NIVEL PRINCIPIANTE

### Ejercicio 1: Tu Primera Búsqueda
**Objetivo:** Familiarizarte con la sintaxis básica de Selenium

**Tareas:**
1. Abre el navegador Chrome
2. Navega a https://www.bing.com
3. Busca "Python programming"
4. Imprime el título de la página de resultados
5. Cierra el navegador

**Pista:** Usa `driver.find_element(By.NAME, "q")` para encontrar el campo de búsqueda.

---

### Ejercicio 2: Navegar entre Páginas
**Objetivo:** Practicar navegación básica

**Tareas:**
1. Navega a https://www.wikipedia.org
2. Haz clic en el enlace "English" 
3. Espera 2 segundos
4. Usa `driver.back()` para volver
5. Imprime la URL actual
6. Usa `driver.forward()` para ir adelante de nuevo

---

### Ejercicio 3: Extraer Información
**Objetivo:** Aprender a extraer texto de elementos

**Tareas:**
1. Navega a https://www.selenium.dev
2. Encuentra el título principal (h1) de la página
3. Imprime el texto del título
4. Encuentra todos los enlaces de navegación
5. Imprime cuántos enlaces hay

**Pista:** Usa `find_elements()` para obtener múltiples elementos.

---

## 🎓 NIVEL INTERMEDIO

### Ejercicio 4: Formulario de Registro
**Objetivo:** Practicar llenado de formularios

**Tareas:**
1. Navega a https://www.selenium.dev/selenium/web/web-form.html
2. Llena TODOS los campos del formulario con datos de prueba
3. Selecciona opciones de los dropdowns
4. Marca los checkboxes
5. Selecciona un radio button
6. Toma un screenshot antes de enviar
7. Haz clic en Submit
8. Verifica que aparezca el mensaje de confirmación

**Bonus:** Guarda el screenshot con un nombre descriptivo que incluya la fecha.

---

### Ejercicio 5: Esperas Inteligentes
**Objetivo:** Dominar las esperas explícitas

**Tareas:**
1. Navega a https://www.selenium.dev/selenium/web/web-form.html
2. Usa `WebDriverWait` para esperar que el campo de texto esté presente
3. Usa `WebDriverWait` para esperar que el botón submit sea clickeable
4. Haz clic en el botón
5. Espera a que aparezca el mensaje de confirmación usando `WebDriverWait`

**Objetivo:** No usar `time.sleep()` en ninguna parte.

---

### Ejercicio 6: Mini Web Scraper
**Objetivo:** Extraer datos estructurados

**Tareas:**
1. Navega a https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets
2. Extrae el nombre y precio de los primeros 5 productos
3. Guarda los datos en un diccionario
4. Imprime los datos en formato de tabla
5. Calcula el precio promedio

**Bonus:** Guarda los datos en un archivo CSV.

---

## 🚀 NIVEL AVANZADO

### Ejercicio 7: Automatización de Login
**Objetivo:** Implementar un flujo completo de autenticación

**Tareas:**
1. Navega a https://practicetestautomation.com/practice-test-login/
2. Implementa una función `login(username, password)` que:
   - Llene los campos de usuario y contraseña
   - Haga clic en submit
   - Verifique si el login fue exitoso
   - Retorne `True` si fue exitoso, `False` si falló
3. Prueba con credenciales correctas: username="student", password="Password123"
4. Prueba con credenciales incorrectas
5. Imprime mensajes apropiados en cada caso

---

### Ejercicio 8: Scraper con Paginación
**Objetivo:** Navegar múltiples páginas y extraer datos

**Tareas:**
1. Navega a https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops
2. Extrae información de productos de la primera página
3. Busca si hay un botón "Next" o "Siguiente"
4. Si existe, navega a la siguiente página
5. Extrae información de esa página también
6. Combina todos los datos
7. Genera un reporte con:
   - Total de productos encontrados
   - Rango de precios
   - Producto más caro
   - Producto más barato

---

### Ejercicio 9: Testing Suite
**Objetivo:** Crear una suite de tests automatizados

**Tareas:**
Crea al menos 5 tests para https://www.selenium.dev/selenium/web/web-form.html:

1. Test que verifique que la página carga correctamente
2. Test que verifique que todos los campos están presentes
3. Test que verifique que se puede escribir en los campos de texto
4. Test que verifique que el formulario se puede enviar
5. Test que verifique que aparece el mensaje de confirmación

**Formato esperado:**
```python
def test_pagina_carga():
    # Tu código aquí
    assert condicion, "Mensaje de error"
    
def test_campos_presentes():
    # Tu código aquí
    pass
    
# etc...
```

---

### Ejercicio 10: Bot de Monitoreo
**Objetivo:** Crear un script que monitoree cambios en una página

**Tareas:**
1. Crea una función que visite https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops
2. Extrae los precios de todos los productos
3. Guarda los precios en un archivo JSON con timestamp
4. La función debe:
   - Detectar si algún precio cambió desde la última ejecución
   - Notificar (imprimir) si hay cambios
   - Actualizar el archivo con los nuevos precios

**Bonus:** Implementa un sistema de alertas cuando el precio baje más de 10%.

---

## 🎨 PROYECTOS FINALES

### Proyecto 1: Buscador de Noticias
**Descripción:** Crea un script que:
- Busque noticias sobre un tema específico en Google News
- Extraiga los títulos y enlaces de las primeras 10 noticias
- Guarde los resultados en un archivo HTML legible
- Incluya la fecha y hora de la búsqueda

**Tecnologías:** Selenium + HTML generation

---

### Proyecto 2: Comparador de Precios
**Descripción:** Crea un script que:
- Busque un producto en múltiples sitios de e-commerce
- Extraiga nombre, precio, y disponibilidad
- Compare los precios
- Genere un reporte con la mejor oferta
- Guarde los datos en un archivo CSV

**Tecnologías:** Selenium + CSV + Análisis de datos

---

### Proyecto 3: Testing Automatizado
**Descripción:** Crea una suite completa de tests para un sitio web que incluya:
- Tests de funcionalidad básica
- Tests de formularios
- Tests de navegación
- Tests de validación de datos
- Generación de reporte de resultados

**Tecnologías:** Selenium + pytest + Reportes HTML

---

## 💡 TIPS PARA LOS EJERCICIOS

### Antes de Empezar
1. ✅ Lee el ejercicio completo antes de codificar
2. ✅ Planifica tu solución (puedes escribir pseudocódigo)
3. ✅ Identifica qué selectores necesitarás usar
4. ✅ Revisa los ejemplos proporcionados si te atoras

### Durante el Desarrollo
1. ✅ Usa print() para depurar y ver qué está pasando
2. ✅ Toma screenshots en puntos clave
3. ✅ Comenta tu código para explicar qué hace cada parte
4. ✅ Prueba tu código frecuentemente

### Buenas Prácticas
1. ✅ Siempre usa try-except-finally
2. ✅ Cierra el navegador aunque haya errores
3. ✅ Usa esperas explícitas en lugar de time.sleep()
4. ✅ Nombra tus variables descriptivamente
5. ✅ Modulariza: crea funciones para tareas repetitivas

---

## 🐛 Debugging Común

### "NoSuchElementException"
**Problema:** El elemento no existe o el selector es incorrecto

**Soluciones:**
- Verifica el selector en el navegador (F12)
- Usa esperas explícitas
- Asegúrate de que el elemento esté en un frame/iframe

---

### "ElementNotInteractableException"
**Problema:** El elemento existe pero no se puede interactuar con él

**Soluciones:**
- Verifica que el elemento esté visible (`is_displayed()`)
- Haz scroll al elemento
- Espera a que sea clickeable con `WebDriverWait`

---

### "TimeoutException"
**Problema:** El elemento no apareció en el tiempo esperado

**Soluciones:**
- Aumenta el tiempo de espera
- Verifica que el selector sea correcto
- Asegúrate de que la página cargue completamente

---

## 📊 Sistema de Evaluación

Para cada ejercicio, evalúa tu código según:

| Criterio | Descripción | Puntos |
|----------|-------------|---------|
| ✅ Funcionalidad | ¿El código hace lo que se pide? | 40% |
| 🎨 Código limpio | ¿Es legible y está bien organizado? | 20% |
| 🛡️ Manejo de errores | ¿Maneja errores apropiadamente? | 20% |
| 📝 Documentación | ¿Tiene comentarios útiles? | 10% |
| 🚀 Eficiencia | ¿Usa buenas prácticas de Selenium? | 10% |

---

## 🎯 Objetivos de Aprendizaje

Al completar estos ejercicios, deberías poder:

✅ Configurar y usar Selenium WebDriver  
✅ Localizar elementos usando diferentes estrategias  
✅ Interactuar con formularios y elementos web  
✅ Implementar esperas apropiadas  
✅ Extraer datos de páginas web  
✅ Manejar errores y excepciones  
✅ Tomar screenshots y generar reportes  
✅ Crear scripts de automatización útiles  
✅ Implementar tests automatizados básicos  

---

## 📚 Recursos de Ayuda

- Guía de referencia: `guia_referencia_selenium.py`
- Ejemplos básicos: `ejemplo_basico_selenium.py`
- Ejemplos intermedios: `ejemplo_intermedio_selenium.py`
- Ejemplos avanzados: `ejemplo_avanzado_selenium.py`
- Casos de uso: `casos_uso_practicos.py`

---

## 🏆 Desafíos Bonus

1. **Modo Ninja:** Completa un ejercicio usando solo 20 líneas de código
2. **Velocista:** Optimiza un ejercicio para que se ejecute en menos de 5 segundos
3. **Documentador:** Agrega docstrings completos a todas tus funciones
4. **Error Hunter:** Implementa manejo de al menos 3 tipos diferentes de excepciones
5. **Generalista:** Crea una versión de un ejercicio que funcione con Firefox y Chrome

---

¡Buena suerte con los ejercicios! 🚀

Recuerda: La práctica hace al maestro. No te desanimes si algo no funciona a la primera, ¡sigue intentando! 💪