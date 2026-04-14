import socket
import threading
import time

print("="*70)
print("EJERCICIO 1: SERVIDOR Y CLIENTE - PUERTO 8001")
print("="*70)

def servidor():
    """Función del servidor que escucha en el puerto 8001"""
    print("\n[SERVIDOR] Iniciando...")
    
    # Crear socket del servidor
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Configurar dirección y puerto
    host = 'localhost'
    puerto = 8001
    
    # Enlazar el socket al puerto
    servidor_socket.bind((host, puerto))
    
    # Escuchar conexiones
    servidor_socket.listen(1)
    print(f"[SERVIDOR] Escuchando en {host}:{puerto}")
    print("[SERVIDOR] Esperando conexión del cliente...")
    
    # Aceptar conexión del cliente
    cliente_socket, direccion = servidor_socket.accept()
    print(f"[SERVIDOR] Cliente conectado desde: {direccion}")
    
    # Mensaje a enviar
    mensaje = "Información enviada con éxito! Gracias por su preferencia"
    
    # Enviar mensaje al cliente
    cliente_socket.send(mensaje.encode('utf-8'))
    print(f"[SERVIDOR] Mensaje enviado: '{mensaje}'")
    
    # Cerrar conexiones
    cliente_socket.close()
    servidor_socket.close()
    print("[SERVIDOR] Conexión cerrada")

def cliente():
    """Función del cliente que se conecta al servidor"""
    # Esperar un poco para que el servidor esté listo
    time.sleep(1)
    
    print("\n[CLIENTE] Iniciando...")
    
    # Crear socket del cliente
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Configurar dirección y puerto del servidor
    host = 'localhost'
    puerto = 8001
    
    print(f"[CLIENTE] Intentando conectar a {host}:{puerto}...")
    
    # Conectar al servidor
    cliente_socket.connect((host, puerto))
    print("[CLIENTE] Conectado al servidor")
    
    # Recibir mensaje del servidor
    mensaje = cliente_socket.recv(1024).decode('utf-8')
    
    print("[CLIENTE] Mensaje recibido:")
    print("-"*70)
    print(f"   {mensaje}")
    print("-"*70)
    
    # Cerrar conexión
    cliente_socket.close()
    print("[CLIENTE] Desconectado")

# Crear hilos para servidor y cliente
servidor_thread = threading.Thread(target=servidor)
cliente_thread = threading.Thread(target=cliente)

# Iniciar servidor primero
servidor_thread.start()

# Iniciar cliente
cliente_thread.start()

# Esperar a que ambos terminen
servidor_thread.join()
cliente_thread.join()

print("\n" + "="*70)
print("✓ COMUNICACIÓN COMPLETADA EXITOSAMENTE")
print("="*70)