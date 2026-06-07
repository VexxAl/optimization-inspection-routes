# Optimización de Rutas de Inspección - Proyecto Hykue

Implementación del algoritmo de Optimización por Colonia de Hormigas (ACO) para resolver el Problema de Enrutamiento de Arcos Capacitados (CARP), aplicado a la inspección autónoma de redes de tuberías.

Proyecto final para la cátedra de Metaheurísticas.

## Instalación y Configuración

Este proyecto utiliza `uv` para la gestión ultrarrápida de dependencias y entornos virtuales.

1. **Instalar uv:**
   Si no tenés `uv` instalado, podés hacerlo con:

    ```bash
    pip install uv
    ```

    (O revisá la documentación oficial para otros métodos de instalación).

2. **Clonar el repositorio:**

    ```bash
    git clone https://github.com/VexxAl/optimization-inspection-routes.git
    cd optimization-inspection-routes
    ```

3. **Sincronizar el entorno virtual:**

    Para instalar todas las dependencias y crear el entorno virtual automáticamente, simplemente ejecutá:

    ```bash
    uv sync
    ```

4. **Activar el entorno:**

    - En Windows:

        ```powershell
        .venv\Scripts\activate
        ```

    - En Linux/Mac:

        ```bash
        source .venv/bin/activate
        ```
