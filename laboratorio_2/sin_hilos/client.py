import socket
import json

def mostrar_menu():
    print("\n--- Menú de Calificaciones ---")
    print("1. Agregar calificación")
    print("2. Buscar por ID")
    print("3. Actualizar calificación")
    print("4. Listar todas")
    print("5. Eliminar por ID")
    print("6. Salir")
    return input("Elija opción: ")

def enviar_comando(comando):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))
    client_socket.send(comando.encode('utf-8'))
    respuesta = client_socket.recv(1024).decode('utf-8')
    client_socket.close()
    return json.loads(respuesta)

while True:
    opcion = mostrar_menu()

    if opcion == "1":
        id_est = input("ID: ")
        nombre = input("Nombre: ")
        materia = input("Materia: ")
        calif = input("Calificación (0-20): ")
        comando = f"AGREGAR|{id_est}|{nombre}|{materia}|{calif}"
        res = enviar_comando(comando)
        print(res.get("mensaje", "Error de respuesta."))


    elif opcion == "2":
        id_est = input("ID: ")
        comando = f"BUSCAR|{id_est}"
        res = enviar_comando(comando)
        if res.get("status") == "ok":
            data = res["data"]
            print(f"Nombre: {data['Nombre']}, Materia: {data['Materia']}, Calificación: {data['Calificacion']}")
        else:
            print(res.get("mensaje", "Error."))

    elif opcion == "3":
        id_est = input("ID: ")
        nueva_calif = input("Nueva calificación (0-20): ")
        comando = f"ACTUALIZAR|{id_est}|{nueva_calif}"
        res = enviar_comando(comando)
        print(res.get("mensaje", "Error."))

    elif opcion == "4":
        comando = "LISTAR"
        res = enviar_comando(comando)
        if res.get("status") == "ok":
            print("\n--- Lista de Calificaciones ---")
            for row in res["data"]:
                print(row)
        else:
            print(res.get("mensaje", "Error."))

    elif opcion == "5":
        id_est = input("ID: ")
        comando = f"ELIMINAR|{id_est}"
        res = enviar_comando(comando)
        print(res.get("mensaje", "Error."))

    elif opcion == "6":
        print("Saliendo del programa...")
        break

    else:
        print("Opción inválida.")
