import numpy as np
import networkx as nx

class RedTuberias:
    def __init__(self, n_nodos):
        self.n_nodes = n_nodos
        self.grafo = nx.DiGraph()

        self.costos_deadheading = np.full((n_nodos, n_nodos), np.inf)
        self.costos_inspeccion = np.full((n_nodos, n_nodos), np.inf)

        # Al principio del algoritmo todas las tuberías requieren inspección
        self.tuberias_requeridas = np.zeros((n_nodos, n_nodos), dtype=bool)

    def agregar_tuberia(self, o:int, d:int, color:str):
        """
        Agrega una tubería entre el nodo de origen (o) y el nodo de destino (d) con un color específico.
         - o: nodo de origen
         - d: nodo de destino
         - color: representa el estado de la tubería (verde, azul, cian, naranja, bordo)
        La función actualiza el grafo con los costos de deadheading e inspección para ambos sentidos (o -> d y d -> o).
        Además, marca la tubería como requerida para inspección.
        """
        
        COSTOS = {
            'verde': {'deadheading': 100, 'inspeccion': 120},       # excelente estado
            'azul': {'deadheading': 150, 'inspeccion': 180},        # buen estado
            'cian': {'deadheading': 250, 'inspeccion': 300},        # estado regular
            'naranja': {'deadheading': 400, 'inspeccion': 480},     # estado malo
            'bordo': {'deadheading': 700, 'inspeccion': 840}        # estado crítico
        }

        costo_deadheading = COSTOS[color]['deadheading']
        costo_inspeccion = COSTOS[color]['inspeccion']

        # sentido de o -> d
        self.grafo.add_edge(o, d, weight=costo_deadheading)
        self.costos_deadheading[o][d] = costo_deadheading
        self.costos_inspeccion[o][d] = costo_inspeccion
        self.tuberias_requeridas[o][d] = True

        # sentido de d -> o
        self.grafo.add_edge(d, o, weight=costo_deadheading)
        self.costos_deadheading[d][o] = costo_deadheading
        self.costos_inspeccion[d][o] = costo_inspeccion
        self.tuberias_requeridas[d][o] = True

    def obtener_vecinas(self, nodo:int):
        """
        Devuelve una lista de nodos vecinos para un nodo dado.
        """
        return list(self.grafo.successors(nodo))
    

def crear_red_prueba():
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

if __name__ == "__main__":
    red = crear_red_prueba()
    print("Grafo de tuberías creado:")
    print("Nodos: ", red.n_nodes)
    print("Total de aristas: ", red.grafo.number_of_edges())
    
    print("\nEjemplo de vecindades para el nodo 12:")
    for vecino in red.obtener_vecinas(12):
        print(f"Vecino: {vecino}, Costo Deadheading: {red.costos_deadheading[12][vecino]}")