# Lab2_Distribuidas
Laboratiorio 2 de la materia de Aplicaciones Distribuidas 

INTEGRANTES:
BRYAN QUISPE 
CARLOS GRANDA
KEVIN COLOMA
ERICK MOREIRA

PARTE 1 

Verificacion del servidor sin hilos

![Ejecución del servidor secuencial server.py, mostrando que escucha correctamente en el puerto 12345. Se crea el archivo calificaciones.csv con el encabezado de columnas para registrar datos.](laboratorio_2/imagenes/servidorsinhilos_levantado.png)


El servidor server.py en la carpeta con_hilos escucha en el puerto 12345 y atiende múltiples clientes simultáneamente mediante hilos.
Cada conexión genera un hilo independiente para manejar solicitudes concurrentes de búsqueda y listado.
![Verificacion del servidor con hilos](laboratorio_2/imagenes/levantamiento_server_con_hilos.png)

Pruebas de menú

El archivo calificaciones.csv registra correctamente los datos enviados por los clientes, garantizando persistencia en disco.
Agregando un estudiante
![Agregar un estudiantes](laboratorio_2/imagenes/prueba_con_hilos_agregar.png)
Buscar y Enlistar estudiante
![Buscar y Enlistar estudiante](laboratorio_2/imagenes/prueba_con_hilos_buscar_listar.png)

El servidor concurrente atiende múltiples conexiones simultáneas, generando un hilo independiente para cada cliente conectado.
Persistencia CSV
![Persistencia CSV](laboratorio_2/imagenes/persistencia_CSV_con_hilos.png)
Pruebas de concurrencia
![Dos clientes](laboratorio_2/imagenes/prueba_con_hilos_2_clientes.png)
Se ejecutan varios clientes conectados simultáneamente al servidor, demostrando la atención paralela mediante hilos. Cada cliente realiza operaciones independientes como agregar, listar y actualizar calificaciones sin interferencias.
![Múltiples](laboratorio_2/imagenes/prueba_con_hilos_varios_clientes.png)

PARTE 2
Fragmento de código que implementa la creación, lectura y búsqueda de NRCs en el archivo CSV.
Permite validar materias y procesar comandos de tipo LISTAR_NRC y BUSCAR_NRC.

![codigo listar](laboratorio_2/imagenes/conexion_con_servidor.jpg).

