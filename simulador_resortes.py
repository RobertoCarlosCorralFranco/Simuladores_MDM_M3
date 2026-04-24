import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
TEC_RED = '#B22222'
st.set_page_config(page_title="Diseño de Resortes - Tecmilenio", layout="wide")

st.markdown(f"""
    <style>
    .main-title {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 28px; font-weight: bold; text-align: center; }}
    .section-header {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 20px; font-weight: bold; border-bottom: 1.5px solid {TEC_GREEN}; padding-bottom: 5px; margin-top: 20px; }}
    .step-box {{ padding: 20px; border: 1px solid #e6e6e6; border-left: 6px solid {TEC_GREEN}; background-color: #ffffff; margin-bottom: 15px; border-radius: 4px; line-height: 1.6; font-family: 'serif'; }}
    .alert-box {{ padding: 15px; background-color: #f8f9fa; border-left: 6px solid {TEC_RED}; border-radius: 4px; font-weight: bold; color: #333; }}
    .highlight {{ color: {TEC_RED}; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">Tema 14: Diseño de Resortes Helicoidales a Compresión</p>', unsafe_allow_html=True)

# ==========================================
# BASE DE DATOS DE MATERIALES (Empíricos)
# ==========================================
MATERIALES = {
    "Alambre de Piano (A228)": {"A": 2211, "m": 0.145, "G": 79300},
    "Acero Estirado Duro": {"A": 1783, "m": 0.190, "G": 79300},
    "Acero Templado en Aceite": {"A": 1477, "m": 0.187, "G": 77200}
}

# ==========================================
# BARRA LATERAL: CONTROLES DEL PROBLEMA
# ==========================================
st.sidebar.header("1. Material y Carga")
material_sel = st.sidebar.selectbox("Material del Alambre", list(MATERIALES.keys()))
F = st.sidebar.slider("Fuerza Axial Aplicada, F (N)", 0.0, 2000.0, 300.0, step=10.0)

st.sidebar.header("2. Geometría del Resorte")
D = st.sidebar.slider("Diámetro Medio, D (mm)", 10.0, 100.0, 40.0, step=1.0)
d = st.sidebar.slider("Diámetro del Alambre, d (mm)", 1.0, 20.0, 5.0, step=0.5)
N_a = st.sidebar.slider("Espiras Activas, Na", 3.0, 30.0, 10.0, step=0.5)

st.sidebar.header("3. Instalación")
L_0 = st.sidebar.slider("Longitud Libre original, L0 (mm)", 50.0, 500.0, 150.0, step=5.0)
alpha = st.sidebar.selectbox("Condición de los extremos (α)", 
                             options=[0.5, 0.707, 1.0, 2.0], 
                             format_func=lambda x: f"{x} (Placas paralelas)" if x==0.5 else str(x))

st.sidebar.markdown("---")
st.sidebar.caption("Prof. Roberto Carlos Corral Franco\nUniversidad Tecmilenio")

# ==========================================
# CÁLCULOS ANALÍTICOS (TIEMPO REAL)
# ==========================================
# Propiedades del material
mat = MATERIALES[material_sel]
A_const = mat["A"]
m_const = mat["m"]
G_mod = mat["G"]

# Resistencia del material
S_ut = A_const / (d ** m_const)
S_sy = 0.45 * S_ut

# Geometría y Esfuerzos
C = D / d
K_B = (4 * C + 2) / (4 * C - 3)
tau_max = K_B * ((8 * F * D) / (np.pi * d**3))

# Constante y Deflexión
k = (d**4 * G_mod) / (8 * D**3 * N_a)
y_def = F / k
L_actual = L_0 - y_def

# Estabilidad y Longitud Sólida (Asumiendo extremos escuadrados y esmerilados)
N_t = N_a + 2
L_s = d * N_t
L_critica = 2.63 * (D / alpha)

# Factor de seguridad torsional
n_s = S_sy / tau_max if tau_max > 0 else 999.9

# Diagnósticos
es_estable = L_0 < L_critica
es_choque = L_actual <= L_s
falla_fatiga = n_s < 1.0

# ==========================================
# INTERFAZ GRÁFICA (PLOTS)
# ==========================================
col_vis, col_diag = st.columns([1, 1.3])

with col_vis:
    st.markdown('<p class="section-header">Simulación Física</p>', unsafe_allow_html=True)
    
    fig_spring, ax_sp = plt.subplots(figsize=(4, 6))
    
    # Dibujar el resorte helicoidal paramétrico
    t = np.linspace(0, N_a * 2 * np.pi, 1000)
    x_sp = (D / 2) * np.sin(t)
    
    # La longitud de las espiras activas se distribuye en el espacio disponible
    espacio_disp = max(L_s, L_actual)
    y_sp = np.linspace(espacio_disp, d*2, 1000) # De arriba hacia abajo
    
    # Efecto de espesor usando un plot grueso
    color_resorte = TEC_RED if (falla_fatiga or es_choque) else '#004B87'
    ax_sp.plot(x_sp, y_sp, color=color_resorte, linewidth=d*1.5, solid_capstyle='round')
    
    # Placas base y carga
    ax_sp.plot([-D, D], [0, 0], color='black', linewidth=4) # Suelo
    ax_sp.plot([-D, D], [espacio_disp, espacio_disp], color='gray', linewidth=4) # Placa superior
    
    # Vector de fuerza
    if F > 0:
        ax_sp.annotate('', xy=(0, espacio_disp), xytext=(0, espacio_disp + L_0*0.2),
                       arrowprops=dict(facecolor=TEC_RED, edgecolor='none', width=3, headwidth=10))
        ax_sp.text(0, espacio_disp + L_0*0.25, f'F = {F} N', color=TEC_RED, ha='center', fontweight='bold')
    
    # Línea de L_solid
    ax_sp.axhline(L_s, color='orange', linestyle='--', linewidth=1.5)
    ax_sp.text(D*0.6, L_s + 2, f"L. Sólida\n({L_s:.1f} mm)", color='orange', fontsize=8)
    
    ax_sp.set_xlim(-D*1.5, D*1.5)
    ax_sp.set_ylim(-10, L_0 * 1.3)
    ax_sp.axis('off')
    st.pyplot(fig_spring)
    
    # Mensaje de estado
    status_msg = ""
    if es_choque:
        status_msg += "💥 <b>CHOQUE SÓLIDO:</b> El resorte se ha aplastado por completo.<br>"
    if falla_fatiga:
        status_msg += "⚠️ <b>FALLA POR CORTANTE:</b> El esfuerzo supera la fluencia torsional.<br>"
    if not es_estable:
        status_msg += "🐍 <b>ALABEO (PANDEO):</b> El resorte es muy esbelto e inestable.<br>"
    if es_estable and not es_choque and not falla_fatiga:
        status_msg += f"✅ <b>DISEÑO SEGURO.</b> Factor de Seguridad: {n_s:.2f}"
        
    st.markdown(f"""
    <div class="alert-box">
        {status_msg}
    </div>
    """, unsafe_allow_html=True)

with col_diag:
    st.markdown('<p class="section-header">Análisis de Esfuerzo y Deformación</p>', unsafe_allow_html=True)
    
    fig_graf, ax_g = plt.subplots(figsize=(6, 5))
    
    # Puntos para la curva
    y_plot = np.linspace(0, L_0 - L_s, 100)
    F_plot = k * y_plot
    
    # Trazar línea de rigidez
    ax_g.plot(y_plot, F_plot, color=TEC_GREEN, linewidth=2, label=f'Rigidez k = {k:.2f} N/mm')
    
    # Punto de operación actual
    if not es_choque:
        ax_g.plot(y_def, F, 'ro', markersize=8, label='Punto de Operación')
        ax_g.vlines(y_def, 0, F, colors='red', linestyles='dotted')
        ax_g.hlines(F, 0, y_def, colors='red', linestyles='dotted')
    else:
        y_max = L_0 - L_s
        F_max = k * y_max
        ax_g.plot(y_max, F_max, 'ro', markersize=8)
        
    # Zona de choque sólido
    y_solid = L_0 - L_s
    ax_g.axvspan(y_solid, y_solid * 1.2, color='orange', alpha=0.3, label='Zona de Longitud Sólida')
    
    # Límite de fluencia torsional mapeado a Fuerza (F_y = tau_sy * pi * d^3 / (8*D*K_B))
    F_yield = (S_sy * np.pi * d**3) / (8 * D * K_B)
    ax_g.axhline(F_yield, color=TEC_RED, linestyle='--', linewidth=1.5, label=f'Límite de Fluencia ($S_{{sy}}$)')
    
    ax_g.set_xlim(0, max(y_solid * 1.2, y_def * 1.1))
    ax_g.set_ylim(0, max(F_yield * 1.2, F * 1.1))
    ax_g.set_xlabel("Deflexión, $y$ (mm)", fontweight='bold')
    ax_g.set_ylabel("Fuerza Axial, $F$ (N)", fontweight='bold')
    ax_g.grid(True, linestyle=':', alpha=0.6)
    ax_g.legend()
    st.pyplot(fig_graf)

# ==========================================
# DESARROLLO ANALÍTICO
# ==========================================
st.markdown('<p class="section-header">Memoria de Cálculo Analítico</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="step-box">
    <b>Paso 1: Resistencia del Alambre</b><br>
    Utilizando las constantes $A = {A_const}$ y $m = {m_const}$:<br>
    $S_{{ut}} = \\frac{{{A_const}}}{{{d}^{{{m_const}}}}} =$ <b>{S_ut:.1f} MPa</b><br>
    Estimación de fluencia torsional: $S_{{sy}} \\approx 0.45 S_{{ut}} =$ <b>{S_sy:.1f} MPa</b>
</div>
<div class="step-box">
    <b>Paso 2: Geometría y Constante del Resorte ($k$)</b><br>
    Índice del resorte: $C = \\frac{{D}}{{d}} = \\frac{{{D}}}{{{d}}} =$ <b>{C:.2f}</b><br>
    $k = \\frac{{d^4 G}}{{8 D^3 N_a}} = \\frac{{({d})^4 ({G_mod})}}{{8 ({D})^3 ({N_a})}} =$ <b>{k:.2f} N/mm</b><br>
    Deflexión actual: $y = \\frac{{F}}{{k}} = \\frac{{{F}}}{{{k:.2f}}} =$ <b>{y_def:.2f} mm</b>
</div>
<div class="step-box">
    <b>Paso 3: Esfuerzo Cortante Máximo ($\\tau_{{max}}$)</b><br>
    Factor de Bergsträsser: $K_B = \\frac{{4C+2}}{{4C-3}} = \\frac{{4({C:.2f})+2}}{{4({C:.2f})-3}} =$ <b>{K_B:.3f}</b><br>
    $\\tau_{{max}} = K_B \\left( \\frac{{8FD}}{{\\pi d^3}} \\right) = {K_B:.3f} \\left( \\frac{{8({F})({D})}}{{\\pi ({d})^3}} \\right) =$ <b>{tau_max:.1f} MPa</b>
</div>
<div class="step-box">
    <b>Paso 4: Análisis de Estabilidad y Longitud Sólida</b><br>
    Espiras Totales ($N_t = N_a + 2$): <b>{N_t}</b><br>
    Longitud Sólida ($L_s = d \\cdot N_t$): <b>{L_s:.1f} mm</b><br>
    Límite crítico de Pandeo para Acero: $L_{{crit}} = 2.63 \\left( \\frac{{D}}{{\\alpha}} \\right) = 2.63 \\left( \\frac{{{D}}}{{{alpha}}} \\right) =$ <b>{L_critica:.1f} mm</b><br>
    <i>Como $L_0$ ({L_0} mm) es {'menor' if es_estable else 'MAYOR'} que $L_{{crit}}$ ({L_critica:.1f} mm), el resorte {'ES ABSOLUTAMENTE ESTABLE' if es_estable else 'SUFRIRÁ PANDEO'}.</i>
</div>
""", unsafe_allow_html=True)