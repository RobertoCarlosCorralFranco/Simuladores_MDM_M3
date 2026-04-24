import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
TEC_RED = '#B22222'
st.set_page_config(page_title="Diseño de Vigas - Tecmilenio", layout="wide")

st.markdown(f"""
    <style>
    .main-title {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 28px; font-weight: bold; text-align: center; }}
    .section-header {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 20px; font-weight: bold; border-bottom: 1.5px solid {TEC_GREEN}; padding-bottom: 5px; margin-top: 20px; }}
    .step-box {{ padding: 20px; border: 1px solid #e6e6e6; border-left: 6px solid {TEC_GREEN}; background-color: #ffffff; margin-bottom: 15px; border-radius: 4px; line-height: 1.6; font-family: 'serif'; }}
    .alert-box {{ padding: 15px; background-color: #f8f9fa; border-left: 6px solid {TEC_RED}; border-radius: 4px; font-weight: bold; color: #333; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">Tema 12: Diseño de Vigas y Análisis de Fallas</p>', unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL: CONTROLES DEL PROBLEMA
# ==========================================
st.sidebar.header("1. Geometría de la Sección (T)")
b_f = st.sidebar.slider("Ancho del patín (mm)", 50.0, 300.0, 150.0, step=5.0) / 1000
t_f = st.sidebar.slider("Espesor del patín (mm)", 10.0, 100.0, 30.0, step=2.0) / 1000
h_w = st.sidebar.slider("Altura del alma (mm)", 50.0, 300.0, 120.0, step=5.0) / 1000
t_w = st.sidebar.slider("Espesor del alma (mm)", 10.0, 100.0, 40.0, step=2.0) / 1000

st.sidebar.header("2. Condiciones de Carga y Material")
L = st.sidebar.slider("Longitud de la viga (m)", 2.0, 12.0, 8.0, step=0.5)
sigma_perm = st.sidebar.number_input("Esfuerzo Normal Permisible (MPa)", value=30.0)
tau_perm = st.sidebar.number_input("Esfuerzo Cortante Permisible (kPa)", value=800.0)

st.sidebar.markdown("---")
st.sidebar.caption("Prof. Roberto Carlos Corral Franco\nUniversidad Tecmilenio")

# ==========================================
# CÁLCULOS ANALÍTICOS (TIEMPO REAL)
# ==========================================
# 1. Áreas y Centroide (Referencia: fibra superior hacia abajo)
A1 = b_f * t_f
y1 = t_f / 2
A2 = t_w * h_w
y2 = t_f + (h_w / 2)

A_tot = A1 + A2
y_bar = (A1 * y1 + A2 * y2) / A_tot  # Distancia del eje neutro desde arriba

# 2. Momento de Inercia (Teorema de Ejes Paralelos)
I1 = (b_f * t_f**3) / 12 + A1 * (y_bar - y1)**2
I2 = (t_w * h_w**3) / 12 + A2 * (y2 - y_bar)**2
I_tot = I1 + I2

# 3. Distancia a la fibra más extrema (c)
c_top = y_bar
c_bot = (t_f + h_w) - y_bar
c_max = max(c_top, c_bot)

# 4. Primer Momento de Área (Q) en el Eje Neutro
y_prime = c_bot / 2
A_prime = t_w * c_bot
Q = y_prime * A_prime

# 5. Cálculo de Cargas Máximas (P)
M_coeff = L / 4
P_flexion = (sigma_perm * 1e6 * I_tot) / (M_coeff * c_max)

V_coeff = 0.5
P_cortante = (tau_perm * 1e3 * I_tot * t_w) / (V_coeff * Q)

# Carga Crítica
P_max = min(P_flexion, P_cortante)
falla_por = "FLEXIÓN" if P_flexion < P_cortante else "CORTANTE"

# ==========================================
# INTERFAZ GRÁFICA (PLOTS)
# ==========================================
col_geom, col_diag = st.columns([1, 1.2])

with col_geom:
    st.markdown('<p class="section-header">Geometría y Vistas de la Viga</p>', unsafe_allow_html=True)
    
    # --- VISTA TRANSVERSAL ---
    fig_sec, ax_sec = plt.subplots(figsize=(5, 4))
    
    # Dibujar Patín
    ax_sec.add_patch(patches.Rectangle((-b_f/2, t_f + h_w - t_f), b_f, t_f, linewidth=2, edgecolor='black', facecolor='#fce4d6'))
    # Dibujar Alma
    ax_sec.add_patch(patches.Rectangle((-t_w/2, 0), t_w, h_w, linewidth=2, edgecolor='black', facecolor='#fce4d6'))
    
    # Eje Neutro
    y_na = (t_f + h_w) - y_bar # Coordenada Y del eje neutro desde abajo
    ax_sec.axhline(y_na, color=TEC_GREEN, linestyle='--', linewidth=2.5, label=f'Eje Neutro (EN)\n a {y_bar*1000:.1f} mm del tope')
    
    ax_sec.set_xlim(-max(b_f, h_w), max(b_f, h_w))
    ax_sec.set_ylim(-0.02, t_f + h_w + 0.05)
    ax_sec.set_aspect('equal')
    ax_sec.axis('off')
    ax_sec.set_title("Sección Transversal", fontsize=11, fontweight='bold')
    ax_sec.legend(loc='upper right', fontsize=9)
    st.pyplot(fig_sec)

    # --- VISTA LATERAL (NUEVO) ---
    fig_lat, ax_lat = plt.subplots(figsize=(5, 2.5))
    H_tot = t_f + h_w
    
    # Dibujar Viga (Lateral)
    # Patín (color sólido)
    ax_lat.add_patch(patches.Rectangle((0, H_tot - t_f), L, t_f, linewidth=1, edgecolor='black', facecolor='#fce4d6'))
    # Alma (ligeramente transparente para distinguir)
    ax_lat.add_patch(patches.Rectangle((0, 0), L, H_tot - t_f, linewidth=1, edgecolor='black', facecolor='#fce4d6', alpha=0.7))
    
    # Eje Neutro a lo largo de la viga
    ax_lat.axhline(H_tot - y_bar, color=TEC_GREEN, linestyle='--', linewidth=2)
    
    # Apoyos (Triángulos)
    w_sup = L * 0.05
    h_sup = H_tot * 0.2
    ax_lat.add_patch(patches.Polygon([[0, 0], [-w_sup/2, -h_sup], [w_sup/2, -h_sup]], closed=True, color='#555555'))
    ax_lat.add_patch(patches.Polygon([[L, 0], [L-w_sup/2, -h_sup], [L+w_sup/2, -h_sup]], closed=True, color='#555555'))
    
    # Carga P (Flecha en el centro)
    ax_lat.annotate(f'P = {P_max/1000:.2f} kN', xy=(L/2, H_tot), xytext=(L/2, H_tot + H_tot*0.5),
                    arrowprops=dict(facecolor=TEC_RED, edgecolor='none', shrink=0.0, width=3, headwidth=8),
                    ha='center', va='bottom', color=TEC_RED, fontweight='bold', fontsize=10)
    
    ax_lat.set_xlim(-L*0.1, L*1.1)
    ax_lat.set_ylim(-h_sup*1.5, H_tot + H_tot*0.8)
    ax_lat.axis('off')
    ax_lat.set_title("Vista Lateral (Longitudinal)", fontsize=11, fontweight='bold')
    st.pyplot(fig_lat)
    
    # --- CAJA DE DECISIÓN ---
    st.markdown(f"""
    <div class="alert-box">
        <h4 style='margin-top:0;'>Decisión de Ingeniería</h4>
        Límite por Flexión: <b>{P_flexion/1000:.3f} kN</b><br>
        Límite por Cortante: <b>{P_cortante/1000:.3f} kN</b><br>
        <hr style='margin:10px 0;'>
        Carga máxima segura: <span style='color:{TEC_RED}; font-size:1.2em;'>P = {P_max/1000:.3f} kN</span><br>
        Modo de falla inminente: <b>{falla_por}</b>
    </div>
    """, unsafe_allow_html=True)

with col_diag:
    st.markdown('<p class="section-header">Diagramas V y M (para Carga Segura P)</p>', unsafe_allow_html=True)
    
    x = np.linspace(0, L, 500)
    # Reacciones
    R = P_max / 2
    
    # Cortante (V)
    V = np.where(x < L/2, R, -R)
    
    # Momento (M)
    M = np.where(x < L/2, R * x, R * L/2 - R * (x - L/2))
    
    fig_vm, (ax_v, ax_m) = plt.subplots(2, 1, figsize=(6, 8.5), sharex=True)
    
    # Plot V
    ax_v.fill_between(x, 0, V/1000, color='#99ccff', alpha=0.5)
    ax_v.plot(x, V/1000, color='#004B87', linewidth=2)
    ax_v.axhline(0, color='black', linewidth=1)
    ax_v.set_ylabel("Cortante V (kN)", fontweight='bold')
    ax_v.set_title("Fuerza Cortante", fontsize=11)
    ax_v.grid(True, linestyle=':', alpha=0.6)
    
    # Plot M
    ax_m.fill_between(x, 0, M/1000, color='#a8e6cf', alpha=0.5)
    ax_m.plot(x, M/1000, color=TEC_GREEN, linewidth=2)
    ax_m.axhline(0, color='black', linewidth=1)
    ax_m.set_ylabel("Momento M (kN·m)", fontweight='bold')
    ax_m.set_xlabel("Longitud de la Viga (m)", fontweight='bold')
    ax_m.set_title("Momento Flector", fontsize=11)
    ax_m.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    st.pyplot(fig_vm)

# ==========================================
# DESARROLLO ANALÍTICO
# ==========================================
st.markdown('<p class="section-header">Memoria de Cálculo Analítico</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="step-box">
    <b>Paso 1: Cálculo del Centroide ($\\bar{{y}}$)</b><br>
    Se ubica el nivel de referencia en la fibra superior. Se divide en dos áreas:<br>
    $A_1$ (Patín) = {A1*10**6:.1f} mm² | $\\tilde{{y}}_1$ = {y1*1000:.1f} mm <br>
    $A_2$ (Alma) = {A2*10**6:.1f} mm² | $\\tilde{{y}}_2$ = {y2*1000:.1f} mm <br>
    $\\bar{{y}} = \\frac{{\\sum \\tilde{{y}} A}}{{\\sum A}} = $ <b>{y_bar*1000:.2f} mm</b>
</div>
<div class="step-box">
    <b>Paso 2: Momento Polar de Inercia Total ($I_x$)</b><br>
    Aplicando el Teorema de Ejes Paralelos ($I_x = \\bar{{I}} + Ad^2$):<br>
    $I_1$ (Patín) = {I1*10**12:.2f} $\\times 10^4$ mm⁴<br>
    $I_2$ (Alma) = {I2*10**12:.2f} $\\times 10^4$ mm⁴<br>
    $I_{{total}} = $ <b>{I_tot*10**12:.2f} $\\times 10^4$ mm⁴</b> (equivale a {I_tot:.6e} m⁴)
</div>
<div class="step-box">
    <b>Paso 3: Comprobación por Flexión ($\\sigma_{{perm}}$)</b><br>
    Fibra crítica ($c$) = {c_max*1000:.2f} mm.<br>
    $\\sigma = \\frac{{M c}}{{I}}$ donde $M_{{max}} = \\frac{{PL}}{{4}}$. Despejando $P$:<br>
    $P_{{flex}} = \\frac{{4 \\sigma_{{perm}} I}}{{L c}} = $ <b>{P_flexion/1000:.3f} kN</b>
</div>
<div class="step-box">
    <b>Paso 4: Comprobación por Cortante ($\\tau_{{perm}}$)</b><br>
    Primer momento de área ($Q$) = {Q*10**9:.2f} $\\times 10^3$ mm³.<br>
    $\\tau = \\frac{{V Q}}{{I t}}$ donde $V_{{max}} = \\frac{{P}}{{2}}$. Despejando $P$:<br>
    $P_{{cortante}} = \\frac{{2 \\tau_{{perm}} I t}}{{Q}} = $ <b>{P_cortante/1000:.3f} kN</b>
</div>
""", unsafe_allow_html=True)