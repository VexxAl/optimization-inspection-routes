# Optimización de Rutas de Inspección - Proyecto Hykue

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://optimization-inspection-routes.streamlit.app/?embed_options=light_theme)

Plataforma experimental e implementación de metaheurísticas para resolver el **Problema de Enrutamiento de Arcos Capacitados (CARP)**, aplicado a la planificación de trayectorias para la inspección autónoma de redes de tuberías.

Proyecto final para la cátedra de Metaheurísticas.

## Características Principales

* **Entorno Multi-Algoritmo:** Implementación orientada a objetos de Optimización por Colonia de Hormigas (ACO) y Búsqueda Tabú (Tabu Search).
* **Dashboard Interactivo:** Panel web analítico construido con Streamlit y Plotly para el análisis de sensibilidad y la visualización de resultados.
* **Métricas en Vivo:** Curvas de convergencia, reconstrucción espacial de trayectos, análisis de métricas físicas (batería y *deadheading*) y mapas estigmérgicos de feromonas.
* **Contrato de Datos Unificado:** Arquitectura robusta basada en *Data Transfer Objects* (`ResultadoEjecucion`) para garantizar la reproducibilidad y comparación justa entre métodos poblacionales y de trayectoria.

## Despliegue en la Nube

Podés interactuar con la última versión estable del algoritmo directamente desde el navegador, sin necesidad de instalar el entorno local, accediendo a nuestro panel en Streamlit Community Cloud ;)

**[Acceder al Dashboard Interactivo](https://optimization-inspection-routes.streamlit.app/?embed_options=light_theme)**

## Instalación y Configuración (Entorno Local)

Este proyecto utiliza `uv` para la gestión ultrarrápida de dependencias y entornos virtuales.

1. **Instalar uv:**
   Si no tenés `uv` instalado, podés hacerlo con:

    ```bash
    pip install uv
    ```

    *(O revisá la documentación oficial para otros métodos de instalación).*

2. **Clonar el repositorio:**

    ```bash
    git clone https://github.com/VexxAl/optimization-inspection-routes.git
    cd optimization-inspection-routes
    ```

3. **Sincronizar el entorno virtual:**
    Para instalar todas las dependencias (incluyendo Streamlit, Plotly, NetworkX, etc.) y crear el entorno virtual automáticamente, simplemente ejecutá:

    ```bash
    uv sync
    ```

4. **Activar el entorno:**
    * En Windows:

        ```powershell
        .venv\Scripts\activate
        ```

    * En Linux/Mac:

        ```bash
        source .venv/bin/activate
        ```

## Estructura del Repositorio

```txt
optimization-inspection-routes/
├── src/
│   ├── dashboard.py         # Panel de control interactivo con Streamlit
│   ├── core_models.py       # Definición de estructuras de datos centrales
│   ├── aco.py               # Implementación de Optimización por Colonia de Hormigas
│   ├── tabu_search.py       # Implementación de Búsqueda Tabú
│   ├── graph_model.py       # Modelado de la red de tuberías y funciones auxiliares
│   ├── graph_generator.py   # Generación de redes de tuberías sintéticas para pruebas
│
├── notebooks/
│   ├── 01_experimentos_iniciales.ipynb  # Análisis exploratorio y pruebas iniciales
│   ├── 02_evaluacion_comparativa.ipynb  # Evaluación comparativa entre ACO y Tabu Search
│
├── data/
│   ├── red_base_5x5.json  # Ejemplo de red de tuberías para pruebas
│   ├── red_densa_10x10.json  # Red más compleja para evaluación de escalabilidad
│   ├── red_realista_asim.json  # Red inspirada en una topología de tuberías real
│
├── README.md
├── pyproject.toml         # Configuración de uv y dependencias del proyecto
├── uv.lock                # Archivo de bloqueo de dependencias generado por uv
├── .gitignore
```
