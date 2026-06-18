import numpy as np
from core_models import ResultadoEjecucion

np.random.seed(19) # para reproducibilidad

class ACO_CARP:
    """
    Algoritmo de Optimización por Colonia de Hormigas (ACO) para el 
    Problema de Enrutamiento de Arcos Capacitados (CARP) - Proyecto Hykue.

    :param red: Instancia de la Red de Tuberías (Graph)
    :param n_hormigas: Número de hormigas (simulaciones) por iteración
    :param max_iter: Número máximo de iteraciones para el proceso de optimización
    :param alpha: Peso de la memoria colectiva (Feromonas) en la ecuación de transición
    :param beta: Peso de la exploración (Visibilidad) en la ecuación de transición
    :param rho: Tasa de evaporación de feromonas (0 < rho < 1)
    :param Q: Amplificador para el depósito elitista de feromonas (mayor Q = mayor refuerzo para mejores soluciones)
    :param omega: Factor de penalización para arcos ya visitados en la ecuación de transición
    """

    def __init__(self, red, n_hormigas=100, max_iter=1000, alpha=1.0, beta=2.0, 
                 rho=0.1, Q=1.0, omega=1000.0, bateria_max=3000.0):
        self.red = red
        self.n_hormigas = n_hormigas
        self.max_iter = max_iter
        
        # hiperparámetros de transición
        self.alpha = alpha      
        self.beta = beta        
        self.rho = rho          
        
        # hiperparámetros de penalización y aptitud
        self.Q = Q
        self.omega = omega      # "para penalizar caños ya visitados
        self.bateria_max = bateria_max
        
        # matriz de feromonas (tau)
        self.tau = np.ones((red.n_nodes, red.n_nodes)) * 0.3
        

        self.mejor_ruta_global = []
        self.mejor_z_global = float('inf')
        self.mejor_cobertura_global = 0
        self.mejor_bateria_consumida_global = 0


    def obtener_costo_arco(self, u, v, arcos_visitados):
        """
        Consulta la memoria individual de la hormiga para determinar qué costo de fricción aplicar (Activo o Inactivo).
        """

        arco_actual = tuple(sorted((u, v)))
        if arco_actual in arcos_visitados:
            return self.red.costos_deadheading[u][v], True      # aplicamos costo barato: c_ij
        else:
            return self.red.costos_inspeccion[u][v], False      # aplicamos costo caro: c*_ij


    def calcular_probabilidades(self, nodo_actual, nodo_anterior, arcos_visitados, bateria_restante):
        """
        Implementa la ecuación de transición con la penalización Omega y la Lista Tabú Condicional.
        """

        vecinos = self.red.obtener_vecinas(nodo_actual)
        
        # filtramos vecinos por viabilidad energética
        vecinos_viables = []
        for v in vecinos:
            costo, _ = self.obtener_costo_arco(nodo_actual, v, arcos_visitados)
            if bateria_restante >= costo:
                vecinos_viables.append((v, costo))
                
        if not vecinos_viables:
            return None # sin salida por falta de batería
            
        
        vecinos_no_tabu = [v_tuple for v_tuple in vecinos_viables if v_tuple[0] != nodo_anterior]       # aplicamos la lista tabú  para evitar movimientos de ida y vuelta inmediatos
        
        # si al filtrar nos quedamos sin opciones, ignoramos la lista
        if not vecinos_no_tabu:
            opciones = vecinos_viables
        else:
            opciones = vecinos_no_tabu
            
        # ruleta estocástica (Visibilidad + Feromona)
        probabilidades = []
        nodos_destino = []
        suma_total = 0.0
        
        for v, costo in opciones:
            arco_actual = tuple(sorted((nodo_actual, v)))
            
            # calculamos la visibilidad (eta)
            if arco_actual in arcos_visitados:
                eta = 1.0 / (costo * self.omega) # penalizamos
            else:
                eta = 1.0 / costo
                
            feromona = self.tau[nodo_actual][v]
            
            # puntuación de la transición
            score = (feromona ** self.alpha) * (eta ** self.beta)
            probabilidades.append(score)
            nodos_destino.append(v)
            suma_total += score
            
        if suma_total == 0:
            return int(np.random.choice(nodos_destino))
            
        probabilidades_normalizadas = [p / suma_total for p in probabilidades]
        
        # elegimos el siguiente nodo
        siguiente_nodo = int(np.random.choice(nodos_destino, p=probabilidades_normalizadas))
                
        return siguiente_nodo


    def simular_hormiga(self, nodo_inicio=0):
        """
        Ciclo de vida de 1 hormiga (1 Simulación de Hykue).
        """

        ruta = [nodo_inicio]
        arcos_visitados = set() # memoria de estado individual
        bateria = self.bateria_max
        nodo_actual = nodo_inicio
        nodo_anterior = None
        
        while bateria > 0:
            siguiente_nodo = self.calcular_probabilidades(nodo_actual, nodo_anterior, arcos_visitados, bateria)
            
            if siguiente_nodo is None:
                break # no tenemos más opciones viables por falta de batería
                
            costo, fue_visitado = self.obtener_costo_arco(nodo_actual, siguiente_nodo, arcos_visitados)
            bateria -= costo
            
            if not fue_visitado:
                arcos_visitados.add(tuple(sorted((nodo_actual, siguiente_nodo))))
                
            ruta.append(siguiente_nodo)
            nodo_anterior = nodo_actual
            nodo_actual = siguiente_nodo
            
        bateria_consumida = self.bateria_max - bateria
        cobertura = len(arcos_visitados)

        # funcion objetivo: capacidad máxima dividido por la cobertura (con penalización para soluciones sin cobertura)
        if cobertura == 0:
            z_fitness = float('inf') # Peor caso
        else:
            z_fitness = self.bateria_max / cobertura 


        return ruta, z_fitness, cobertura, bateria_consumida


    def actualizar_feromonas(self, mejor_ruta_iter, mejor_z_iter):
        """
        Evaporación y Depósito elitista.
        """
        # evaporación global
        self.tau *= (1 - self.rho)
        
        # depósito
        if mejor_z_iter < float('inf'):
            deposito = self.Q / mejor_z_iter
            for i in range(len(mejor_ruta_iter) - 1):
                u = mejor_ruta_iter[i]
                v = mejor_ruta_iter[i+1]
                self.tau[u][v] += deposito


    def run(self):
        """
        Bucle de simulación poblacional.
        """

        print(f"--- Iniciando ACO ---")
        print(f"Población: {self.n_hormigas} hormigas | Iteraciones: {self.max_iter}")
        print(f"Batería Máxima: {self.bateria_max} | Factor de Castigo: {self.omega}\n")

        self.historial_z = []
        
        for iteracion in range(self.max_iter):            
            mejor_ruta_iter = []
            mejor_z_iter = float('inf')
            mejor_cobertura_iter = 0
            mejor_bateria_consumida_iter = 0            
            
            for _ in range(self.n_hormigas):
                # empezamos en el Nodo 0 (podemos variar esto en los experimentos para generar diversidad)
                ruta, z_fitness, cobertura, bateria_consumida = self.simular_hormiga(nodo_inicio=0)
                
                if z_fitness < mejor_z_iter:
                    mejor_z_iter = z_fitness
                    mejor_ruta_iter = ruta
                    mejor_cobertura_iter = cobertura
                    mejor_bateria_consumida_iter = bateria_consumida
                    
            if mejor_z_iter < self.mejor_z_global:
                self.mejor_z_global = mejor_z_iter
                self.mejor_ruta_global = mejor_ruta_iter
                self.mejor_cobertura_global = mejor_cobertura_iter
                self.mejor_bateria_consumida_global = mejor_bateria_consumida_iter

                print(f"Iteración {iteracion+1} -> Nuevo Óptimo | Z: {self.mejor_z_global:.2f} | Cobertura: {self.mejor_cobertura_global} tramos | Batería consumida: {self.mejor_bateria_consumida_global:.2f}")
                
            self.actualizar_feromonas(mejor_ruta_iter, mejor_z_iter)
            self.historial_z.append(self.mejor_z_global)
        

        print("\n--- Resultados Finales ---")
        print(f"Mejor Puntaje Z (Costo por tramo): {self.mejor_z_global:.2f}")
        print(f"Tramos únicos inspeccionados: {self.mejor_cobertura_global} / {self.red.grafo.number_of_edges() // 2}")
        print(f"Batería consumida total: {self.mejor_bateria_consumida_global:.2f} / {self.bateria_max}")
        print(f"Ruta propuesta:\n{self.mejor_ruta_global}")
        
        return ResultadoEjecucion(
            algoritmo="ACO",
            parametros={
                "alpha": self.alpha,
                "beta": self.beta,
                "rho": self.rho,
                "Q": self.Q,
                "omega": self.omega,
                "n_hormigas": self.n_hormigas,
                "n_iteraciones": self.max_iter,
                "bateria_max": self.bateria_max,
            },

            mejor_ruta_nodos=self.mejor_ruta_global,

            mejor_ruta_arcos=[
                (self.mejor_ruta_global[i],
                self.mejor_ruta_global[i + 1])
                for i in range(len(self.mejor_ruta_global) - 1)
            ],

            fitness_final=self.mejor_z_global,
            bateria_consumida_total=self.mejor_bateria_consumida_global,
            arcos_unicos_inspeccionados=self.mejor_cobertura_global,
            historial_mejor_global=self.historial_z
        )

# ---

# ejecución independiente
if __name__ == "__main__":
    from graph_model import RedTuberias
    
    # cargamos la red de prueba 5x5 desde ./data/red_base_5x5.json
    red_tuberias = RedTuberias.cargar_red("./data/red_base_5x5.json")

    # Batería configurada para permitir varios movimientos
    # (Ej: 3000 unidades permite ~10-15 arcos dependiendo del color)
    aco = ACO_CARP(
        red=red_tuberias, 
        n_hormigas=20,      
        max_iter=1000,        
        bateria_max=3000.0,
        omega=1000.0
    ) # el """mejor fitness""" para esta configuración debería ser 3000/40 = 75 (ya que hay 40 arcos únicos en la red de prueba)
    
    resultado = aco.run()