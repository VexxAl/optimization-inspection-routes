import numpy as np

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True, kw_only=True)
class ResultadoEjecucion:
    """
    Resultado unificado de una ejecución algorítmica.
    Su objetivo es servir como contrato de datos único para:

    - Experimentos
    - Comparación entre algoritmos
    - Dashboard interactivo
    - Informe académico
    - Defensa del proyecto
    """

    # ============================================================
    # Información general de la ejecución
    # ============================================================

    algoritmo: str
    parametros: Dict[str, Any]

    # ============================================================
    # Mejor solución encontrada
    # ============================================================

    mejor_ruta_nodos: List[int]

    mejor_ruta_arcos: List[Tuple[int, int]]

    fitness_final: float

    bateria_consumida_total: float

    bateria_consumida_deadheading: float = 0.0

    arcos_unicos_inspeccionados: int = 0

    # ============================================================
    # Historial de convergencia
    # ============================================================

    historial_mejor_global: List[float] = field(default_factory=list)

    historial_mejor_iteracion: List[float] = field(default_factory=list)

    historial_promedio: List[float] = field(default_factory=list)

    historial_peor: List[float] = field(default_factory=list)

    historial_cobertura: List[int] = field(default_factory=list)

    # ============================================================
    # Métricas de ejecución
    # ============================================================

    tiempo_ejecucion_seg: float = 0.0

    motivo_parada: str = "iteraciones_maximas"

    # ============================================================
    # Métricas específicas de metaheurísticas
    # ============================================================

    matriz_feromonas_final: Optional[np.ndarray] = None

    eventos_tabu: int = 0

    # ============================================================
    # Validaciones
    # ============================================================

    def __post_init__(self) -> None:

        if self.fitness_final < 0:
            raise ValueError(
                "El fitness final no puede ser negativo."
            )

        if self.bateria_consumida_total < 0:
            raise ValueError(
                "La batería consumida no puede ser negativa."
            )

        if self.bateria_consumida_deadheading < 0:
            raise ValueError(
                "La batería consumida por deadheading no puede ser negativa."
            )

        if (
            self.bateria_consumida_deadheading
            > self.bateria_consumida_total
        ):
            raise ValueError(
                "El consumo por deadheading no puede exceder "
                "la batería total consumida."
            )

        if self.arcos_unicos_inspeccionados < 0:
            raise ValueError(
                "La cobertura no puede ser negativa."
            )

        if self.tiempo_ejecucion_seg < 0:
            raise ValueError(
                "El tiempo de ejecución no puede ser negativo."
            )

        if (
            self.mejor_ruta_arcos
            and len(self.mejor_ruta_arcos)
            != max(0, len(self.mejor_ruta_nodos) - 1)
        ):
            raise ValueError(
                "La cantidad de arcos no coincide con la ruta de nodos."
            )