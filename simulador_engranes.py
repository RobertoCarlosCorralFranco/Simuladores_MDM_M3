import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
TEC_RED = '#B22222'
st.set_page_config(page_title="Diseño de Engranes - Tecmilenio", layout="wide")

st.markdown(f"""
    <style>
    .main-title {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 28px; font-weight: bold; text-align: center; }}
    .section-header {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 20px; font-weight: bold; border-bottom: 1.5px solid {TEC_GREEN}; padding-bottom: 5px; margin-top: 20px; }}
    .step-box {{ padding: 20px; border: 1px solid #e6e6e6; border-left: 6px solid {TEC_GREEN}; background-color: #ffffff; margin-bottom: 15px; border-radius: 4px; line-height: 1.6; font-family: 'serif'; }}
    .alert-box {{ padding: 15px; background-color: #f8f9fa; border-left: 6px solid {TEC_RED}; border-radius: 4px; font-weight: bold; color: #333; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">Tema 15: Diseño y Cinemática de Engranes Rectos</p>', unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL: CONTROLES DEL PROBLEMA
# ==========================================
st.sidebar.header("1. Geometría del Diente")
modulo = st.sidebar.slider("Módulo, m (mm)", 1.0, 10.0, 4.0, step=0.5)

st.sidebar.header("2. Tren de Engranes")
N1 = st.sidebar.slider("Dientes del Piñón (N1)", 12, 40, 18, step=1)
# MODIFICACIÓN: Límite superior ampliado a 200 dientes para permitir relaciones 8:1
N2 = st.sidebar.slider("Dientes de la Rueda (N2)", 12, 200, 54, step=1)

st.sidebar.header("3. Potencia y Velocidad")
omega1 = st.sidebar.slider("Vel. de Entrada Piñón, ω1 (RPM)", 100, 3500, 1750, step=50)

st.sidebar.markdown("---")
st.sidebar.caption("Prof. Roberto Carlos Corral Franco\nUniversidad Tecmilenio")

# ==========================================
# CÁLCULOS ANALÍTICOS (TIEMPO REAL)
# ==========================================
# 1. Geometría de Paso
d1 = modulo * N1
d2 = modulo * N2
C = (d1 + d2) / 2
paso_circular = np.pi * modulo

# 2. Nomenclatura del Diente (Estándar AGMA)
a = modulo               # Addendum (Cabeza)
b = 1.25 * modulo        # Dedendum (Raíz)
do1 = d1 + 2 * a         # Diámetro exterior Piñón
do2 = d2 + 2 * a         # Diámetro exterior Rueda
dr1 = d1 - 2 * b         # Diámetro raíz Piñón
dr2 = d2 - 2 * b         # Diámetro raíz Rueda

# 3. Cinemática y Relación
relacion_mG = N2 / N1
omega2 = omega1 * (N1 / N2)

tipo_tren = "REDUCTOR de Velocidad" if N1 < N2 else "MULTIPLICADOR de Velocidad" if N1 > N2 else "TRANSMISIÓN 1:1"
color_tren = TEC_GREEN if N1 < N2 else TEC_RED

# ==========================================
# INTERFAZ GRÁFICA (PLOTS)
# ==========================================
col_vis, col_calc = st.columns([1.3, 1])

with col_vis:
    st.markdown('<p class="section-header">Simulación de Acoplamiento (Malla)</p>', unsafe_allow_html=True)
    
    fig_gear, ax_g = plt.subplots(figsize=(7, 5))
    
    # Función para generar el perfil visual del engrane (Trapezoidal simplificado)
    def get_gear_coords(x_c, y_c, r_pitch, m_val, N, offset_angle):
        theta = np.linspace(0, 2*np.pi, 2000)
        wave = np.sin(N * theta + offset_angle)
        wave = np.clip(wave * 1.5, -1, 1) # Forma trapezoidal
        # r_pitch + addendum (si es pico) o - dedendum (si es valle)
        r = r_pitch + np.where(wave > 0, a * wave, b * wave)
        return x_c + r * np.cos(theta), y_c + r * np.sin(theta)

    # El Piñón está en el origen (0,0)
    # Su punto de contacto está en (d1/2, 0). Queremos un diente aquí: sin(0 + offset) = 1 -> offset = pi/2
    x1, y1 = get_gear_coords(0, 0, d1/2, modulo, N1, np.pi/2)
    ax_g.plot(x1, y1, color='#004B87', linewidth=1.5)
    ax_g.fill(x1, y1, color='#004B87', alpha=0.2)
    
    # La Rueda está en (C, 0)
    # Su punto de contacto respecto a su centro es ángulo PI. Queremos un valle: sin(N2*PI + offset) = -1
    offset_rueda = (3*np.pi/2) - (N2 * np.pi)
    x2, y2 = get_gear_coords(C, 0, d2/2, modulo, N2, offset_rueda)
    ax_g.plot(x2, y2, color=TEC_GREEN, linewidth=1.5)
    ax_g.fill(x2, y2, color=TEC_GREEN, alpha=0.2)
    
    # Dibujar Círculos de Paso (Pitch Circles)
    ax_g.add_patch(patches.Circle((0, 0), d1/2, fill=False, linestyle='-.', color='black', alpha=0.5))
    ax_g.add_patch(patches.Circle((C, 0), d2/2, fill=False, linestyle='-.', color='black', alpha=0.5))
    
    # Marcar Centros y Ejes
    ax_g.plot(0, 0, 'ko', markersize=5)
    ax_g.plot(C, 0, 'ko', markersize=5)
    ax_g.plot([0, C], [0, 0], 'k--', alpha=0.5)
    
    # Acotar Distancia entre Centros (C)
    ax_g.annotate('', xy=(0, min(-d1/2, -d2/2)*1.1), xytext=(C, min(-d1/2, -d2/2)*1.1),
                  arrowprops=dict(arrowstyle='<->', color=TEC_RED))
    ax_g.text(C/2, min(-d1/2, -d2/2)*1.15, f'C = {C:.1f} mm', ha='center', color=TEC_RED, fontweight='bold')
    
    # Flechas de Rotación
    ax_g.annotate('', xy=(0, d1/2*0.6), xytext=(-d1/2*0.6, 0),
                  arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.5", color='#004B87', lw=2))
    ax_g.text(-d1/2*0.6, d1/2*0.6, f"$\omega_1$\n{omega1} RPM", color='#004B87', ha='right', fontweight='bold')

    ax_g.annotate('', xy=(C + d2/2*0.6, 0), xytext=(C, d2/2*0.6),
                  arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.5", color=TEC_GREEN, lw=2))
    ax_g.text(C + d2/2*0.6, d2/2*0.6, f"$\omega_2$\n{omega2:.1f} RPM", color=TEC_GREEN, ha='left', fontweight='bold')

    ax_g.set_aspect('equal')
    ax_g.axis('off')
    st.pyplot(fig_gear)

with col_calc:
    st.markdown('<p class="section-header">Análisis Cinemático</p>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="alert-box">
        <h4 style='margin-top:0;'>Tipo de Sistema</h4>
        El arreglo opera como un <span style='color:{color_tren};'>{tipo_tren}</span>.<br><br>
        Relación de Transmisión ($m_G$): <b>{relacion_mG:.2f}</b><br>
        Velocidad de Salida ($\\omega_2$): <span style='color:{color_tren}; font-size:1.3em;'>{omega2:.1f} RPM</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">Memoria de Cálculo Analítico</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="step-box">
        <b>Paso 1: Diámetros de Paso ($d$)</b><br>
        El diámetro de paso es el círculo imaginario donde ocurre el rodamiento puro.<br>
        Piñón: $d_1 = m \\cdot N_1 = ({modulo})({N1}) =$ <b>{d1:.1f} mm</b><br>
        Rueda: $d_2 = m \\cdot N_2 = ({modulo})({N2}) =$ <b>{d2:.1f} mm</b>
    </div>
    <div class="step-box">
        <b>Paso 2: Distancia de Centro a Centro ($C$)</b><br>
        $C = \\frac{{d_1 + d_2}}{{2}} = \\frac{{{d1:.1f} + {d2:.1f}}}{{2}} =$ <b>{C:.1f} mm</b>
    </div>
    <div class="step-box">
        <b>Paso 3: Geometría del Diente (Nomenclatura)</b><br>
        Paso Circular: $p = \\pi \\cdot m = \\pi ({modulo}) =$ <b>{paso_circular:.2f} mm</b><br>
        Cabeza (Addendum): $a = m =$ <b>{a:.2f} mm</b><br>
        Raíz (Dedendum): $b = 1.25m =$ <b>{b:.2f} mm</b><br>
        Diámetro Exterior (Piñón): $D_{{o1}} = d_1 + 2a =$ <b>{do1:.1f} mm</b>
    </div>
    <div class="step-box">
        <b>Paso 4: Velocidad Angular de Salida ($\\omega_2$)</b><br>
        $\\omega_2 = \\omega_1 \\left( \\frac{{N_1}}{{N_2}} \\right) = {omega1} \\left( \\frac{{{N1}}}{{{N2}}} \\right) =$ <b>{omega2:.1f} RPM</b>
    </div>
    """, unsafe_allow_html=True)
