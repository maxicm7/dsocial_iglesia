import streamlit as st
import pandas as pd
import numpy as np

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Optimizador de Préstamos Solidarios",
    page_icon="✝️",
    layout="wide"
)

# --- Funciones del Modelo ---

def generar_datos_ficticios(num_solicitudes):
    """Genera un DataFrame con solicitudes de préstamo simuladas."""
    proyectos = [
        "Taller de Costura", "Panadería Comunitaria", "Servicio de Reparaciones",
        "Huerto Urbano Orgánico", "Cuidado de Niños", "Clases de Refuerzo",
        "Tienda de Abarrotes", "Carpintería", "Venta de Comida", "Reciclaje Creativo"
    ]
    data = {
        'ID_Proyecto': range(1, num_solicitudes + 1),
        'Nombre_Proyecto': np.random.choice(proyectos, num_solicitudes, replace=True),
        'Monto_Solicitado': np.random.randint(500, 5001, num_solicitudes),
        'V_Viabilidad': np.random.uniform(1, 10, num_solicitudes).round(1),
        'C_Cohesion_Grupo': np.random.uniform(1, 10, num_solicitudes).round(1),
        'I_Impacto_Comunitario': np.random.uniform(1, 10, num_solicitudes).round(1),
        'N_Nivel_Necesidad': np.random.uniform(1, 10, num_solicitudes).round(1),
        'E_Compromiso': np.random.uniform(1, 10, num_solicitudes).round(1),
    }
    df = pd.DataFrame(data)
    # Asegurar que los montos sean múltiplos de 50 para que se vea más limpio
    df['Monto_Solicitado'] = (df['Monto_Solicitado'] // 50) * 50
    return df

def optimizar_prestamos(df, capital_disponible, pesos):
    """Aplica el algoritmo de optimización para seleccionar los mejores proyectos."""
    # 1. Calcular el IPS para cada proyecto
    df['IPS'] = (
        pesos['w_v'] * df['V_Viabilidad'] +
        pesos['w_c'] * df['C_Cohesion_Grupo'] +
        pesos['w_i'] * df['I_Impacto_Comunitario'] +
        pesos['w_n'] * df['N_Nivel_Necesidad'] +
        pesos['w_e'] * df['E_Compromiso']
    )

    # 2. Calcular la "Eficiencia Solidaria" (IPS por dólar)
    df['Eficiencia_Solidaria'] = df['IPS'] / df['Monto_Solicitado']

    # 3. Ordenar los proyectos por eficiencia descendente
    df_sorted = df.sort_values(by='Eficiencia_Solidaria', ascending=False)

    # 4. Seleccionar proyectos hasta agotar el capital (algoritmo codicioso)
    capital_restante = capital_disponible
    proyectos_aprobados_idx = []
    
    for index, row in df_sorted.iterrows():
        if row['Monto_Solicitado'] <= capital_restante:
            proyectos_aprobados_idx.append(index)
            capital_restante -= row['Monto_Solicitado']
            
    proyectos_aprobados = df.loc[proyectos_aprobados_idx]
    proyectos_rechazados = df.drop(proyectos_aprobados_idx)

    return proyectos_aprobados, proyectos_rechazados, capital_restante

# --- Interfaz de Usuario (Streamlit) ---

st.title("✝️ Simulador de Optimización de Préstamos Solidarios")
st.markdown("""
Esta herramienta simula cómo una fundación puede asignar préstamos sin interés, basándose en la **Doctrina Social de la Iglesia**. 
El objetivo no es el lucro, sino maximizar el **Impacto Social Solidario (ISS)**.
Utilice los controles de la barra lateral para ajustar las prioridades de la Fundación y ver cómo afecta la selección de proyectos.
""")

# --- Barra Lateral de Controles ---
st.sidebar.header("Panel de Control de la Fundación")

capital_total = st.sidebar.slider(
    "Capital Disponible para Préstamos ($)", 5000, 100000, 20000, 1000
)

num_solicitudes = st.sidebar.slider(
    "Número de Solicitudes a Evaluar", 10, 100, 25
)

st.sidebar.markdown("---")
st.sidebar.subheader("Ajustar Prioridades (Pesos del IPS)")
st.sidebar.info("La suma de los pesos no necesita ser 1, el modelo los normalizará, pero refleja la importancia relativa.")

w_v = st.sidebar.slider("Peso de Viabilidad del Proyecto (w_v)", 0.0, 1.0, 0.3, 0.05)
w_c = st.sidebar.slider("Peso de Cohesión del Grupo (w_c)", 0.0, 1.0, 0.2, 0.05)
w_i = st.sidebar.slider("Peso de Impacto Comunitario (w_i)", 0.0, 1.0, 0.2, 0.05)
w_n = st.sidebar.slider("Peso de Nivel de Necesidad (w_n)", 0.0, 1.0, 0.2, 0.05)
w_e = st.sidebar.slider("Peso de Compromiso con el Modelo (w_e)", 0.0, 1.0, 0.1, 0.05)

pesos = {'w_v': w_v, 'w_c': w_c, 'w_i': w_i, 'w_n': w_n, 'w_e': w_e}

# --- Lógica Principal y Visualización ---

# Generar datos para esta simulación
df_solicitudes = generar_datos_ficticios(num_solicitudes)

# Ejecutar la optimización
aprobados_df, rechazados_df, capital_sobrante = optimizar_prestamos(df_solicitudes.copy(), capital_total, pesos)

# Mostrar resultados
st.subheader("Resultados de la Optimización")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Capital Asignado", f"${capital_total - capital_sobrante:,}")
col2.metric("Proyectos Aprobados", f"{len(aprobados_df)}")
col3.metric("Impacto Social Total (IPS)", f"{aprobados_df['IPS'].sum():.2f}")
col4.metric("Capital Sobrante", f"${capital_sobrante:,}")


# Pestañas para ver detalles
tab1, tab2, tab3 = st.tabs(["✅ Proyectos Aprobados", "❌ Proyectos en Lista de Espera", "📊 Visualización"])

with tab1:
    st.markdown(f"**Lista de los {len(aprobados_df)} proyectos seleccionados, ordenados por eficiencia solidaria:**")
    st.dataframe(aprobados_df[['ID_Proyecto', 'Nombre_Proyecto', 'Monto_Solicitado', 'IPS', 'Eficiencia_Solidaria']].style.format({
        'Monto_Solicitado': '${:,.2f}',
        'IPS': '{:.2f}',
        'Eficiencia_Solidaria': '{:.4f}'
    }))

with tab2:
    st.markdown(f"**Lista de los {len(rechazados_df)} proyectos que no pudieron ser financiados en este ciclo:**")
    st.dataframe(rechazados_df[['ID_Proyecto', 'Nombre_Proyecto', 'Monto_Solicitado', 'IPS', 'Eficiencia_Solidaria']].sort_values('Eficiencia_Solidaria', ascending=False).style.format({
        'Monto_Solicitado': '${:,.2f}',
        'IPS': '{:.2f}',
        'Eficiencia_Solidaria': '{:.4f}'
    }))

with tab3:
    st.subheader("Comparación de IPS por Proyecto")
    
    # Combinar dataframes para el gráfico
    aprobados_df['Estado'] = 'Aprobado'
    rechazados_df['Estado'] = 'En Espera'
    chart_df = pd.concat([aprobados_df, rechazados_df]).sort_values('IPS', ascending=False)

    st.bar_chart(
        chart_df,
        x='ID_Proyecto',
        y='IPS',
        color='Estado' # Usa colores para distinguir aprobados de rechazados
    )
    st.caption("El gráfico muestra el IPS de cada proyecto. Los proyectos aprobados son aquellos con la mayor 'eficiencia solidaria' (IPS por dólar) hasta agotar el capital.")

st.markdown("---")
st.subheader("Tabla de Datos Crudos (Solicitudes Originales)")
st.dataframe(df_solicitudes)
