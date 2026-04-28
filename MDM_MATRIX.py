import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
TEC_RED = '#B22222'
st.set_page_config(page_title="Selección Avanzada - Tecmilenio", layout="wide")

st.markdown(f"""
    <style>
    .main-title {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 28px; font-weight: bold; text-align: center; }}
    .section-header {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 20px; font-weight: bold; border-bottom: 1.5px solid {TEC_GREEN}; padding-bottom: 5px; margin-top: 15px; margin-bottom: 15px; }}
    .winner-box {{ padding: 15px; background-color: #e2f0d9; border: 2px solid {TEC_GREEN}; border-radius: 8px; text-align: center; margin-bottom: 15px; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">Proyecto Final: Matriz de Selección Multidisciplinaria</p>', unsafe_allow_html=True)
st.caption("Prof. Roberto Carlos Corral Franco | Universidad Tecmilenio | Mecánica de Materiales")

# ==========================================
# MOTOR DE LA MATRIZ DE DECISIÓN (FUNCIÓN MAESTRA)
# ==========================================
def calcular_matriz(df, metas, pesos, direcciones):
    """
    df: DataFrame con los materiales.
    metas: Lista de valores objetivo.
    pesos: Lista de pesos (1 a 5).
    direcciones: Lista de 1 (Más es mejor) o -1 (Menos es mejor).
    """
    scores_totales = []
    puntuaciones_radar = []
    
    # Extraer solo las columnas numéricas de evaluación (ignorando Nombre y Categoría)
    cols_eval = df.columns[2:]
    
    for index, row in df.iterrows():
        scores_temp = []
        for i, col in enumerate(cols_eval):
            val = row[col]
            meta = metas[i]
            if direcciones[i] == 1: # Más es mejor
                score = min(100.0, (val / meta) * 100) if meta > 0 else 100.0
            else: # Menos es mejor
                score = min(100.0, (meta / val) * 100) if val > 0 else 100.0
            scores_temp.append(score)
            
        # Promedio ponderado
        peso_total = sum(pesos)
        puntaje_final = sum(s * p for s, p in zip(scores_temp, pesos)) / peso_total
        
        scores_totales.append(round(puntaje_final, 1))
        puntuaciones_radar.append(scores_temp)

    df_resultado = df.copy()
    df_resultado['Compatibilidad (%)'] = scores_totales
    df_sorted = df_resultado.sort_values(by='Compatibilidad (%)', ascending=False).reset_index(drop=True)
    
    ganador = df_sorted.iloc[0]
    ganador_idx = df_resultado.index[df_resultado['Material'] == ganador['Material']].tolist()[0]
    radar_vals = puntuaciones_radar[ganador_idx]
    
    return df_sorted, ganador, radar_vals

def graficar_radar(labels, valores, titulo):
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    valores += valores[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angles, valores, color=TEC_GREEN, linewidth=2)
    ax.fill(angles, valores, color=TEC_GREEN, alpha=0.3)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontweight='bold', fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(['25%', '50%', '75%', '100%'], color="grey", size=7)
    ax.set_title(titulo, y=1.08, fontweight='bold', fontsize=10)
    return fig

# ==========================================
# ESTRUCTURA DE PESTAÑAS (TABS)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Diseño de Vigas", "⚙️ Ejes y Flechas", "🗜️ Resortes Helicoidales", "⚙️ Engranes Rectos"])

# ------------------------------------------
# TAB 1: VIGAS (Flexión y Cortante)
# ------------------------------------------
with tab1:
    st.markdown('<p class="section-header">Selección Estructural para Vigas</p>', unsafe_allow_html=True)
    
    df_vigas = pd.DataFrame({
        "Material": ["Acero A36", "Acero A992 (W)", "Aluminio 6061-T6", "Titanio Ti-6Al-4V", "Madera Estructural", "Concreto Armado"],
        "Categoría": ["Metal", "Metal", "Metal", "Metal", "Orgánico", "Compuesto"],
        "Fluencia Sy (MPa)": [250, 345, 276, 880, 40, 30],
        "Módulo E (GPa)": [200, 200, 70, 114, 11, 25],
        "Densidad (g/cm3)": [7.85, 7.85, 2.70, 4.43, 0.60, 2.40],
        "Costo (USD/kg)": [1.2, 1.5, 4.0, 40.0, 0.5, 0.1]
    })
    
    col1, col2 = st.columns([1, 2.5])
    with col1:
        st.subheader("Metas y Pesos")
        v_sy = st.number_input("Fluencia Mínima (MPa)", value=200, key="v_sy")
        p_sy = st.slider("Importancia Fluencia", 1, 5, 4, key="p_sy")
        
        v_e = st.number_input("Rigidez E Mínima (GPa)", value=100, key="v_e")
        p_e = st.slider("Importancia Deflexión (E)", 1, 5, 3, key="p_e")
        
        v_den = st.number_input("Densidad Máx (g/cm3)", value=8.0, key="v_den")
        p_den = st.slider("Importancia Peso Ligero", 1, 5, 2, key="p_den")
        
        v_cos = st.number_input("Costo Máx (USD/kg)", value=2.0, key="v_cos")
        p_cos = st.slider("Importancia Costo", 1, 5, 4, key="p_cos")
        
    with col2:
        df_res_v, gan_v, rad_v = calcular_matriz(
            df_vigas, 
            [v_sy, v_e, v_den, v_cos], 
            [p_sy, p_e, p_den, p_cos], 
            [1, 1, -1, -1] # 1: Más es mejor, -1: Menos es mejor
        )
        
        c_radar, c_tabla = st.columns([1, 1.5])
        with c_radar:
            st.pyplot(graficar_radar(['Fluencia', 'Rigidez (E)', 'Ligereza', 'Costo'], rad_v, gan_v['Material']))
        with c_tabla:
            st.markdown(f"<div class='winner-box'>🥇 Ganador: <b>{gan_v['Material']}</b> ({gan_v['Compatibilidad (%)']}%)</div>", unsafe_allow_html=True)
            st.dataframe(df_res_v[['Compatibilidad (%)', 'Material', 'Fluencia Sy (MPa)', 'Módulo E (GPa)']].style.background_gradient(subset=['Compatibilidad (%)'], cmap='Greens'), height=200)

# ------------------------------------------
# TAB 2: EJES Y FLECHAS (Fatiga de Goodman)
# ------------------------------------------
with tab2:
    st.markdown('<p class="section-header">Selección para Flechas de Transmisión (Fatiga)</p>', unsafe_allow_html=True)
    
    df_flechas = pd.DataFrame({
        "Material": ["Acero 1020 (CD)", "Acero 4140 (Q&T)", "Acero 4340 (Alta Resistencia)", "Inoxidable 316", "Aluminio 7075-T6", "Titanio Grado 5"],
        "Categoría": ["Bajo Carbono", "Aleado", "Aleado", "Inoxidable", "No Ferroso", "Aleación Especial"],
        "Límite Fatiga Se (MPa)": [200, 450, 500, 280, 160, 510],
        "Sensibilidad Entalla q (1-10)": [4, 7, 9, 5, 8, 6], # Menor es mejor (menos sensible a cuñeros)
        "Maquinabilidad (%)": [70, 55, 45, 50, 90, 30],
        "Costo (USD/kg)": [1.5, 3.0, 4.5, 6.0, 5.0, 45.0]
    })
    
    col1, col2 = st.columns([1, 2.5])
    with col1:
        st.subheader("Metas y Pesos")
        f_se = st.number_input("Límite Fatiga Mín (MPa)", value=300, key="f_se")
        pf_se = st.slider("Importancia Fatiga", 1, 5, 5, key="pf_se")
        
        f_q = st.number_input("Sensibilidad Entalla Máx", value=5, key="f_q")
        pf_q = st.slider("Importancia (Menos Muescas)", 1, 5, 3, key="pf_q")
        
        f_maq = st.number_input("Maquinabilidad Mín (%)", value=50, key="f_maq")
        pf_maq = st.slider("Importancia Manufactura", 1, 5, 2, key="pf_maq")
        
        f_cos = st.number_input("Costo Máx (USD/kg)", value=5.0, key="f_cos")
        pf_cos = st.slider("Importancia Costo", 1, 5, 4, key="pf_cos2")
        
    with col2:
        df_res_f, gan_f, rad_f = calcular_matriz(
            df_flechas, 
            [f_se, f_q, f_maq, f_cos], 
            [pf_se, pf_q, pf_maq, pf_cos], 
            [1, -1, 1, -1] # Sensibilidad y Costo son -1 (Menos es mejor)
        )
        
        c_radar, c_tabla = st.columns([1, 1.5])
        with c_radar:
            st.pyplot(graficar_radar(['Límite Fatiga', 'Baja Sensibilidad', 'Maquinabilidad', 'Costo'], rad_f, gan_f['Material']))
        with c_tabla:
            st.markdown(f"<div class='winner-box'>🥇 Ganador: <b>{gan_f['Material']}</b> ({gan_f['Compatibilidad (%)']}%)</div>", unsafe_allow_html=True)
            st.dataframe(df_res_f[['Compatibilidad (%)', 'Material', 'Límite Fatiga Se (MPa)', 'Sensibilidad Entalla q (1-10)']].style.background_gradient(subset=['Compatibilidad (%)'], cmap='Greens'), height=200)

# ------------------------------------------
# TAB 3: RESORTES HELICOIDALES
# ------------------------------------------
with tab3:
    st.markdown('<p class="section-header">Selección de Alambre para Resortes</p>', unsafe_allow_html=True)
    
    df_resortes = pd.DataFrame({
        "Material": ["Alambre de Piano (A228)", "Templado en Aceite", "Cobre al Berilio", "Bronce Fosforado", "Inoxidable 302"],
        "Categoría": ["Alto Carbono", "Aleado", "No Ferroso", "No Ferroso", "Inoxidable"],
        "Constante A (MPa·mm)": [2211, 1477, 1200, 900, 1700], # Indicador de Sut base
        "Módulo Rigidez G (GPa)": [79.3, 77.2, 48.0, 41.0, 69.0],
        "Resist. Corrosión (1-10)": [3, 4, 9, 8, 10],
        "Costo (USD/kg)": [4.0, 2.5, 35.0, 15.0, 8.0]
    })
    
    col1, col2 = st.columns([1, 2.5])
    with col1:
        st.subheader("Metas y Pesos")
        r_a = st.number_input("Constante A Mínima", value=1500, key="r_a")
        pr_a = st.slider("Importancia Resistencia Base", 1, 5, 4, key="pr_a")
        
        r_g = st.number_input("Módulo Rigidez G (GPa)", value=75.0, key="r_g")
        pr_g = st.slider("Importancia Rigidez Cortante", 1, 5, 4, key="pr_g")
        
        r_corr = st.number_input("Resist. Corrosión Mínima", value=5, key="r_corr")
        pr_corr = st.slider("Importancia Ambiente", 1, 5, 2, key="pr_corr")
        
        r_cos = st.number_input("Costo Máx (USD/kg)", value=5.0, key="r_cos")
        pr_cos = st.slider("Importancia Costo", 1, 5, 3, key="pr_cos3")
        
    with col2:
        df_res_r, gan_r, rad_r = calcular_matriz(
            df_resortes, 
            [r_a, r_g, r_corr, r_cos], 
            [pr_a, pr_g, pr_corr, pr_cos], 
            [1, 1, 1, -1]
        )
        
        c_radar, c_tabla = st.columns([1, 1.5])
        with c_radar:
            st.pyplot(graficar_radar(['Resistencia (A)', 'Rigidez (G)', 'Corrosión', 'Costo'], rad_r, gan_r['Material']))
        with c_tabla:
            st.markdown(f"<div class='winner-box'>🥇 Ganador: <b>{gan_r['Material']}</b> ({gan_r['Compatibilidad (%)']}%)</div>", unsafe_allow_html=True)
            st.dataframe(df_res_r[['Compatibilidad (%)', 'Material', 'Constante A (MPa·mm)', 'Módulo Rigidez G (GPa)']].style.background_gradient(subset=['Compatibilidad (%)'], cmap='Greens'), height=200)

# ------------------------------------------
# TAB 4: ENGRANES RECTOS
# ------------------------------------------
with tab4:
    st.markdown('<p class="section-header">Selección de Material para Engranes</p>', unsafe_allow_html=True)
    
    df_engranes = pd.DataFrame({
        "Material": ["Fundición Gris (Grado 30)", "Acero 1040 (Estructural)", "Acero 8620 (Carburizado)", "Bronce al Aluminio", "Nylamid (Plástico)"],
        "Categoría": ["Fundición", "Acero Base", "Acero Tratado", "No Ferroso", "Polímero"],
        "Dureza Superficial (HB)": [200, 250, 600, 170, 80], # Resistencia al desgaste (Picaduras)
        "Fatiga Flexión Raíz (MPa)": [100, 200, 450, 150, 40], # Ecuación de Lewis/AGMA
        "Absorción Ruido/Impacto (1-10)": [7, 4, 3, 6, 10], # Plásticos y fundiciones absorben más
        "Costo (USD/kg)": [1.0, 2.0, 5.5, 12.0, 4.0]
    })
    
    col1, col2 = st.columns([1, 2.5])
    with col1:
        st.subheader("Metas y Pesos")
        e_hb = st.number_input("Dureza Mínima (HB)", value=250, key="e_hb")
        pe_hb = st.slider("Importancia Desgaste", 1, 5, 5, key="pe_hb")
        
        e_fat = st.number_input("Fatiga Raíz Mínima (MPa)", value=200, key="e_fat")
        pe_fat = st.slider("Importancia Resistencia Diente", 1, 5, 4, key="pe_fat")
        
        e_ruido = st.number_input("Absorción Ruido Mínima", value=5, key="e_ruido")
        pe_ruido = st.slider("Importancia Operación Silenciosa", 1, 5, 2, key="pe_ruido")
        
        e_cos = st.number_input("Costo Máx (USD/kg)", value=3.0, key="e_cos")
        pe_cos = st.slider("Importancia Costo", 1, 5, 3, key="pe_cos4")
        
    with col2:
        df_res_e, gan_e, rad_e = calcular_matriz(
            df_engranes, 
            [e_hb, e_fat, e_ruido, e_cos], 
            [pe_hb, pe_fat, pe_ruido, pe_cos], 
            [1, 1, 1, -1]
        )
        
        c_radar, c_tabla = st.columns([1, 1.5])
        with c_radar:
            st.pyplot(graficar_radar(['Dureza (Desgaste)', 'Fatiga (Raíz)', 'Silencio', 'Costo'], rad_e, gan_e['Material']))
        with c_tabla:
            st.markdown(f"<div class='winner-box'>🥇 Ganador: <b>{gan_e['Material']}</b> ({gan_e['Compatibilidad (%)']}%)</div>", unsafe_allow_html=True)
            st.dataframe(df_res_e[['Compatibilidad (%)', 'Material', 'Dureza Superficial (HB)', 'Fatiga Flexión Raíz (MPa)']].style.background_gradient(subset=['Compatibilidad (%)'], cmap='Greens'), height=200)