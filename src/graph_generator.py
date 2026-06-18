import os
import numpy as np
from graph_model import RedTuberias


def generar_red_base() -> RedTuberias:
    """
    Malla de 5x5 basada en el mapa topológico tomado de ejemplo.
    """

    red = RedTuberias(25)

    # tuberías de oeste a este
    horizontales = [
        # fiila 0
        (0, 1, 'verde'), (1, 2, 'verde'), (2, 3, 'verde'), (3, 4, 'verde'),
        # fila 1
        (5, 6, 'cian'), (6, 7, 'verde'), (7, 8, 'verde'), (8, 9, 'cian'),
        # fila 2
        (10, 11, 'naranja'), (11, 12, 'naranja'), (12, 13, 'naranja'), (13, 14, 'bordo'),
        # fila 3
        (15, 16, 'naranja'), (16, 17, 'naranja'), (17, 18, 'naranja'), (18, 19, 'bordo'),
        # fila 4
        (20, 21, 'azul'), (21, 22, 'azul'), (22, 23, 'azul'), (23, 24, 'azul')
    ]

    # tuberías de norte a sur
    verticales = [
        # columna 0
        (0, 5, 'cian'), (5, 10, 'verde'), (10, 15, 'verde'), (15, 20, 'azul'),
        # columna 1
        (1, 6, 'verde'), (6, 11, 'verde'), (11, 16, 'verde'), (16, 21, 'verde'),
        # columna 2
        (2, 7, 'cian'), (7, 12, 'verde'), (12, 17, 'naranja'), (17, 22, 'naranja'),
        # columna 3
        (3, 8, 'azul'), (8, 13, 'cian'), (13, 18, 'naranja'), (18, 23, 'naranja'),
        # columna 4
        (4, 9, 'cian'), (9, 14, 'cian'), (14, 19, 'naranja'), (19, 24, 'naranja')
    ]

    for o, d, color in horizontales + verticales:
        red.agregar_tuberia(o, d, color)

    return red


def generar_red_densa() -> RedTuberias:
    """
    Genera una malla 10x10 (100 nodos) algorítmicamente.
    Asigna colores y distancias heterogéneas para complejizar el espacio de búsqueda.
    """

    filas, columnas = 10, 10
    red = RedTuberias(filas * columnas)
    colores = ['verde', 'azul', 'cian', 'naranja', 'bordo']

    for i in range(filas):
        for j in range(columnas):
            nodo_actual = i * columnas + j
            
            # horizontal (hacia la derecha)
            if j < columnas - 1:
                color = np.random.choice(colores)
                distancia = round(np.random.uniform(0.5, 5.0), 1)
                red.agregar_tuberia(nodo_actual, nodo_actual + 1, color, distancia)
                
            # vertical (hacia abajo)
            if i < filas - 1:
                color = np.random.choice(colores)
                distancia = round(np.random.uniform(0.5, 5.0), 1)
                red.agregar_tuberia(nodo_actual, nodo_actual + columnas, color, distancia)
                
    return red


def generar_red_realista() -> RedTuberias:
    """
    Construye una red basada en la malla 5x5 pero incorpora ramificaciones sin salida (nodos de grado 1) y saltos de distancia asimétricos.
    """
    red = RedTuberias(30) # 25 nodos base + 5 nodos terminales
    
    # reconstruir base 5x5 con distancias variadas
    base = generar_red_base()
    for u, v, data in base.grafo.edges(data=True):
        if u < v:
            dist_mod = 1.0 + ((u + v) % 3) * 0.5 
            red.agregar_tuberia(u, v, data['color'], distancia=dist_mod)
            
    # agregamos callejones sin salida
    
    red.agregar_tuberia(24, 25, 'bordo', distancia=8.5)
    red.agregar_tuberia(12, 26, 'cian', distancia=3.0)
    red.agregar_tuberia(4, 27, 'naranja', distancia=5.5)
    red.agregar_tuberia(0, 28, 'verde', distancia=1.2)
    red.agregar_tuberia(16, 29, 'azul', distancia=1.0)
    
    return red


def instanciar_redes_ejemplos():
    """
    Ejecuta el pipeline de generación, serialización y reconstrucción.
    """

    directorio_instancias = "./data"  # guardamos en ./data para mantener el proyecto organizado
    os.makedirs(directorio_instancias, exist_ok=True)
    
    instancias = {
        "red_base_5x5.json": generar_red_base(),
        "red_densa_10x10.json": generar_red_densa(),
        "red_realista_asim.json": generar_red_realista()
    }
    
    # fase de exportación
    for filename, red in instancias.items():
        filepath = os.path.join(directorio_instancias, filename)
        red.guardar_red(filepath)
        
    # fase de validación de integridad estructural
    for filename in instancias.keys():
        filepath = os.path.join(directorio_instancias, filename)
        red_cargada = RedTuberias.cargar_red(filepath)
        
        is_valida = True
        for nodo in range(red_cargada.n_nodes):
            if red_cargada.costos_deadheading.shape != (red_cargada.n_nodes, red_cargada.n_nodes):
                is_valida = False
                
        estado = "INTEGRA" if is_valida else "CORRUPTA"
        print(f" -> Mapa de {filename}: Estructura matricial {estado}.")

if __name__ == "__main__":
    instanciar_redes_ejemplos()