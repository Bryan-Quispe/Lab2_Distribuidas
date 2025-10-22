# nrcs_server.py — Servidor secuencial para validar NRCs
import socket
import csv
import json
import os

ARCHIVO_NRC = 'nrcs.csv'
HOST = 'localhost'
PORT = 12346

# ----------------- Funciones de datos -----------------
def inicializar_nrc_csv():
    """Crea archivo base de NRCs si no existe."""
    if not os.path.exists(ARCHIVO_NRC):
        with open(ARCHIVO_NRC, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['NRC', 'Materia'])
            writer.writerows([
                ['MAT101', 'Matemáticas I'],
                ['CS102', 'Programación I'],
                ['NET201', 'Redes I'],
                ['SO202', 'Sistemas Operativos'],
                ['BD301', 'Bases de Datos']
            ])

def listar_nrcs():
    try:
        with open(ARCHIVO_NRC, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return {"status": "ok", "data": list(reader)}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def buscar_nrc(nrc):
    try:
        with open(ARCHIVO_NRC, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['NRC'] == nrc:
                    return {"status": "ok", "data": row}
        return {"status": "not_found", "mensaje": "NRC no existe"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

# ----------------- Procesar comandos -----------------
def procesar_comando(comando):
    partes = comando.strip().split('|')
    op = partes[0].upper()
    if op == "LISTAR_NRC":
        return listar_nrcs()
    elif op == "BUSCAR_NRC" and len(partes) == 2:
        return buscar_nrc(partes[1].strip())
    else:
        return {"status": "error", "mensaje": "Comando inválido"}

# ----------------- Servidor principal -----------------
# ----------------- Servidor principal -----------------
def main():
    inicializar_nrc_csv()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[NRC] Servidor escuchando en {HOST}:{PORT} ...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"[NRC] Cliente conectado desde {addr}")

            try:
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    print(f"[NRC] Petición recibida: {data}")

                    # Identificar la operación solicitada
                    partes = data.strip().split('|')
                    operacion = partes[0].upper()

                    if operacion in ["LISTAR_NRC", "LISTAR NRC"]:
                        print(f"[NRC] Solicitando listado completo de NRCs")
                    elif operacion in ["BUSCAR_NRC", "BUSCAR NRC"]:
                        if len(partes) > 1:
                            print(f"[NRC] Buscando NRC específico: {partes[1].strip()}")
                        else:
                            print(f"[NRC] Comando BUSCAR recibido sin parámetro NRC")

                    # Procesar la petición
                    respuesta = procesar_comando(data)
                    respuesta_json = json.dumps(respuesta, ensure_ascii=False)

                    client_socket.send(respuesta_json.encode('utf-8'))
                    print(f"[NRC] Respuesta enviada: {respuesta_json}")

            except Exception as e:
                print(f"[NRC] Error al atender cliente {addr}: {e}")

            finally:
                client_socket.close()
                print(f"[NRC] Cliente desconectado: {addr}\n{'-'*80}")

    except KeyboardInterrupt:
        print("\n[NRC] Servidor detenido manualmente.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
