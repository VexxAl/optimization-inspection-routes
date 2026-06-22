import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from graph_generator import generar_red_base
from aco import ACO_CARP

# Configuración de página
st.set_page_config(page_title="Hykue ACO-CARP Dashboard", layout="wide")


# Módulos de Visualización
def graficar_convergencia(resultado):
    """Genera la curva de convergencia de la función objetivo Z y otras métricas."""
    fig = go.Figure()
    
    # Z Global
    fig.add_trace(go.Scatter(
        y=resultado.historial_mejor_global,
        mode='lines', name='Mejor Z Global',
        line=dict(color='red', width=3)
    ))
    
    # Z Promedio (si está poblado)
    if resultado.historial_promedio:
        fig.add_trace(go.Scatter(
            y=resultado.historial_promedio,
            mode='lines', name='Z Promedio Poblacional',
            line=dict(color='orange', width=1, dash='dash')
        ))

    fig.update_layout(
        title="Curva de Convergencia del Algoritmo ACO",
        xaxis_title="Iteraciones",
        yaxis_title="Fitness Z (Batería / Cobertura) [↓ Mejor]",
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )
    return fig


def mapear_costo_a_color(costo):
    """Asigna el color representativo según el costo de fricción inactivo (deadheading)."""
    if costo == 100: return 'green'
    if costo == 150: return 'blue'
    if costo == 250: return 'cyan'
    if costo == 400: return 'orange'
    if costo == 700: return 'darkred'
    return 'gray'

def _graficar_base_red(red):
    """
    Retorna figura base con topología de la red (aristas y nodos sin ruta).
    """
    fig = go.Figure()
    
    # coordenadas espaciales fijas para grilla de la red 5x5
    pos_x = {i: (i % 5) for i in range(red.n_nodes)}
    pos_y = {i: (4 - (i // 5)) for i in range(red.n_nodes)}
    
    # aristas individuales con su color por costo operacional
    arcos_dibujados = set()
    for u, v in red.grafo.edges():
        arco_fisico = tuple(sorted((u, v)))
        if arco_fisico not in arcos_dibujados:
            x0, y0 = pos_x[u], pos_y[u]
            x1, y1 = pos_x[v], pos_y[v]
            
            costo = red.costos_deadheading[u][v]
            color = mapear_costo_a_color(costo)
            
            fig.add_trace(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode='lines',
                line=dict(width=4, color=color),
                hoverinfo='text',
                text=f"Tubería {u}-{v} | Costo Base: {costo}",
                showlegend=False
            ))
            arcos_dibujados.add(arco_fisico)
    
    return fig, pos_x, pos_y


def graficar_topologia_sin_ruta(red):
    """
    Grafica solo la topología de la red con números y colores.
    """
    fig, pos_x, pos_y = _graficar_base_red(red)
    
    # vértices con numeración
    x_nodos = [pos_x[i] for i in range(red.n_nodes)]
    y_nodos = [pos_y[i] for i in range(red.n_nodes)]
    
    fig.add_trace(go.Scatter(
        x=x_nodos, y=y_nodos,
        mode='markers+text',
        marker=dict(size=22, color='white', line=dict(width=2, color='black')),
        text=[str(i) for i in range(red.n_nodes)],
        textposition="middle center",
        textfont=dict(size=10, color='black'),
        name='Intersecciones',
        showlegend=False
    ))
    
    fig.update_layout(
        title="Red Topológica",
        showlegend=True,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
        height=650
    )
    return fig


def graficar_ruta_sin_numeros(red, ruta_nodos):
    """
    Grafica la ruta óptima sin números en los nodos.
    """
    fig, pos_x, pos_y = _graficar_base_red(red)
    
    # vértices sin numeración
    x_nodos = [pos_x[i] for i in range(red.n_nodes)]
    y_nodos = [pos_y[i] for i in range(red.n_nodes)]
    
    fig.add_trace(go.Scatter(
        x=x_nodos, y=y_nodos,
        mode='markers',
        marker=dict(size=22, color='white', line=dict(width=2, color='black')),
        name='Intersecciones',
        showlegend=False,
        hoverinfo='text',
        text=[f"Nodo {i}" for i in range(red.n_nodes)]
    ))
    
    # superposición de la trayectoria óptima
    if ruta_nodos:
        ruta_x = [pos_x[n] for n in ruta_nodos]
        ruta_y = [pos_y[n] for n in ruta_nodos]
        
        fig.add_trace(go.Scatter(
            x=ruta_x, y=ruta_y,
            mode='lines+markers',
            line=dict(width=5, color='rgba(255, 0, 255, 0.7)'),
            marker=dict(size=10, color='darkblue', symbol='circle'),
            name='Ruta de Inspección',
            hoverinfo='text',
            text=[f"Paso {i}: Nodo {n}" for i, n in enumerate(ruta_nodos)]
        ))
        
        # indicadores de Inicio y Fin del recorrido
        fig.add_trace(go.Scatter(
            x=[pos_x[ruta_nodos[0]], pos_x[ruta_nodos[-1]]],
            y=[pos_y[ruta_nodos[0]], pos_y[ruta_nodos[-1]]],
            mode='markers+text',
            marker=dict(size=14, color=['green', 'red'], symbol=['square', 'x']),
            text=['INICIO', 'FIN'],
            textposition="top center",
            textfont=dict(size=11, color='black'),
            name='Puntos Críticos',
            showlegend=False
        ))
    
    fig.update_layout(
        title="Trayectoria Óptima",
        showlegend=True,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
        height=650
    )
    return fig


def graficar_matriz_feromonas(matriz_tau):
    """Genera un Heatmap de la matriz de feromonas final."""
    fig = px.imshow(
        matriz_tau, 
        color_continuous_scale="Viridis",
        labels=dict(x="Nodo Destino", y="Nodo Origen", color="Concentración (τ)"),
        title="Mapa Estigmérgico (Matriz de Feromonas)"
    )
    
    return fig



def main():
    st.title("Hykue: Optimización de Rutas de Inspección")
    st.markdown("Dashboard para el análisis del problema de enrutamiento de arcos capacitados.")

    # hiperparámetros ACO
    st.sidebar.header("⚙️ Hiperparámetros ACO")
    
    n_hormigas = st.sidebar.slider("Población (Hormigas)", 10, 200, 20, step=10)
    max_iter = st.sidebar.slider("Iteraciones Máximas", 10, 2000, 200, step=10)
    bateria_max = st.sidebar.number_input("Batería Máxima", min_value=500, max_value=10000, value=3000, step=100)

    st.sidebar.subheader("Ecuación de Transición")
    alpha = st.sidebar.slider("Alfa (Importancia Feromona)", 0.0, 5.0, 1.15, step=0.05)
    beta = st.sidebar.slider("Beta (Importancia Visibilidad)", 0.0, 5.0, 1.5, step=0.1)
    omega = st.sidebar.number_input("Omega (Penalización Deadheading)", value=1113.17)
    
    st.sidebar.subheader("Actualización Estigmérgica")
    rho = st.sidebar.slider("Rho (Tasa Evaporación)", 0.01, 1.0, 0.05, step=0.01)
    Q = st.sidebar.number_input("Q (Factor Depósito Elitista)", value=1.0)

    ejecutar = st.sidebar.button("Ejecutar Simulación", type="primary")

    if ejecutar:
        with st.spinner('Ejecuyendo colonia de hormigas y optimizando trayectorias...'):
            red = generar_red_base()
            aco = ACO_CARP(
                red=red, n_hormigas=n_hormigas, max_iter=max_iter,
                alpha=alpha, beta=beta, rho=rho, Q=Q, omega=omega, bateria_max=bateria_max
            )
            
            resultado = aco.run() 

            # guardamos en el estado de la sesión
            st.session_state.resultado = resultado
            st.session_state.red = red
            st.session_state.tiempo = resultado.tiempo_ejecucion_seg

            # Forzamos una recarga limpia de la UI para renderizar los componentes de abajo
            st.rerun()

    # evaluamos la ausencia de datos para bloquear el renderizado de gráficos
    if 'resultado' not in st.session_state:
        st.info("<- Ajuste los parámetros y presione 'Ejecutar Simulación' para comenzar.")
        return

    # --- PANELES DE VISUALIZACIÓN ---
    resultado = st.session_state.resultado
    red = st.session_state.red

    st.subheader("📊 Indicadores Globales")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Fitness Z (Costo/Tramo)", f"{resultado.fitness_final:.2f}")
    col2.metric("Cobertura (Arcos Únicos)", f"{resultado.arcos_unicos_inspeccionados}")
    col3.metric("Batería Consumida", f"{resultado.bateria_consumida_total:.1f} / {bateria_max}")
    col4.metric("Batería Deadheading", f"{resultado.bateria_consumida_deadheading :.1f}")
    col5.metric("Iteraciones Ejecutadas", f"{len(resultado.historial_mejor_global)}")
    col6.metric("Tiempo Computacional", f"{st.session_state.tiempo:.2f} s")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["📈 Convergencia y Fitness", "🗺️ Mapa y Ruta", "🧪 Matriz de Feromonas"])

    with tab1:
        st.plotly_chart(graficar_convergencia(resultado), width='stretch')
        st.caption(r"Nota: El estancamiento prematuro de Z puede indicar una convergencia a óptimo local. Aumentar la penalización $\Omega$ o reducir $\rho$ favorece la exploración.")

    with tab2:
        col_topo, col_ruta = st.columns(2)
        
        with col_topo:
            st.plotly_chart(graficar_topologia_sin_ruta(red), width='stretch')
        
        with col_ruta:
            st.plotly_chart(graficar_ruta_sin_numeros(red, resultado.mejor_ruta_nodos), width='stretch')

        with st.expander("Ver Secuencia de Nodos"):
            st.write(" $\\rightarrow$ ".join(map(str, resultado.mejor_ruta_nodos)))
    with tab3:
        if resultado.matriz_feromonas_final is not None:
            st.plotly_chart(graficar_matriz_feromonas(resultado.matriz_feromonas_final), width='stretch')
            st.caption(r"Los colores más cálidos representan caminos fuertemente reforzados por el depósito elitista $(\Delta\tau = Q/Z_{best})$.")
        else:
            st.warning("La matriz de feromonas no fue exportada en el objeto ResultadoEjecucion.")

if __name__ == "__main__":
    main()