import time
import numpy as np
from core_models import ResultadoEjecucion

np.random.seed(19) # para reproducibilidad

class TabuSearch_CARP:
    """
    Algoritmo de Búsqueda Tabú para el Problema de Enrutamiento de Arcos Capacitados (CARP).
    Diseñado como metaheurística comparativa frente a ACO.
    """
    def __init__(self, red_tuberias, bateria_maxima=3000.0, max_iter=500, t_vecindad=10, tenencia_tabu=5, omega=1000.0):
        self.grafo = red_tuberias
        self.bateria_max = bateria_maxima
        self.max_iter = max_iter
        self.t_vecindad = t_vecindad
        self.tenencia_tabu = tenencia_tabu
        self.omega = omega
        
        # memoria de corto plazo: { (nodo_origen, nodo_destino) : iteracion_de_vencimiento }
        self.lista_tabu = {}


    def _evaluar_ruta_nodos(self, ruta_nodos):
        """
        Calcula las métricas del recorrido.
        """
        arcos_inspeccionados = set()
        bateria_total = 0.0
        bateria_deadheading = 0.0
        
        for i in range(len(ruta_nodos) - 1):
            u = ruta_nodos[i]
            v = ruta_nodos[i+1]
            tuberia = tuple(sorted((u, v))) # bidireccional
            
            if tuberia in arcos_inspeccionados:
                costo = self.grafo.costos_deadheading[u, v]
                bateria_total += costo
                bateria_deadheading += costo
            else:
                costo = self.grafo.costos_inspeccion[u, v]
                bateria_total += costo
                arcos_inspeccionados.add(tuberia)
                
        return bateria_total, bateria_deadheading, arcos_inspeccionados


    def _precalcular_estados(self, ruta):
        """
        Recorre la ruta una sola vez y cachea el estado físico.
        Retorna dos listas donde el índice 'i' contiene el estado exacto al alcanzar el nodo 'ruta[i]'.
        """
        
        bat_acumulada = 0.0
        arcos_acumulados = set()
        
        # estado inicial (antes de iniciar la ruta)
        baterias_prefijo = [bat_acumulada]
        arcos_prefijo = [arcos_acumulados.copy()]
        
        for j in range(len(ruta) - 1):
            u = int(ruta[j])
            v = int(ruta[j+1])
            tuberia = tuple(sorted((u, v)))
            
            if tuberia in arcos_acumulados:
                bat_acumulada += self.grafo.costos_deadheading[u, v]
            else:
                bat_acumulada += self.grafo.costos_inspeccion[u, v]
                arcos_acumulados.add(tuberia)
                
            baterias_prefijo.append(bat_acumulada)
            arcos_prefijo.append(arcos_acumulados.copy()) # Snapshot aislado
            
        return baterias_prefijo, arcos_prefijo
    

    def _visibilidad(self, u, v, arcos_inspeccionados):
        tuberia = tuple(sorted((u, v)))
        fue_inspeccionado = tuberia in arcos_inspeccionados
        
        costo = self.grafo.costos_deadheading[u, v] if fue_inspeccionado else self.grafo.costos_inspeccion[u, v]
        
        if fue_inspeccionado:
            return 1.0 / (costo * self.omega)
        return 1.0 / costo


    def _calcular_fitness(self, arcos):
        """
        Función objetivo que minimiza el consumo de batería por tramo inspeccionado.
        """

        cobertura = len(arcos)
        fitness = np.inf if cobertura == 0 else self.bateria_max / cobertura

        return fitness


    def _construir_ruta(self, nodo_inicio, bateria_restante, arcos_inspeccionados_base, iteracion_actual, nodo_previo=None):
        """
        Construcción de ruta con criterio de visibilidad y penalización Tabú.
        """
        
        ruta = [nodo_inicio]
        arcos_inspeccionados = set(arcos_inspeccionados_base)
        bateria_actual = float(bateria_restante)
        nodo_actual = nodo_inicio
        
        if nodo_previo is not None:
            nodo_previo = int(nodo_previo)
            
        while bateria_actual > 0:
            sucesores = list(self.grafo.grafo.successors(nodo_actual))
            candidatos = []
            
            for vecino in sucesores:
                tuberia = tuple(sorted((nodo_actual, vecino)))
                fue_inspeccionado = tuberia in arcos_inspeccionados
                
                costo_req = self.grafo.costos_deadheading[nodo_actual, vecino] if fue_inspeccionado else self.grafo.costos_inspeccion[nodo_actual, vecino]
                
                arco_dirigido = (nodo_actual, vecino)
                es_tabu = self.lista_tabu.get(arco_dirigido, -1) >= iteracion_actual
                
                if bateria_actual >= costo_req and not es_tabu:
                    if vecino != nodo_previo:
                        candidatos.append((vecino, costo_req, fue_inspeccionado, tuberia))
            
            # condición de "escape"
            if not candidatos and nodo_previo is not None:
                if self.grafo.grafo.has_edge(nodo_actual, nodo_previo):
                    tuberia_retorno = tuple(sorted((nodo_actual, nodo_previo)))
                    fue_insp_ret = tuberia_retorno in arcos_inspeccionados
                    costo_retorno = self.grafo.costos_deadheading[nodo_actual, nodo_previo] if fue_insp_ret else self.grafo.costos_inspeccion[nodo_actual, nodo_previo]
                    if bateria_actual >= costo_retorno:
                        candidatos.append((nodo_previo, costo_retorno, fue_insp_ret, tuberia_retorno))
            
            # si no hay candidatos el robot se detiene
            if not candidatos:
                break
                
            # ruleta basada en visibilidad
            visibilidades = [self._visibilidad(nodo_actual, c[0], arcos_inspeccionados) for c in candidatos]
            suma_vis = sum(visibilidades)
            
            if suma_vis == 0:
                break
                
            probabilidades = np.array(visibilidades) / suma_vis
            eleccion = np.random.choice(len(candidatos), p=probabilidades)
            
            siguiente_nodo, costo_consumido, fue_inspeccionado, tuberia_elegida = candidatos[eleccion]
            
            # transición
            bateria_actual -= costo_consumido
            if not fue_inspeccionado:
                arcos_inspeccionados.add(tuberia_elegida)
                
            ruta.append(siguiente_nodo)
            nodo_previo = nodo_actual
            nodo_actual = siguiente_nodo
            
        bateria_consumida = bateria_restante - bateria_actual
        return ruta, arcos_inspeccionados, bateria_consumida


    def _generar_vecino(self, ruta, iteracion, baterias_prefijo, arcos_prefijo):
        """
        Operador de vecindad basado en pivote con reconstrucción y penalización Tabú.
        """


        if len(ruta) < 3:
            return {'ruta': ruta , 'fitness': np.inf}  # no hay suficiente ruta para generar un vecino significativo
            
        # seleccionamos el pivote
        idx_pivote = np.random.randint(0, len(ruta) - 2)
        nodo_pivote = int(ruta[idx_pivote])
        nodo_siguiente_original = int(ruta[idx_pivote + 1])
        
        # búsqueda de alternativas
        sucesores = list(self.grafo.grafo.successors(nodo_pivote))
        alternativas = []
        for v in sucesores:
            if v != nodo_siguiente_original:
                alternativas.append(v)
        
        if not alternativas:
            return {'ruta': ruta , 'fitness': np.inf}
            
        nodo_alternativo = int(np.random.choice(alternativas))
        
        # extracción del estado precalculado
        bateria_gastada_trunc = baterias_prefijo[idx_pivote]
        arcos_truncados = arcos_prefijo[idx_pivote].copy() 
        bateria_restante = self.bateria_max - bateria_gastada_trunc
        
        # evaluación de la alternativa elegida
        tuberia_alt = tuple(sorted((nodo_pivote, nodo_alternativo)))
        fue_inspeccionado_alt = tuberia_alt in arcos_truncados
        costo_alt = self.grafo.costos_deadheading[nodo_pivote, nodo_alternativo] if fue_inspeccionado_alt else self.grafo.costos_inspeccion[nodo_pivote, nodo_alternativo]
        
        if bateria_restante < costo_alt:
            return {'ruta': ruta , 'fitness': np.inf}       # inválido por energía
            
        bateria_restante -= costo_alt
        if not fue_inspeccionado_alt:
            arcos_truncados.add(tuberia_alt)
            
        # penalización Tabú al camino original truncado
        self.lista_tabu[(nodo_pivote, nodo_siguiente_original)] = iteracion + self.tenencia_tabu
        
        # (re)construcción del resto de la ruta desde el nodo alternativo
        nodo_previo = nodo_pivote if idx_pivote == 0 else ruta[idx_pivote - 1]
        ruta_parcial, arcos_finales, _ = self._construir_ruta(
            nodo_inicio=nodo_alternativo,
            bateria_restante=bateria_restante,
            arcos_inspeccionados_base=arcos_truncados,
            iteracion_actual=iteracion,
            nodo_previo=nodo_previo
        )
        
        # evaluación final
        ruta_truncada = ruta[:idx_pivote + 1]
        ruta_completa = ruta_truncada + ruta_parcial
        bateria_total_final, _, _ = self._evaluar_ruta_nodos(ruta_completa)

        fitness = self._calcular_fitness(arcos_finales)
        
        return { 
            'ruta': ruta_completa, 
            'arcos_inspeccionados': arcos_finales, 
            'bateria_consumida': bateria_total_final, 
            'fitness': fitness 
        }


    def run(self, nodo_inicio=0):
        """
        Bucle principal de la metaheurística.
        """
        
        print(f"--- Iniciando Tabu Search ---")
        print(f"Iteraciones: {self.max_iter} | Tenencia Tabú: {self.tenencia_tabu}")
        print(f"Batería Máxima: {self.bateria_max} | Factor de Castigo: {self.omega}\n")

        tiempo_inicio = time.perf_counter()
        
        historial_mejor_global = []
        
        # inicialización
        ruta_init, arcos_init, bat_init = self._construir_ruta(nodo_inicio, self.bateria_max, set(), 0)
        fitness_init = self._calcular_fitness(arcos_init)
        
        mejor_solucion = {
            'ruta': ruta_init,
            'arcos_inspeccionados': arcos_init,
            'bateria_consumida': bat_init,
            'fitness': fitness_init
        }
        
        iteraciones_sin_mejora = 0
        
        for i in range(self.max_iter):
            # exploración local
            
            baterias_prefijo, arcos_prefijo = self._precalcular_estados(mejor_solucion['ruta'])     # un solo recorrido de la ruta base por iteración

            mejor_vecino = self._generar_vecino(mejor_solucion['ruta'], i, baterias_prefijo, arcos_prefijo)
            vecindario = [mejor_vecino]
            for _ in range(self.t_vecindad-1):
                vecino = self._generar_vecino(mejor_solucion['ruta'], i, baterias_prefijo, arcos_prefijo)
                vecindario.append(vecino)
                if vecino['fitness'] < mejor_vecino['fitness']:
                    mejor_vecino = vecino
            
            # actualización de la mejor solución global y del estado actual
            if mejor_vecino['fitness'] < mejor_solucion['fitness']:
                mejor_solucion = mejor_vecino
                iteraciones_sin_mejora = 0
                print(f"Iteración {i+1} -> Nuevo Óptimo | Z: {mejor_solucion['fitness']:.2f} | Cobertura: {len(mejor_solucion['arcos_inspeccionados'])} tramos | Batería consumida: {mejor_solucion['bateria_consumida']:.2f}")
            else:
                iteraciones_sin_mejora += 1
                
            historial_mejor_global.append(mejor_solucion['fitness'])
            
            # mantenimiento de memoria
            if i % 50 == 0:
                self.lista_tabu = {k: v for k, v in self.lista_tabu.items() if v > i}
                
            if iteraciones_sin_mejora >= 100:
                print(f"\nConvergencia temprana en iteración {i+1}.")
                break
                
        tiempo_total = time.perf_counter() - tiempo_inicio
        
        bat_total, bat_dh, arcos_inspeccionados_finales = self._evaluar_ruta_nodos(mejor_solucion['ruta'])
        
        print("\n--- Resultados Finales ---")
        print(f"Mejor Puntaje Z (Costo por tramo): {mejor_solucion['fitness']:.2f}")
        print(f"Tramos únicos inspeccionados: {len(arcos_inspeccionados_finales)} / {self.grafo.grafo.number_of_edges() // 2}")
        print(f"Batería consumida total: {bat_total:.2f}")
        print(f"Batería en deadheading: {bat_dh:.2f}")
        print(f"Tiempo de cómputo: {tiempo_total:.4f} seg")
        print(f"Ruta propuesta:\n{mejor_solucion['ruta']}")

        return ResultadoEjecucion(
            algoritmo="Tabu Search",
            parametros={
                "bateria_maxima": self.bateria_max,
                "max_iter": self.max_iter,
                "tenencia_tabu": self.tenencia_tabu,
                "omega": self.omega,
                "tamanio_vecindad": self.t_vecindad
            },
            mejor_ruta_nodos=mejor_solucion['ruta'],
            mejor_ruta_arcos=[(mejor_solucion['ruta'][j], mejor_solucion['ruta'][j+1]) for j in range(len(mejor_solucion['ruta']) - 1)],
            fitness_final=mejor_solucion['fitness'],
            bateria_consumida_total=bat_total,
            bateria_consumida_deadheading=bat_dh,
            arcos_unicos_inspeccionados=len(arcos_inspeccionados_finales),
            historial_mejor_global=historial_mejor_global,
            tiempo_ejecucion_seg=tiempo_total
        )

# ejemplo de ejecución
if __name__ == "__main__":
    from graph_model import RedTuberias

    red_tuberias = RedTuberias.cargar_red("./data/red_base_5x5.json")
    
    # config similar a ACO
    tabu = TabuSearch_CARP(
        red_tuberias=red_tuberias, 
        bateria_maxima=3000.0, 
        max_iter=100, 
        tenencia_tabu=5,
        t_vecindad=10,
        omega=1000.0
    )
    
    resultado = tabu.run(nodo_inicio=0)
