import socket
import json

# ---------------- Comunicación ----------------
def enviar_comando(comando):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 12345))
    s.send(comando.encode('utf-8'))
    data = s.recv(2048).decode('utf-8')
    s.close()
    return json.loads(data)

# ---------------- Menú ----------------
def menu():
    print("\n--- MENÚ CLIENTE ---")
    print("1. Agregar calificación")
    print("2. Buscar por ID")
    print("3. Actualizar calificación")
    print("4. Listar todo")
    print("5. Eliminar por ID")
    print("6. Salir")
    return input("Opción: ")

# ---------------- Función auxiliar para validar ID duplicado ----------------
def existe_id(id_est):
    """Consulta al servidor si el ID ya existe."""
    res = enviar_comando(f"BUSCAR|{id_est}")
    return res.get("status") == "ok"

# ---------------- Programa principal ----------------
while True:
    op = menu()

    # ----------- OPCIÓN 1: Agregar calificación -----------
    if op == "1":
        # Verificar ID duplicado
        while True:
            id_est = input("ID: ")
            if existe_id(id_est):
                print(f"El ID {id_est} ya existe. Ingrese otro ID.")
            else:
                break

        nombre = input("Nombre: ")
        materia = input("Materia (ej. MAT101): ")

        # Validar calificación entre 0 y 10
        while True:
            try:
                calif = float(input("Calificación (0-10): "))
                if 0 <= calif <= 10:
                    break
                else:
                    print("Calificación fuera de rango. Debe ser entre 0 y 10.")
            except ValueError:
                print("Ingrese un número válido.")

        res = enviar_comando(f"AGREGAR|{id_est}|{nombre}|{materia}|{calif}")
        print(res["mensaje"])

    # ----------- OPCIÓN 2: Buscar por ID -----------
    elif op == "2":
        id_est = input("ID: ")
        res = enviar_comando(f"BUSCAR|{id_est}")
        if res.get("status") == "ok":
            data = res["data"]
            print(f"ID: {data['ID_Estudiante']} | Nombre: {data['Nombre']} | Materia: {data['Materia']} | Calificación: {data['Calificacion']}")
        else:
            print("No se encontró el estudiante.")

    # ----------- OPCIÓN 3: Actualizar calificación -----------
    elif op == "3":
        id_est = input("ID del estudiante a actualizar: ")
        if not existe_id(id_est):
            print("Ese ID no existe.")
        else:
            while True:
                try:
                    nueva_calif = float(input("Nueva calificación (0-10): "))
                    if 0 <= nueva_calif <= 10:
                        break
                    else:
                        print("Debe estar entre 0 y 10.")
                except ValueError:
                    print("Ingrese un número válido.")
            res = enviar_comando(f"ACTUALIZAR|{id_est}|{nueva_calif}")
            print(res["mensaje"])

    # ----------- OPCIÓN 4: Listar todos -----------
    elif op == "4":
        res = enviar_comando("LISTAR")
        if res.get("status") == "ok":
            print("\nLISTADO DE CALIFICACIONES:")
            for row in res["data"]:
                print(f"{row['ID_Estudiante']} - {row['Nombre']} - {row['Materia']} - {row['Calificacion']}")
        else:
            print(res["mensaje"])

    # ----------- OPCIÓN 5: Eliminar por ID -----------
    elif op == "5":
        id_est = input("ID a eliminar: ")
        res = enviar_comando(f"ELIMINAR|{id_est}")
        print(res["mensaje"])

    elif op == "6":
        print("Saliendo del sistema...")
        break
    else:
        print("Opción inválida")
