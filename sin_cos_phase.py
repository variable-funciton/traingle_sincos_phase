%%writefile sin_cos_phase.py
import streamlit as st
import numpy as np
import sympy as sym
import matplotlib.pyplot as plt

# --- Matplotlib の日本語文字化け対策 ---
plt.rcParams["font.sans-serif"] = ["Meiryo", "Yu Gothic", "MS Gothic", "Hiragino Sans", "IPAexGothic"]
plt.rcParams["axes.unicode_minus"] = False

# --- ページ設定 ---
st.set_page_config(page_title="sinとcosの位相と周期性", layout="wide")
st.title(r"$\sin$ と $\cos$ の位相差（$\frac{\pi}{2}$）と周期性の可視化")

# --- 事前計算のキャッシュ（スライダー操作時の負荷を劇的に削減） ---
@st.cache_data
def get_precomputed_data():
    # k = -24 〜 24 (-2π 〜 2π) の表示文字列とLaTeX表記を事前生成
    slider_str = {}
    latex_deg = {}
    for deg in range(-360, 721, 15):
        if deg == 0:
             latex_deg[deg] = "0"
        else:
            latex_deg[deg] = sym.latex(sym.Rational(deg, 180) * sym.pi)
            
    for k in range(-24, 25):
        deg = k * 15
        if k == 0:
            slider_str[k] = "0"
        else:
            slider_str[k] = str(sym.Rational(k, 12) * sym.pi).replace("pi", "π")

    # x軸の描画データ（400点で十分滑らか＆高速）
    x_min, x_max = -2 * np.pi, 3 * np.pi
    x = np.linspace(x_min, x_max, 400)
    sin_x = np.sin(x)
    cos_x = np.cos(x)

    # x軸の目盛り
    tick_degs = list(range(-360, 541, 90))
    tick_rads = np.deg2rad(tick_degs)
    tick_labels_deg = [f"${d}^\\circ$" for d in tick_degs]
    tick_labels_rad = [f"${latex_deg[d]}$" for d in tick_degs]

    return slider_str, latex_deg, x, sin_x, cos_x, tick_rads, tick_labels_deg, tick_labels_rad

slider_str, latex_deg, x, sin_x, cos_x, tick_rads, tick_labels_deg, tick_labels_rad = get_precomputed_data()

# --- サイドバー：設定とスライダー ---
st.sidebar.header("パラメータ設定")

unit = st.sidebar.radio("角度 $t$ の単位", ("ラジアン (rad)", "60分法 (度)"))

if unit == "60分法 (度)":
    t_deg = st.sidebar.slider("平行移動量 t (度)", min_value=-360, max_value=360, value=0, step=15)
    t_label = f"{t_deg}^\\circ"
    tick_labels = tick_labels_deg
else:
    k_selected = st.sidebar.select_slider(
        "平行移動量 t (ラジアン)",
        options=list(range(-24, 25)),
        value=0,
        format_func=lambda k: slider_str[k]
    )
    t_deg = k_selected * 15
    t_label = latex_deg[t_deg]
    tick_labels = tick_labels_rad

t_rad = np.deg2rad(t_deg)

st.sidebar.subheader("有名角の可視化オプション")
show_famous = st.sidebar.checkbox("有名角に対応する点を表示", value=True)
show_shift_arrow = st.sidebar.checkbox("基準点の平行移動（矢印）を表示", value=True)

famous_type = st.sidebar.selectbox(
    "強調する有名角のグループ",
    ("すべて (30°, 45°, 60°, 90°系)", "90° (π/2) 刻みのみ", "30°・60° (π/6, π/3) 系", "45° (π/4) 系")
)

# --- 現在の t の状態と一致判定の表示 ---
col_info1, col_info2 = st.columns([1, 2])
with col_info1:
    st.markdown(f"#### 現在の移動量: $t = {t_label}$")
with col_info2:
    if (t_deg - 90) % 360 == 0:
        st.success(r"完全一致： $\cos(x - t) = \sin(x)$ （位相差 $\frac{\pi}{2} + 2n\pi$）")
    elif (t_deg + 90) % 360 == 0:
        st.success(r"完全一致： $\sin(x - t) = \cos(x)$ （位相差 $-\frac{\pi}{2} + 2n\pi$）")
    elif t_deg % 360 == 0 and t_deg != 0:
        st.info(r"1周期（$2\pi$ / $360^\circ$）分シフト： 元の $\sin(x), \cos(x)$ と同じ波形に戻っています。")

# --- 有名角データの作成 ---
if famous_type == "90° (π/2) 刻みのみ":
    base_degs = [0, 90, 180, 270, 360]
elif famous_type == "30°・60° (π/6, π/3) 系":
    base_degs = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360]
elif famous_type == "45° (π/4) 系":
    base_degs = [0, 45, 90, 135, 180, 225, 270, 315, 360]
else:
    base_degs = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]

famous_x = np.deg2rad(base_degs)
famous_x_shifted = famous_x + t_rad

# --- グラフ描画関数 ---
y_ticks = [-1, -np.sqrt(3)/2, -1/np.sqrt(2), -0.5, 0, 0.5, 1/np.sqrt(2), np.sqrt(3)/2, 1]
y_tick_labels = [
    "$-1$", "$-\\frac{\\sqrt{3}}{2}$", "$-\\frac{1}{\\sqrt{2}}$", "$-\\frac{1}{2}$",
    "$0$",
    "$\\frac{1}{2}$", "$\\frac{1}{\\sqrt{2}}$", "$\\frac{\\sqrt{3}}{2}$", "$1$"
]

def plot_wave_comparison(ax, y_fixed, y_shifted, fixed_famous_y, label_fixed, label_shifted, title_str):
    ax.plot(x, y_fixed, "--", color="gray", lw=2, alpha=0.8, label=label_fixed)
    ax.plot(x, y_shifted, "-", color="#1f77b4", lw=2.5, label=label_shifted)
    ax.axvspan(t_rad, 2 * np.pi + t_rad, color="#1f77b4", alpha=0.07, label="基本周期区間 $[t, t+2\\pi]$")

    if show_famous:
        ax.scatter(famous_x, fixed_famous_y, color="gray", s=35, zorder=4, alpha=0.6)
        ax.scatter(famous_x_shifted, fixed_famous_y, color="#d62728", s=50, zorder=5, label="移動後の有名角の点")

        if show_shift_arrow and t_deg != 0:
            for deg_0 in [0, 90, 180, 270, 360]:
                if deg_0 in base_degs:
                    idx = base_degs.index(deg_0)
                    x0 = famous_x[idx]
                    y0 = fixed_famous_y[idx]
                    ax.annotate(
                        "", xy=(x0 + t_rad, y0), xytext=(x0, y0),
                        arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5),
                        zorder=6
                    )

    for val in y_ticks[1:-1]:
        if val != 0:
            ax.axhline(val, color="green", linestyle=":", linewidth=0.7, alpha=0.35)

    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlim(-2 * np.pi, 3 * np.pi)
    ax.set_ylim(-1.35, 1.35)
    ax.set_xticks(tick_rads)
    ax.set_xticklabels(tick_labels, fontsize=11)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_tick_labels, fontsize=8.5)
    ax.set_title(title_str, fontsize=13, pad=10)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", fontsize=9.5, framealpha=0.9)

# --- 2段グラフの作成（余白と解像度を最適化） ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.5), dpi=85)
plt.subplots_adjust(hspace=0.52)

plot_wave_comparison(
    ax=ax1,
    y_fixed=cos_x,
    y_shifted=np.sin(x - t_rad),
    fixed_famous_y=np.sin(famous_x),
    label_fixed=r"$y = \cos(x)$ (固定)",
    label_shifted=rf"$y = \sin(x - t)$  ($t = {t_label}$)",
    title_str=r"① $y = \sin(x - t)$ と $y = \cos(x)$ の比較"
)

plot_wave_comparison(
    ax=ax2,
    y_fixed=sin_x,
    y_shifted=np.cos(x - t_rad),
    fixed_famous_y=np.cos(famous_x),
    label_fixed=r"$y = \sin(x)$ (固定)",
    label_shifted=rf"$y = \cos(x - t)$  ($t = {t_label}$)",
    title_str=r"② $y = \cos(x - t)$ と $y = \sin(x)$ の比較"
)

st.pyplot(fig)
plt.close(fig)  # メモリ解放（連続操作時の速度低下を防止）

# --- 有名角の対応値テーブル（1つのMarkdown表にまとめて高速化） ---
with st.expander("基本周期内の有名角と関数値の対応表を確認する"):
    st.markdown(r"元の角度 $x_0$ における値が、平行移動によって **$x = x_0 + t$** の位置に現れます。")
    if unit == "60分法 (度)":
        headers = [f"${d}^\\circ$" for d in base_degs]
        shifted = [f"${d + t_deg}^\\circ$" for d in base_degs]
    else:
        headers = [f"${latex_deg[d]}$" for d in base_degs]
        shifted = [f"${latex_deg[d + t_deg]}$" for d in base_degs]

    md_table = "| 元の角度 $x_0$ | " + " | ".join(headers) + " |\n"
    md_table += "| :--- | " + " | ".join([":---:" for _ in base_degs]) + " |\n"
    md_table += "| **移動後 $x_0 + t$** | " + " | ".join(shifted) + " |"
    st.markdown(md_table)
