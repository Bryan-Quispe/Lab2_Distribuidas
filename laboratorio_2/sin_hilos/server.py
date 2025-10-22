import socket
import csv
import json
import os

# Definición de constantes
ARCHIVO_CSV = 'calificaciones.csv'
OK = 'ok'
NOT_FOUND = 'not_found'
ERROR = 'error'
AGREGAR = 'AGREGAR'
BUSCAR = 'BUSCAR'
ACTUALIZAR = 'ACTUALIZAR'
LISTAR = 'LISTAR'
ELIMINAR = 'ELIMINAR'

def inicializar_csv():
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])

def agregar_calificacion(id_est, nombre, materia, calificacion):
    try:
        # Validar entrada
        if not id_est or not nombre or not materia or not calificacion:
            return {"status": ERROR, "mensaje": "Todos los campos son obligatorios"}
        try:
            calificacion = float(calificacion)
            if not 0 <= calificacion <= 10:
                return {"status": ERROR, "mensaje": "La calificación debe estar entre 0 y 10"}
        except ValueError:
            return {"status": ERROR, "mensaje": "La calificación debe ser un número válido"}
        
        with open(ARCHIVO_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([id_est, nombre, materia, calificacion])
        return {"status": OK, "mensaje": f"Calificación agregada para ID {id_est}"}
    except Exception as e:
        return {"status": ERROR, "mensaje": f"Error al agregar calificación: {str(e)}"}

def buscar_por_id(id_est):
    try:
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                    return {"status": OK, "data": row}
            return {"status": NOT_FOUND, "mensaje": "ID no encontrado"}
    except Exception as e:
        return {"status": ERROR, "mensaje": f"Error al buscar: {str(e)}"}

def actualizar_calificacion(id_est, nueva_calif):
    try:
        # Validar entrada
        try:
            nueva_calif = float(nueva_calif)
            if not 0 <= nueva_calif <= 10:
                return {"status": ERROR, "mensaje": "La calificación debe estar entre 0 y 10"}
        except ValueError:
            return {"status": ERROR, "mensaje": "La calificación debe ser un número válido"}

        rows = []
        found = False
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                    row['Calificacion'] = str(nueva_calif)
                    found = True
                rows.append(row)
        if not found:
            return {"status": NOT_FOUND, "mensaje": "ID no encontrado"}
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])
            writer.writeheader()
            writer.writerows(rows)
        return {"status": OK, "mensaje": f"Calificación actualizada a {nueva_calif}"}
    except Exception as e:
        return {"status": ERROR, "mensaje": f"Error al actualizar: {str(e)}"}

def listar_todas():
    try:
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            return {"status": OK, "data": data}
    except Exception as e:
        return {"status": ERROR, "mensaje": f"Error al listar: {str(e)}"}

def eliminar_por_id(id_est):
    try:
        rows = []
        found = False
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                    found = True
                else:
                    rows.append(row)
        if not found:
            return {"status": NOT_FOUND, "mensaje": "ID no encontrado"}
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])
            writer.writeheader()
            writer.writerows(rows)
        return {"status": OK, "mensaje": f"Registro eliminado para ID {id_est}"}
    except Exception as e:
        return {"status": ERROR, "mensaje": f"Error al eliminar: {str(e)}"}

def procesar_comando(comando):
    try:
        partes = comando.strip().split('|')
        op = partes[0]
        if op == AGREGAR and len(partes) == 5:
            return agregar_calificacion(partes[1], partes[2], partes[3], partes[4])
        elif op == BUSCAR and len(partes) == 2:
            return buscar_por_id(partes[1])
        elif op == ACTUALIZAR and len(partes) == 3:
            return actualizar_calificacion(partes[1], partes[2])
        elif op == LISTAR and len(partes) == 1:
            return listar_todas()
        elif op == ELIMINAR and len(partes) == 2:
            return eliminar_por_id(partes[1])
        else:
            return {"status": ERROR, "mensaje": "Comando inválido"}
    except Exception as e:
        return {"status": ERROR, "mensaje": f"Error al procesar comando: {str(e)}"}

# Inicializar CSV
inicializar_csv()

# Configuración del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(1)
print("Servidor secuencial escuchando en puerto 12345...")

try:
    while True:
        try:
            client_socket, addr = server_socket.accept()
            print(f"Cliente conectado desde {addr}")
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                respuesta = procesar_comando(data)
                client_socket.send(json.dumps(respuesta).encode('utf-8'))
            client_socket.close()
            print("Cliente desconectado.")
        except Exception as e:
            print(f"Error en conexión con cliente: {str(e)}")
            if 'client_socket' in locals():
                client_socket.close()
except KeyboardInterrupt:
    print("Servidor detenido.")
finally:
    server_socket.close()