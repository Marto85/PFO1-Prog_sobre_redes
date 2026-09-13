import sqlite3
import sys
import socket
from datetime import datetime

# Nombre del archivo de base de datos local
DB_NAME = "chat.db"

def inicializar_db():
    """
    Creo la tabla de mensajes si no existe.
    Se maneja excepciones en caso de que el archivo o la base de datos no sean accesibles.
    """
    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        ''')
        
        conexion.commit()
        conexion.close()
        print("[BD] Base de datos inicializada correctamente.")
    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo acceder o inicializar la base de datos: {e}")
        sys.exit(1)


def guardar_mensaje(contenido, ip_cliente, fecha_envio):
    """
    Inserta un nuevo registro en la tabla de mensajes.
    Retorna True si es exitoso o False si hubo un error.
    """
    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        
        cursor.execute('''
            INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
            VALUES (?, ?, ?)
        ''', (contenido, fecha_envio, ip_cliente))
        
        conexion.commit()
        conexion.close()
        return True
    except sqlite3.Error as e:
        print(f"[ERROR BD] Error al guardar mensaje: {e}")
        return False

    # Configuracion de red
HOST = "localhost"
PORT = 5000

def inicializar_socket():
    """
    Configura y pone en escucha el socket TCP del servidor.
    Maneja el error de puerto ocupado (Address already in use).
    """
    try:
        # Configuracion del socket TCP/IP
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Permite reutilizar el puerto inmediatamente si se reinicia el script
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Enlaza el socket a la direccion y puerto definidos
        servidor.bind((HOST, PORT))
        servidor.listen(5)
        print(f"[SERVIDOR] Escuchando en {HOST}:{PORT}...")
        return servidor
    except OSError as e:
        print(f"[ERROR] No se pudo inicializar el socket en el puerto {PORT}. ¿Puerto ocupado? Detalle: {e}")
        sys.exit(1)

def atender_clientes(servidor):
    """
    Acepta conexiones y procesa mensajes entrantes de clientes.
    """
    try:
        while True:
            # Espera y acepta una nueva conexion
            socket_cliente, direccion = servidor.accept()
            ip_cliente = direccion[0]
            print(f"[CONEXION] Cliente conectado desde {ip_cliente}:{direccion[1]}")
            
            try:
                while True:
                    # Recibe los datos enviados por el cliente
                    datos = socket_cliente.recv(1024)
                    if not datos:
                        # Si no hay datos, el cliente cerro la conexion
                        break
                    
                    mensaje = datos.decode('utf-8')
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    print(f"[{ip_cliente}] Mensaje recibido: {mensaje}")
                    
                    # Guarda el mensaje en la base de datos
                    guardar_mensaje(mensaje, ip_cliente, timestamp)
                    
                    # Responde al cliente con la confirmacion y el timestamp
                    respuesta = f"Mensaje recibido: {timestamp}"
                    socket_cliente.sendall(respuesta.encode('utf-8'))
            except ConnectionResetError:
                print(f"[CONEXION] El cliente {ip_cliente} se desconecto abruptamente.")
            finally:
                socket_cliente.close()
                print(f"[CONEXION] Conexion cerrada con {ip_cliente}.")
                
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Apagando el servidor...")
    finally:
        servidor.close()

if __name__ == '__main__':
    # 1. Inicializa la base de datos
    inicializar_db()
    # 2. Inicializa el socket en escucha
    servidor_socket = inicializar_socket()
    # 3. Empieza a atender clientes
    atender_clientes(servidor_socket)