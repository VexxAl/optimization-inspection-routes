import os
import json
import numpy as np
import networkx as nx

class RedTuberias:

    COSTOS_BASE = {
        'verde': {'deadheading': 100, 'inspeccion': 120},       # excelente estado
        'azul': {'deadheading': 150, 'inspeccion': 180},        # buen estado
        'cian': {'deadheading': 250, 'inspeccion': 300},        # estado regular
        'naranja': {'deadheading': 400, 'inspeccion': 480},     # estado malo
        'bordo': {'deadheading': 700, 'inspeccion': 840}        # estado crítico
    }

    def __init__(self, n_nodos):
        self.n_nodes = n_nodos
        self.grafo = nx.DiGraph()

        self.costos_deadheading = np.full((n_nodos, n_nodos), np.inf)
        self.costos_inspeccion = np.full((n_nodos, n_nodos), np.inf)

        # Al principio del algoritmo todas las tuberías requieren inspección
        self.tuberias_requeridas = np.zeros((n_nodos, n_nodos), dtype=bool)

    def agregar_tuberia(self, o:int, d:int, color:str, distancia:float=1.0):
        """
        Agrega una tubería entre el nodo de origen (o) y el nodo de destino (d) con un color específico.
         - o: nodo de origen
         - d: nodo de destino
         - color: representa el estado de la tubería (verde, azul, cian, naranja, bordo)
         - distancia: distancia entre los nodos.
        La función actualiza el grafo con los costos de deadheading e inspección para ambos sentidos (o -> d y d -> o).
        Además, marca la tubería como requerida para inspección.
        """

        if color not in self.COSTOS_BASE:
            raise ValueError(f"Color '{color}' no reconocido. Colores válidos: {list(self.COSTOS_BASE.keys())}")
        
        costo_deadheading = self.COSTOS_BASE[color]['deadheading'] * distancia
        costo_inspeccion = self.COSTOS_BASE[color]['inspeccion'] * distancia

        # atributos para cada arco de la estructura
        atributos_arco = {
            'color': color,
            'distancia': distancia,
            'costo_deadheading': costo_deadheading,
            'costo_inspeccion': costo_inspeccion,
            'wheight': costo_deadheading
        }


        # sentido de o -> d
        self.grafo.add_edge(o, d, **atributos_arco)
        self.costos_deadheading[o][d] = costo_deadheading
        self.costos_inspeccion[o][d] = costo_inspeccion
        self.tuberias_requeridas[o][d] = True

        # sentido de d -> o
        self.grafo.add_edge(d, o, **atributos_arco)
        self.costos_deadheading[d][o] = costo_deadheading
        self.costos_inspeccion[d][o] = costo_inspeccion
        self.tuberias_requeridas[d][o] = True

    def obtener_vecinas(self, nodo:int):
        """
        Devuelve una lista de nodos vecinos para un nodo dado.
        """
        return list(self.grafo.successors(nodo))
    
    def guardar_red(self, path='data/red_tuberias.json'):
        """
        Guarda la red de tuberías en un archivo JSON.
        """

        aristas_guardadas = []

        for o, d, data in self.grafo.edges(data=True):
            # Para evitar duplicados, solo guardamos una dirección (o -> d) si o < d
            if o < d:  
                aristas_guardadas.append({
                    'origen': o,
                    'destino': d,
                    'color': data['color'],
                    'distancia': data['distancia']
                })

        data = {
            'n_nodos': self.n_nodes,
            'aristas': aristas_guardadas
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def cargar_red(cls, path='data/red_tuberias.json') -> 'RedTuberias':
        """
        Carga la red de tuberías desde un archivo JSON.
        """

        if not os.path.exists(path):
            raise FileNotFoundError(f"Archivo '{path}' no encontrado.")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        n_nodos = data.get('n_nodos')
        if n_nodos is None:
            raise ValueError("El archivo JSON debe contener el número de nodos bajo la clave 'n_nodos'.")
        
        # instanciamos la clase
        red = cls(n_nodos)

        for arista in data.get('aristas', []):
            red.agregar_tuberia(
                o = arista['origen'],
                d = arista['destino'],
                color = arista['color'],
                distancia = arista.get('distancia', 1.0)  # valor por defecto si no se especifica
            )
        
        return red
