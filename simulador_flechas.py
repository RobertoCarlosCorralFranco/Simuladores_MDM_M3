import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
TEC_RED = '#B22222'
st.set_page_config(page_title="Diseño de Flechas - Tecmilenio", layout="wide")

st.markdown(f"""
    <style>
    .main-title {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 28px; font-weight: bold; text-align: center; }}
    .section-header {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 20px; font-weight: bold; border-bottom: 1.5px solid {TEC_GREEN}; padding-bottom: 5px; margin-top: 20px; }}
    .step-box {{ padding: 20px; border: 1px solid #e6e6e6; border-left: 6px solid {TEC_GREEN}; background-color: #ffffff; margin-bottom: 15px; border-radius: 4px; line-height: 1.6; font-family: 'serif'; }}
    .alert-box {{ padding: 15px; background-color: #f8f9fa; border-left: 6px solid {TEC_RED}; border-radius: 4px; font-weight: bold; color: #333; }}
    .highlight {{ color: {TEC_RED}; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">Tema 13: Diseño de Flechas por Fatiga (Goodman Modificado)</p>', unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL: CONTROLES DEL PROBLEMA
# ==========================================
st.sidebar.header("1. Cargas Operativas")
# Por defecto: Ejercicio 3 de la presentación
M_a = st.sidebar.slider("Momento Flexionante Alternante, Ma (N·m)", 0.0, 500.0, 70.0, step=5.0)
T_m = st.sidebar.slider("Par de Torsión Medio, Tm (N·m)", 0.0, 500.0, 45.0, step=5.0)

st.sidebar.header("2. Propiedades del Material")
S_ut = st.sidebar.number_input("Resistencia Última, Sut (MPa)", value=500.0, step=10.0)
S_e = st.sidebar.number_input("Límite de Fatiga, Se (MPa)", value=200.0, step=10.0)

st.sidebar.header("3. Concentradores y Seguridad")
K_f = st.sidebar.slider("Concentrador Flexión (Kf)", 1.0, 3.0, 1.5, step=0.1)
K_fs = st.sidebar.slider("Concentrador Torsión (Kfs)", 1.0, 3.0, 1.2, step=0.1)
n = st.sidebar.slider("Factor de Seguridad (n)", 1.0, 5.0, 2.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.caption("Prof. Roberto Carlos Corral Franco\nUniversidad Tecmilenio")

# ==========================================
# CÁLCULOS ANALÍTICOS (TIEMPO REAL)
# ==========================================
# Ecuación de Goodman para flecha sólida (flexión reversible, torsión constante)
# d = ( (16*n / pi) * ( (2*Kf*Ma)/Se + (sqrt(3)*Kfs*Tm)/Sut ) )^(1/3)

term_a = (2 * K_f * M_a) / (S_e * 1e6)
term_m = (np.sqrt(3) * K_fs * T_m) / (S_ut * 1e6)

d_m = ( (16 * n / np.pi) * (term_a + term_m) )**(1/3)
d_mm = d_m * 1000

# Cálculo de esfuerzos equivalentes de von Mises (usando el diámetro calculado)
# Para graficar en el diagrama de Goodman
sigma_a_prime = (16 / (np.pi * d_m**3)) * (2 * K_f * M_a) / 1e6 # en MPa
sigma_m_prime = (16 / (np.pi * d_m**3)) * (np.sqrt(3) * K_fs * T_m) / 1e6 # en MPa

# ==========================================
# INTERFAZ GRÁFICA (PLOTS)
# ==========================================
col_diag, col_vis = st.columns([1.2, 1])

with col_diag:
    st.markdown('<p class="section-header">Diagrama de Fatiga de Goodman</p>', unsafe_allow_html=True)
    
    fig_goodman, ax_g = plt.subplots(figsize=(6, 5))
    
    # Línea de Falla Goodman (n=1)
    ax_g.plot([0, S_ut], [S_e, 0], color=TEC_RED, linewidth=2.5, label='Línea de Falla (Goodman)')
    
    # Línea de Diseño Seguro (n)
    S_e_n = S_e / n
    S_ut_n = S_ut / n
    ax_g.plot([0, S_ut_n], [S_e_n, 0], color=TEC_GREEN, linestyle='--', linewidth=2, label=f'Línea de Diseño (n={n})')
    
    # Zona Segura (Sombreado)
    ax_g.fill_between([0, S_ut_n], [S_e_n, 0], color='#e2f0d9', alpha=0.5)
    
    # Punto de Operación (Esfuerzos Equivalentes)
    ax_g.plot(sigma_m_prime, sigma_a_prime, 'bo', markersize=8, label='Punto de Operación')
    ax_g.plot([0, sigma_m_prime], [0, sigma_a_prime], 'b:', linewidth=1.5) # Línea de carga
    
    # Anotaciones
    ax_g.annotate(f"({sigma_m_prime:.1f}, {sigma_a_prime:.1f}) MPa", 
                  (sigma_m_prime, sigma_a_prime), xytext=(10, 10), textcoords='offset points', fontsize=9)
    
    ax_g.set_xlim(0, S_ut * 1.1)
    ax_g.set_ylim(0, S_e * 1.1)
    ax_g.set_xlabel("Esfuerzo Medio Equivalente, $\\sigma'_m$ (MPa)", fontweight='bold')
    ax_g.set_ylabel("Esfuerzo Alternante Equivalente, $\\sigma'_a$ (MPa)", fontweight='bold')
    ax_g.grid(True, linestyle=':', alpha=0.6)
    ax_g.legend()
    st.pyplot(fig_goodman)

with col_vis:
    st.markdown('<p class="section-header">Dimensionamiento de la Flecha</p>', unsafe_allow_html=True)
    
    # Visualización Geométrica de la Flecha
    fig_shaft, ax_s = plt.subplots(figsize=(5, 3))
    
    # Proporciones visuales
    radio = d_mm / 2
    longitud = max(100, d_mm * 5)
    
    # Dibujar flecha central
    rect = patches.Rectangle((0, -radio), longitud, d_mm, facecolor='#cccccc', edgecolor='black', linewidth=1.5)
    ax_s.add_patch(rect)
    
    # Dibujar rodamientos/apoyos en los extremos para contexto
    ax_s.add_patch(patches.Rectangle((longitud*0.1, -radio*1.4), longitud*0.1, d_mm*1.4, facecolor='#444444'))
    ax_s.add_patch(patches.Rectangle((longitud*0.8, -radio*1.4), longitud*0.1, d_mm*1.4, facecolor='#444444'))
    
    # Acotación del diámetro
    ax_s.annotate('', xy=(longitud*0.5, -radio), xytext=(longitud*0.5, radio),
                  arrowprops=dict(arrowstyle='<->', color=TEC_RED, lw=2))
    ax_s.text(longitud*0.52, 0, f"d = {d_mm:.2f} mm", color=TEC_RED, fontweight='bold', va='center')
    
    # Línea central
    ax_s.plot([-longitud*0.1, longitud*1.1], [0, 0], 'k-.', lw=1, alpha=0.5)
    
    ax_s.set_xlim(-longitud*0.1, longitud*1.1)
    ax_s.set_ylim(-max(30, radio*2), max(30, radio*2))
    ax_s.axis('off')
    st.pyplot(fig_shaft)
    
    st.markdown(f"""
    <div class="alert-box">
        <h4 style='margin-top:0;'>Decisión de Ingeniería</h4>
        Para evitar la falla por fatiga bajo una vida infinita con un factor de seguridad de {n}:<br><br>
        Diámetro Mínimo Requerido: <span style='color:{TEC_RED}; font-size:1.4em;'>{d_mm:.2f} mm</span><br>
        <i>(Aproximar al tamaño de rodamiento estándar superior)</i>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# DESARROLLO ANALÍTICO
# ==========================================
st.markdown('<p class="section-header">Memoria de Cálculo Analítico (Ecuación Maestra)</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="step-box">
    <b>Paso 1: Identificación de Cargas y Concentradores</b><br>
    Flexión (Alternante): $M_a$ = {M_a} N·m, $K_f$ = {K_f}<br>
    Torsión (Media): $T_m$ = {T_m} N·m, $K_{{fs}}$ = {K_fs}<br>
    <i>Nota: Se asume que el eje rota, por lo que el momento flector se invierte completamente ($M_m = 0$) y la torsión es constante ($T_a = 0$).</i>
</div>
<div class="step-box">
    <b>Paso 2: Ecuación de Goodman Modificada para Flechas</b><br>
    Aplicando la Teoría de Energía de Distorsión y despejando el diámetro ($d$):<br>
    $d = \\left( \\frac{{16n}}{{\\pi}} \\left[ \\frac{{\\sqrt{{4(K_f M_a)^2}}}}{{S_e}} + \\frac{{\\sqrt{{3(K_{{fs}} T_m)^2}}}}{{S_{{ut}}}} \\right] \\right)^{{1/3}}$<br><br>
    Sustituyendo valores:<br>
    $d = \\left( \\frac{{16({n})}}{{\\pi}} \\left[ \\frac{{2({K_f})({M_a})}}{{ {S_e} \\times 10^6 }} + \\frac{{\\sqrt{{3}}({K_fs})({T_m})}}{{ {S_ut} \\times 10^6 }} \\right] \\right)^{{1/3}}$
</div>
<div class="step-box">
    <b>Paso 3: Esfuerzos Equivalentes de Operación (Verificación en Diagrama)</b><br>
    Utilizando el diámetro calculado ($d = {d_m:.5f}$ m), los esfuerzos de von Mises en la fibra crítica son:<br>
    Esfuerzo Medio Equivalente ($\\sigma'_m$): <b>{sigma_m_prime:.2f} MPa</b><br>
    Esfuerzo Alternante Equivalente ($\\sigma'_a$): <b>{sigma_a_prime:.2f} MPa</b><br>
    <i>Como se observa en el diagrama superior, este punto de operación cae exactamente sobre la Línea de Diseño, validando el Factor de Seguridad $n={n}$.</i>
</div>
""", unsafe_allow_html=True)