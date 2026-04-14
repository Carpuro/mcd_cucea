import requests
from bs4 import BeautifulSoup

print("="*70)
print("EJERCICIO: WEB SCRAPING - GeeksforGeeks")
print("="*70)

# URL de la página
url = "https://www.geeksforgeeks.org/"

print(f"\nObteniendo página: {url}")
print("-"*70)

# 1. Obtener el código HTML de la página
print("\n1. Obteniendo código HTML...")

try:
    # Hacer la petición HTTP
    response = requests.get(url)
    response.raise_for_status()  # Verificar que no haya errores
    
    # Obtener el código HTML
    html_code = response.text
    
    print(f"✓ Código HTML obtenido exitosamente")
    print(f"✓ Tamaño del HTML: {len(html_code)} caracteres")
    
    # Mostrar primeros 500 caracteres
    print("\nPrimeros 500 caracteres del HTML:")
    print("-"*70)
    print(html_code[:500])
    print("...")
    print("-"*70)
    
except Exception as e:
    print(f"✗ Error al obtener la página: {e}")
    exit()

# 2. Encontrar todas las etiquetas que contengan la palabra "link"
print("\n2. Buscando etiquetas que contengan 'link'...")
print("-"*70)

# Parsear el HTML con BeautifulSoup
soup = BeautifulSoup(html_code, 'html.parser')

# Buscar todas las etiquetas que contengan "link" en su nombre
etiquetas_link = soup.find_all(lambda tag: 'link' in tag.name.lower())

print(f"✓ Encontradas {len(etiquetas_link)} etiquetas con 'link' en su nombre")
print("\nPrimeras 10 etiquetas encontradas:")
print("-"*70)

for i, etiqueta in enumerate(etiquetas_link[:10], 1):
    # Mostrar la etiqueta completa (limitada a 100 caracteres)
    etiqueta_str = str(etiqueta)[:100]
    print(f"{i}. {etiqueta_str}{'...' if len(str(etiqueta)) > 100 else ''}")

# También buscar etiquetas <a> que son links
enlaces = soup.find_all('a')
print(f"\n✓ Encontrados {len(enlaces)} enlaces (<a> tags)")

# Mostrar algunos ejemplos de enlaces
print("\nPrimeros 5 enlaces:")
print("-"*70)
for i, enlace in enumerate(enlaces[:5], 1):
    href = enlace.get('href', 'Sin href')
    texto = enlace.get_text(strip=True)[:50]
    print(f"{i}. Texto: '{texto}' → URL: {href}")

# 3. Desplegar todo el texto sin etiquetas
print("\n" + "="*70)
print("3. Texto de la página (sin etiquetas HTML)")
print("="*70)

# Obtener todo el texto sin etiquetas HTML
texto_completo = soup.get_text()

# Limpiar el texto (eliminar espacios en blanco excesivos)
lineas = texto_completo.split('\n')
lineas_limpias = [linea.strip() for linea in lineas if linea.strip()]
texto_limpio = '\n'.join(lineas_limpias)

print(f"\n✓ Texto extraído: {len(texto_limpio)} caracteres")
print(f"✓ Líneas de texto: {len(lineas_limpias)}")

print("\nPrimeros 2000 caracteres del texto:")
print("-"*70)
print(texto_limpio[:2000])
print("\n...")
print("-"*70)

# Guardar el texto completo en un archivo
nombre_archivo = "geeksforgeeks_texto.txt"
with open(nombre_archivo, 'w', encoding='utf-8') as f:
    f.write(texto_limpio)

print(f"\n✓ Texto completo guardado en: '{nombre_archivo}'")

# Estadísticas adicionales
print("\n" + "="*70)
print("ESTADÍSTICAS")
print("="*70)

# Contar palabras
palabras = texto_limpio.split()
print(f"Total de palabras: {len(palabras)}")

# Contar diferentes tipos de etiquetas
print(f"\nTipos de etiquetas en la página:")
etiquetas_todas = soup.find_all()
tipos_etiquetas = {}
for etiqueta in etiquetas_todas:
    nombre = etiqueta.name
    tipos_etiquetas[nombre] = tipos_etiquetas.get(nombre, 0) + 1

# Mostrar las 10 etiquetas más comunes
print("-"*70)
etiquetas_ordenadas = sorted(tipos_etiquetas.items(), key=lambda x: x[1], reverse=True)
for etiqueta, cantidad in etiquetas_ordenadas[:10]:
    print(f"  <{etiqueta}>: {cantidad}")

print("\n" + "="*70)
print("✓ EJERCICIO COMPLETADO")
print("="*70)