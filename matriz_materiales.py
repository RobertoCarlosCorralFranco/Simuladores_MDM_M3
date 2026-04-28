import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
TEC_RED = '#B22222'
st.set_page_config(page_title="Selección de Materiales - Tecmilenio", layout="wide")

st.markdown(f"""
    <style>
    .main-title {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 28px; font-weight: bold; text-align: center; }}
    .section-header {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 20px; font-weight: bold; border-bottom: 1.5px solid {TEC_GREEN}; padding-bottom: 5px; margin-top: 20px; }}
    .step-box {{ padding: 20px; border: 1px solid #e6e6e6; border-left: 6px solid {TEC_GREEN}; background-color: #ffffff; margin-bottom: 15px; border-radius: 4px; line-height: 1.6; font-family: 'serif'; }}
    .alert-box {{ padding: 15px; background-color: #f8f9fa; border-left: 6px solid {TEC_RED}; border-radius: 4px; font-weight: bold; color: #333; }}
    .winner-box {{ padding: 20px; background-color: #e2f0d9; border: 2px solid {TEC_GREEN}; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">Tema 15: Matriz de Decisión para Selección de Materiales</p>', unsafe_allow_html=True)

# ==========================================
# BASE DE DATOS DE MATERIALES (10 Opciones)
# ==========================================
data = {
    "Material": [
        "Acero ASTM A36 (Bajo Carbono)", "Acero AISI 4140 (Alta Aleación)",
        "Aluminio 6061-T6", "Titanio Ti-6Al-4V", "Cobre C11000",
        "Kevlar 49 / Matriz Epóxica", "Fibra de Carbono (CFRP)",
        "Cerámica Alúmina (Al2O3)", "Nylon 6/6 (Polímero)", "PVC (Polímero)"
    ],
    "Categoría": ["Metal", "Metal", "Metal", "Metal", "Metal", "Compuesto", "Compuesto", "Cerámica", "Polímero", "Polímero"],
    "Resistencia (MPa)": [250.0, 655.0, 276.0, 880.0, 210.0, 1300.0, 1500.0, 300.0, 80.0, 50.0],
    "Ductilidad (%)": [20.0, 15.0, 12.0, 14.0, 45.0, 2.0, 1.0, 0.1, 40.0, 25.0],
    "Costo (USD/kg)": [1.5, 3.0, 4.0, 40.0, 8.0, 50.0, 60.0, 10.0, 4.0, 1.2],
    "Densidad (g/cm3)": [7.85, 7.85, 2.70, 4.43, 8.89, 1.44, 1.60, 3.90, 1.14, 1.35]
}
df_materiales = pd.DataFrame(data)

# ==========================================
# BARRA LATERAL: PARÁMETROS META Y PESOS
# ==========================================
st.sidebar.header("1. Valores Meta (Especificaciones)")
meta_res = st.sidebar.slider("Resistencia Mínima (MPa)", 10, 1500, 200, step=10)
meta_duc = st.sidebar.slider("Ductilidad Mínima (%)", 0, 50, 10, step=1)
meta_cos = st.sidebar.slider("Costo Máximo (USD/kg)", 1.0, 100.0, 5.0, step=1.0)
meta_den = st.sidebar.slider("Densidad Máxima (g/cm³)", 1.0, 10.0, 8.0, step=0.1)

st.sidebar.header("2. Importancia (1 = Baja, 5 = Alta)")
peso_res = st.sidebar.slider("Importancia de Resistencia", 1, 5, 4)
peso_duc = st.sidebar.slider("Importancia de Ductilidad", 1, 5, 2)
peso_cos = st.sidebar.slider("Importancia del Costo", 1, 5, 4)
peso_den = st.sidebar.slider("Importancia de Densidad", 1, 5, 1)

st.sidebar.markdown("---")
st.sidebar.caption("Prof. Roberto Carlos Corral Franco\nUniversidad Tecmilenio")

# ==========================================
# ALGORITMO DE MATRIZ DE DECISIÓN AUTOMÁTICA
# ==========================================
scores_totales = []
puntuaciones_radar = []

for index, row in df_materiales.iterrows():
    # 1. Puntaje Resistencia (Más es mejor)
    s_res = min(100.0, (row['Resistencia (MPa)'] / meta_res) * 100) if meta_res > 0 else 100.0
    
    # 2. Puntaje Ductilidad (Más es mejor)
    s_duc = min(100.0, (row['Ductilidad (%)'] / meta_duc) * 100) if meta_duc > 0 else 100.0
    
    # 3. Puntaje Costo (Menos es mejor - Inverso)
    s_cos = min(100.0, (meta_cos / row['Costo (USD/kg)']) * 100) if row['Costo (USD/kg)'] > 0 else 100.0
    
    # 4. Puntaje Densidad (Menos es mejor - Inverso)
    s_den = min(100.0, (meta_den / row['Densidad (g/cm3)']) * 100) if row['Densidad (g/cm3)'] > 0 else 100.0
    
    # Promedio Ponderado
    peso_total = peso_res + peso_duc + peso_cos + peso_den
    puntaje_final = (s_res * peso_res + s_duc * peso_duc + s_cos * peso_cos + s_den * peso_den) / peso_total
    
    scores_totales.append(round(puntaje_final, 1))
    puntuaciones_radar.append([s_res, s_duc, s_cos, s_den])

# Asignar resultados al DataFrame y ordenar de Mejor a Peor
df_materiales['Compatibilidad (%)'] = scores_totales
df_sorted = df_materiales.sort_values(by='Compatibilidad (%)', ascending=False).reset_index(drop=True)

# Extraer el ganador
ganador = df_sorted.iloc[0]
ganador_idx = df_materiales.index[df_materiales['Material'] == ganador['Material']].tolist()[0]
ganador_radar = puntuaciones_radar[ganador_idx]

# ==========================================
# INTERFAZ GRÁFICA (PLOTS Y TABLAS)
# ==========================================
col_tabla, col_graf = st.columns([1.5, 1])

with col_tabla:
    st.markdown(f"""
    <div class="winner-box">
        <h3 style='margin:0; color:{TEC_GREEN};'>Material Óptimo Seleccionado</h3>
        <h1 style='margin:5px 0;'>{ganador['Material']}</h1>
        <p style='margin:0; font-size:18px;'>Compatibilidad con el Proyecto: <b>{ganador['Compatibilidad (%)']}%</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">Matriz de Decisión Automatizada (Ranking)</p>', unsafe_allow_html=True)
    
    # Formatear la tabla para visualización
    df_display = df_sorted[['Compatibilidad (%)', 'Material', 'Categoría', 'Resistencia (MPa)', 'Ductilidad (%)', 'Costo (USD/kg)', 'Densidad (g/cm3)']]
    st.dataframe(df_display.style.background_gradient(subset=['Compatibilidad (%)'], cmap='Greens'), use_container_width=True, height=380)

with col_graf:
    st.markdown('<p class="section-header">Perfil de Desempeño del Material Óptimo</p>', unsafe_allow_html=True)
    
    # Crear Gráfico de Radar (Spider Plot) con Matplotlib
    labels = ['Resistencia', 'Ductilidad', 'Costo\n(Ahorro)', 'Ligereza\n(Baja Densidad)']
    num_vars = len(labels)
    
    # Calcular ángulos para cada eje
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    
    # Cerrar el polígono
    ganador_radar += ganador_radar[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    
    # Dibujar contorno y rellenar
    ax.plot(angles, ganador_radar, color=TEC_GREEN, linewidth=2)
    ax.fill(angles, ganador_radar, color=TEC_GREEN, alpha=0.3)
    
    # Configurar diseño del radar
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontweight='bold', fontsize=10)
    
    # Escala de 0 a 100%
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], color="grey", size=8)
    
    ax.set_title(f"Cumplimiento de Metas: {ganador['Material']}", y=1.08, fontweight='bold', fontsize=11)
    st.pyplot(fig)

# ==========================================
# CASOS DE ESTUDIO (GUÍA EDUCATIVA)
# ==========================================
st.markdown('<p class="section-header">Casos de Estudio para la Clase</p>', unsafe_allow_html=True)

col_c1, col_c2 = st.columns(2)

with col_c1:
    st.markdown(f"""
    <div class="step-box">
        <b style="color:{TEC_GREEN}; font-size:18px;">Ejemplo 1: Tanque de Compresor</b><br>
        <i>Objetivo: Contener presión de forma económica y segura.</i><br><br>
        <b>Configuración sugerida en controles:</b><br>
        • <b>Metas:</b> Resistencia media (250 MPa), Ductilidad media (15%), Costo muy bajo ($2 USD/kg). Densidad irrelevante (10 g/cm³).<br>
        • <b>Pesos:</b> Resistencia (4), Ductilidad (3), Costo (5), Densidad (1).<br><br>
        <i>Al configurar esto, el algoritmo detectará automáticamente que el <b>Acero ASTM A36</b> vence a las cerámicas (por ductilidad) y al Titanio (por costo), coronándose como el #1.</i>
    </div>
    """, unsafe_allow_html=True)

with col_c2:
    st.markdown(f"""
    <div class="step-box">
        <b style="color:{TEC_RED}; font-size:18px;">Ejemplo 2: Recipiente Aeroespacial</b><br>
        <i>Objetivo: Soportar presión extrema con el mínimo peso posible, sin importar el costo.</i><br><br>
        <b>Configuración sugerida en controles:</b><br>
        • <b>Metas:</b> Resistencia extrema (1000 MPa), Ductilidad baja (2%), Costo irrelevante ($100 USD/kg). Densidad ultrabaja (1.5 g/cm³).<br>
        • <b>Pesos:</b> Resistencia (5), Ductilidad (1), Costo (1), Densidad (5).<br><br>
        <i>Bajo esta configuración estricta, los metales caen al fondo por su peso, y los materiales compuestos como el <b>Kevlar 49</b> o <b>CFRP</b> tomarán el liderazgo indiscutible.</i>
    </div>
    """, unsafe_allow_html=True)