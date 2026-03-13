# pip install streamlit matplotlib numpy
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.set_page_config(page_title="Asse Cardiaco ECG", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .result-box {
        border-radius: 12px;
        padding: 14px 18px;
        text-align: left;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# Calcolatore dell'Asse Cardiaco ECG")
st.markdown("---")

LEADS = {
    "D1":  {"angle": 0,    "color": "#e74c3c"},
    "D2":  {"angle": 60,   "color": "#e67e22"},
    "D3":  {"angle": 120,  "color": "#f39c12"},
    "aVR": {"angle": -150, "color": "#9b59b6"},
    "aVL": {"angle": -30,  "color": "#3498db"},
    "aVF": {"angle": 90,   "color": "#16a085"},
}

col_chart, col_params = st.columns([1.6, 1], gap="large") # colonna sx per il grafico più ampia (1.6), colonna per i paramestri a 1

# Paramestri: colonna a destra, opzione per metterli in alto o a sinistra
lead_values: dict[str, float] = {}

with col_params:
    st.subheader("Parametri")

    for lead, info in LEADS.items():
        sign = st.radio(
            f"**{lead}** ({info['angle']}°)",
            options=["Positivo", "Negativo"],
            key=f"sign_{lead}",
            horizontal=True,
        )
        lead_values[lead] = 5.0 if sign == "Positivo" else -5.0 

    # Calcolo, formula corretta?
    d1_val  = lead_values["D1"]
    avf_val = lead_values["aVF"]

    axis_angle = np.degrees(np.arctan2(avf_val, d1_val)) if not (d1_val == 0 and avf_val == 0) else 0.0
    axis_angle = ((axis_angle + 180.0) % 360.0) - 180.0

    def classify(angle):
        if -30 <= angle <= 90:
            return "Asse Normale", "#27ae60", "Normale"
        elif -90 <= angle < -30:
            return "Deviazione Assiale Sinistra (LAD)", "#2980b9", "LAD"
        elif 90 < angle <= 180:
            return "Deviazione Assiale Destra (RAD)", "#c0392b", "RAD"
        else:
            return "Asse Estremo / Indeterminato", "#8e44ad", "Estremo"

    axis_label, axis_hex, axis_type = classify(axis_angle)

    st.markdown("---")
    st.metric("Asse Calcolato", f"{axis_angle:.1f}°")
    st.markdown(
        f"<div class='result-box' style='background:{axis_hex}22;"
        f"border-left:5px solid {axis_hex}'>"
        f"<b>{axis_label}</b></div>",
        unsafe_allow_html=True,
    )

# Grafico
with col_chart:
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#f8f9fa")
    ax.set_xlim(-1.7, 1.7)
    ax.set_ylim(-1.7, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")

    def ecg_xy(deg, r=1.0):
        rad = np.radians(deg)
        return r * np.cos(rad), -r * np.sin(rad)

    def draw_sector(a_start, a_end, color, alpha=0.18):
        thetas = np.linspace(np.radians(a_start), np.radians(a_end), 300)
        xs = [0] + [np.cos(t) for t in thetas] + [0]
        ys = [0] + [-np.sin(t) for t in thetas] + [0]
        ax.fill(xs, ys, color=color, alpha=alpha, zorder=1)

    draw_sector(-30,  90,  "#27ae60")
    draw_sector(-90, -30,  "#2980b9")
    draw_sector( 90,  180, "#c0392b")
    draw_sector( 180,  270, "#8e44ad")

    theta_c = np.linspace(0, 2 * np.pi, 360)
    ax.plot(np.cos(theta_c), np.sin(theta_c), color="gray", linewidth=1.5, alpha=0.4, zorder=2)

    for deg in range(-180, 181, 30):
        xlab, ylab = ecg_xy(deg, 1.22)
        ax.text(xlab, ylab, f"{deg}°", ha="center", va="center", fontsize=7, color="#7f8c8d", zorder=3)

    for lead, info in LEADS.items():
        ang = info["angle"]
        xp, yp = ecg_xy(ang)
        xn, yn = -xp, -yp

        ax.plot([xn, xp], [yn, yp], color="#bdc3c7", linewidth=1.0, linestyle="--", zorder=2)
        ax.plot([0, xp], [0, yp], color=info["color"], linewidth=2.0, zorder=3)

        val = lead_values[lead]
        dot_c = "#27ae60" if val > 0 else "#e74c3c"
        ax.plot(xp, yp, "o", color=dot_c, markersize=9, markeredgecolor="white", markeredgewidth=1, zorder=5)

        xl, yl = ecg_xy(ang, 1.45)
        ax.text(xl, yl, lead, ha="center", va="center", fontsize=10, fontweight="bold", color=info["color"], zorder=6)

    xa, ya = ecg_xy(axis_angle, 0.88)
    ax.annotate("", xy=(xa, ya), xytext=(-0.08 * xa, -0.08 * ya),
                arrowprops=dict(arrowstyle="->", color=axis_hex, lw=3.0, mutation_scale=22), zorder=8)
    ax.plot(0, 0, "o", color=axis_hex, markersize=6, zorder=9)

    # ax.set_title(f"Asse Cardiaco: {axis_angle:.1f}°  —  {axis_type}",
    #              fontsize=12, fontweight="bold", color="#2c3e50", pad=14)

    # legend_handles = [
    #     mpatches.Patch(color="#27ae60", alpha=0.7, label="Normale  (−30° a +90°)"),
    #     mpatches.Patch(color="#2980b9", alpha=0.7, label="LAD      (−90° a −30°)"),
    #     mpatches.Patch(color="#c0392b", alpha=0.7, label="RAD      (+90° a +180°)"),
    #     mpatches.Patch(color="#8e44ad", alpha=0.7, label="Estremo  (±180° ÷ −90°)"),
    # ]
    # ax.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, -0.06),
    #           ncol=2, fontsize=8.5, framealpha=0.85, edgecolor="#cccccc")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
