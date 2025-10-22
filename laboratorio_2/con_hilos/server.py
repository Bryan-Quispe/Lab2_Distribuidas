import socket
import threading
import csv
import json
import os

# Archivo CSV donde se almacenan las calificaciones
ARCHIVO_CSV = '../calificaciones.csv'

# ============================================================
# 1. FUNCIONES DE MANEJO DE ARCHIVO CSV
# ============================================================

def inicializar_csv():
    """
    Crea el archivo CSV si no existe.
    Este archivo guarda: ID del estudiante, nombre, materia y calificación.
    """
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])

def listar_todas():
    """
    Retorna todas las calificaciones registradas en formato JSON.
    """
    try:
        with open(ARCHIVO_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return {"status": "ok", "data": list(reader)}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def buscar_por_id(id_est):
    """
    Busca una calificación por ID de estudiante.
    Si existe, retorna el registro completo; si no, un mensaje de 'no encontrado'.
    """
    with open(ARCHIVO_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ID_Estudiante'] == id_est:
                return {"status": "ok", "data": row}
    return {"status": "not_found", "mensaje": "Estudiante no encontrado"}


# ============================================================
# 2. COMUNICACIÓN CON EL SERVIDOR DE NRCs (inter-servidor)
# ============================================================

def consultar_nrc(nrc):
    """
    Se conecta al servidor NRC (puerto 12346) para verificar que la materia exista.
    Retorna un diccionario con el resultado:
    - {"status": "ok"} si el NRC existe
    - {"status": "error"} si hay problema de red o el servidor NRC no responde
    """
    try:
        HOST, PORT = 'localhost', 12346
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        # Enviar comando al servidor NRC (protocolo definido)
        s.sendall(f"BUSCAR_NRC|{nrc}".encode('utf-8'))
        data = s.recv(1024)
        s.close()
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        return {"status": "error", "mensaje": f"Error consultando NRC: {e}"}


# ============================================================
# 3. OPERACIONES CRUD (CREAR, LEER, ACTUALIZAR, ELIMINAR)
# ============================================================

def agregar_calificacion(id_est, nombre, materia, calif):
    """
    Agrega un nuevo registro al CSV.
    Antes de registrar, valida el NRC con el servidor NRCs.
    """
    res_nrc = consultar_nrc(materia)
    if res_nrc["status"] != "ok":
        return {"status": "error", "mensaje": "Materia/NRC no válida o servidor NRC no disponible"}

    with open(ARCHIVO_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([id_est, nombre, materia, calif])
    return {"status": "ok", "mensaje": "Calificación agregada correctamente"}

def actualizar_calificacion(id_est, nueva_calif):
    """
    Actualiza la calificación de un estudiante si existe.
    Reescribe el archivo CSV manteniendo todos los registros.
    """
    filas = []
    actualizado = False
    with open(ARCHIVO_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ID_Estudiante'] == id_est:
                row['Calificacion'] = nueva_calif
                actualizado = True
            filas.append(row)

    if not actualizado:
        return {"status": "not_found", "mensaje": "Estudiante no encontrado"}

    with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])
        writer.writeheader()
        writer.writerows(filas)

    return {"status": "ok", "mensaje": "Calificacion actualizada correctamente"}

def eliminar_por_id(id_est):
    """
    Elimina el registro de un estudiante según su ID.
    """
    filas = []
    eliminado = False
    with open(ARCHIVO_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ID_Estudiante'] != id_est:
                filas.append(row)
            else:
                eliminado = True

    with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])
        writer.writeheader()
        writer.writerows(filas)

    if eliminado:
        return {"status": "ok", "mensaje": "Registro eliminado"}
    else:
        return {"status": "not_found", "mensaje": "Estudiante no encontrado"}


# ============================================================
# 4. PROCESAMIENTO DE COMANDOS (PROTOCOLO ENTRE CLIENTE Y SERVIDOR)
# ============================================================

def procesar_comando(comando):
    """
    Interpreta los comandos recibidos desde el cliente según el protocolo:
    AGREGAR|id|nombre|materia|calif
    BUSCAR|id
    ACTUALIZAR|id|nueva_calif
    LISTAR
    ELIMINAR|id
    """
    partes = comando.strip().split('|')
    op = partes[0].upper()

    if op == "AGREGAR" and len(partes) == 5:
        return agregar_calificacion(partes[1], partes[2], partes[3], partes[4])
    elif op == "BUSCAR" and len(partes) == 2:
        return buscar_por_id(partes[1])
    elif op == "ACTUALIZAR" and len(partes) == 3:
        return actualizar_calificacion(partes[1], partes[2])
    elif op == "LISTAR":
        return listar_todas()
    elif op == "ELIMINAR" and len(partes) == 2:
        return eliminar_por_id(partes[1])
    else:
        return {"status": "error", "mensaje": "Comando inválido"}


# ============================================================
# 5. SERVIDOR CONCURRENTE (uso de hilos)
# ============================================================

def manejar_cliente(client_socket, addr):
    """
    Atiende a un cliente en un hilo independiente.
    - Recibe el comando del cliente
    - Procesa el comando
    - Envía la respuesta
    """
    hilo_actual = threading.current_thread().name
    print(f"[SERVER] 🟢 Cliente conectado desde {addr} en hilo {hilo_actual}")

    try:
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            print(f"[SERVER] 📥 ({addr}) → Recibido del cliente: {data}")

            # Procesar la operación solicitada (CRUD)
            respuesta = procesar_comando(data)
            respuesta_json = json.dumps(respuesta)

            # Enviar respuesta al cliente
            client_socket.send(respuesta_json.encode('utf-8'))
            print(f"[SERVER] 📤 ({addr}) ← Enviado al cliente: {respuesta_json}")
        else:
            print(f"[SERVER] ⚠️ ({addr}) No se recibió ningún dato.")
    except Exception as e:
        print(f"[SERVER] ❌ Error en hilo {hilo_actual} con {addr}: {e}")
    finally:
        client_socket.close()
        print(f"[SERVER] 🔴 Cliente {addr} desconectado del hilo {hilo_actual}")


# ============================================================
# 6. FUNCIÓN PRINCIPAL (acepta múltiples clientes concurrentes)
# ============================================================

def main():
    """
    Crea el socket del servidor principal.
    Escucha peticiones en el puerto 12345 y lanza un hilo por cliente.
    """
    inicializar_csv()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(5)  # hasta 5 conexiones en espera
    print("[SERVER] Servidor concurrente escuchando en puerto 12345...")

    try:
        while True:
            # Acepta nueva conexión y lanza un hilo independiente
            client_socket, addr = server_socket.accept()
            hilo = threading.Thread(target=manejar_cliente, args=(client_socket, addr))
            hilo.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Servidor detenido manualmente.")
    finally:
        server_socket.close()


# ============================================================
# 7. PUNTO DE ENTRADA DEL PROGRAMA
# ============================================================

if __name__ == "__main__":
    """
    Ejecuta el servidor cuando este archivo se ejecuta directamente.
    Si se importa como módulo, no se inicia automáticamente.
    """
    main()
