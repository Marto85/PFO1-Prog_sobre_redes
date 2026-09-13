import socket
import sys

# Configuracion de conexion hacia el servidor
HOST = "localhost"
PORT = 5000

def iniciar_cliente():
    """
    Conecta al servidor, permite enviar multiples mensajes
    y finaliza cuando el usuario escribe 'éxito' o 'exito' (con o sin tilde).
    """
    try:
        # Configuracion del socket TCP/IP
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect((HOST, PORT))
        print(f"[CONECTADO] Conectado al servidor en {HOST}:{PORT}")
        print("Escribi tus mensajes (o 'éxito' para salir):\n")

        while True:
            mensaje = input("> ")
            
            # Condicion de salida
            if mensaje.strip().lower() in ["éxito", "exito"]:
                print("[SALIDA] Cerrando conexion...")
                break
            
            # Evita enviar lineas vacias
            if not mensaje.strip():
                continue

            # Envia el mensaje codificado en bytes
            cliente.sendall(mensaje.encode('utf-8'))

            # Recibe la respuesta del servidor (buffer de 1024 bytes)
            respuesta = cliente.recv(1024)
            if not respuesta:
                print("[AVISO] El servidor cerro la conexion.")
                break

            # Muestra la respuesta enviada por el servidor
            print(f"[SERVIDOR] {respuesta.decode('utf-8')}\n")

    except ConnectionRefusedError:
        print(f"[ERROR] No se pudo conectar al servidor en {HOST}:{PORT}. ¿Esta iniciado servidor.py?")
    except KeyboardInterrupt:
        print("\n[SALIDA] Cliente interrumpido por el usuario.")
    finally:
        cliente.close()
        print("[CLIENTE] Conexion finalizada.")

if __name__ == '__main__':
    iniciar_cliente()