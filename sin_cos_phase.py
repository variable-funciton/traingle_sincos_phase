import streamlit as st
import numpy as np
import sympy as sym
import matplotlib.pyplot as plt
# 日本語フォントの設定（Windows / Mac / Linux 対応のフォールバック付き）
plt.rcParams["font.sans-serif"] = ["Meiryo", "Yu Gothic", "MS Gothic", "Hiragino Sans", "IPAexGothic"]
plt.rcParams["axes.unicode_minus"] = False  # マイナス記号の文字化け防止

# --- ページ設定 ---
st.set_page_config(page_title="sinとcosの位相と周期性", layout="wide")
st.title(r"$\sin$ と $\cos$ の位相差（$\frac{\pi}{2}$）と周期性の可視化")

# --- サイドバー：設定とスライダー ---
st.sidebar.header("パラメータ設定")

# 1. 単位の切り替え（ラジアン / 60分法）
unit = st.sidebar.radio("角度 $t$ の単位", ("ラジアン (rad)", "60分法 (度)"))

# 周期性を意識させるため、範囲を -2π 〜 2π (-360° 〜 360°) に設定
# 有名角（30°, 45°, 60°, 90°など）をすべて踏めるよう、15° (π/12) 刻みに設定
if unit == "60分法 (度)":
    t_deg = st.sidebar.slider("平行移動量 t (度)", min_value=-360, max_value=360, value=0, step=15)
    t_rad = np.deg2rad(t_deg)
    t_label = f"{t_deg}^\\circ"
else:
    # π/12 刻みの選択肢を生成 (-24π/12 〜 +24π/12)
    k_values = list(range(-24, 25))
    
    def format_rad(k):
        if k == 0:
            return "0"
        expr = sym.Rational(k, 12) * sym.pi
        return f"{sym.latex(expr)}".replace("\\frac", "").replace("{", "").replace("}", "/") if False else str(expr).replace("pi", "π")

    k_selected = st.sidebar.select_slider(
        "平行移動量 t (ラジアン)",
        options=k_values,
        value=0,
        format_func=lambda k: "0" if k == 0 else str(sym.Rational(k, 12) * sym.pi).replace("pi", "π")
    )
    t_deg = k_selected * 15
    t_rad = np.deg2rad(t_deg)
    t_sym = sym.Rational(k_selected, 12) * sym.pi
    t_label = sym.latex(t_sym)

# 2. 有名角の表示設定
st.sidebar.subheader("有名角の可視化オプション")
show_famous = st.sidebar.checkbox("有名角に対応する点を表示", value=True)
show_shift_arrow = st.sidebar.checkbox("基準点の平行移動（矢印）を表示", value=True)

famous_type = st.sidebar.selectbox(
    "強調する有名角のグループ",
    ("すべて (30°, 45°, 60°, 90°系)", "90° (π/2) 刻みのみ", "30°・60° (π/6, π/3) 系", "45° (π/4) 系")
)

# --- 現在の t の状態と一致判定の表示 ---
col_info1, col_info2 = st.columns(2)
with col_info1:
    st.markdown(f"現在の移動量: $t = {t_label}$")
with col_info2:
    # 位相が一致するタイミングのハイライト（周期 360° を考慮）
    if (t_deg - 90) % 360 == 0:
        st.success(r"完全一致．$\cos(x - t) = \sin(x)$（位相差 $\frac{\pi}{2} + 2n\pi$）")
    elif (t_deg + 90) % 360 == 0:
        st.success(r"完全一致．$\sin(x - t) = \cos(x)$（位相差 $-\frac{\pi}{2} + 2n\pi$）")
    elif t_deg % 360 == 0 and t_deg != 0:
        st.info(r"1周期（$2\pi$ / $360^\circ$）分シフト！元の $\sin(x), \cos(x)$ と同じ波形に戻っています。")

# --- 有名角データの作成 (0 〜 2π の1周期分を代表点としてプロット) ---
if famous_type == "90° (π/2) 刻みのみ":
    base_degs = [0, 90, 180, 270, 360]
elif famous_type == "30°・60° (π/6, π/3) 系":
    base_degs = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360]
elif famous_type == "45° (π/4) 系":
    base_degs = [0, 45, 90, 135, 180, 225, 270, 315, 360]
else:
    base_degs = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]

famous_x = np.deg2rad(base_degs)
famous_x_shifted = famous_x + t_rad  # x - t = x_0 となる点 x = x_0 + t

# --- 描画範囲と軸目盛りの設定 ---
x_min, x_max = -2 * np.pi, 3 * np.pi
x = np.linspace(x_min, x_max, 1000)

# x軸の目盛り（π/2 = 90° 刻み）
tick_degs = list(range(-360, 541, 90))
tick_rads = np.deg2rad(tick_degs)
if unit == "60分法 (度)":
    tick_labels = [f"${d}^\\circ$" for d in tick_degs]
else:
    tick_labels = [f"${sym.latex(sym.Rational(d, 180) * sym.pi)}$" if d != 0 else "$0$" for d in tick_degs]

# --- グラフ描画関数 ---
def plot_wave_comparison(ax, y_fixed, y_shifted, fixed_famous_y, label_fixed, label_shifted, title_str):
    # 固定グラフ（比較対象）
    ax.plot(x, y_fixed, "--", color="gray", lw=2, alpha=0.8, label=label_fixed)
    # 動くグラフ（x方向に t だけ平行移動）
    ax.plot(x, y_shifted, "-", color="#1f77b4", lw=2.5, label=label_shifted)

    # 1周期 (0 <= x <= 2π) の背景ハイライト（平行移動に追従）
    ax.axvspan(0 + t_rad, 2 * np.pi + t_rad, color="#1f77b4", alpha=0.07, label="基本周期区間 $[t, t+2\\pi]$")

    # 有名角の点のプロット
    if show_famous:
        # 元の有名角の位置 (0 〜 2π)
        ax.scatter(famous_x, fixed_famous_y, color="gray", s=40, zorder=4, alpha=0.6)
        # 平行移動後の有名角の位置 (t 〜 t + 2π)
        ax.scatter(famous_x_shifted, fixed_famous_y, color="#d62728", s=55, zorder=5, label="移動後の有名角の点")

        # 平行移動の矢印（代表点: x=0, π/2, π, 3π/2, 2π）
        if show_shift_arrow and t_deg != 0:
            for deg_0 in [0, 90, 180, 270, 360]:
                if deg_0 in base_degs:
                    idx = base_degs.index(deg_0)
                    x0 = famous_x[idx]
                    y0 = fixed_famous_y[idx]
                    ax.annotate(
                        "", xy=(x0 + t_rad, y0), xytext=(x0, y0),
                        arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5, ls="-"),
                        zorder=6
                    )

    # 補助線（y = ±1/2, ±1/√2, ±√3/2）
    for val in [-np.sqrt(3)/2, -1/np.sqrt(2), -0.5, 0.5, 1/np.sqrt(2), np.sqrt(3)/2]:
        ax.axhline(val, color="green", linestyle=":", linewidth=0.8, alpha=0.4)

    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-1.4, 1.4)
    ax.set_xticks(tick_rads)
    ax.set_xticklabels(tick_labels, fontsize=12)
    ax.set_yticks([-1, -np.sqrt(3)/2, -1/np.sqrt(2), -0.5, 0, 0.5, 1/np.sqrt(2), np.sqrt(3)/2, 1])
    ax.set_yticklabels([
        "$-1$", "$-\\frac{\\sqrt{3}}{2}$", "$-\\frac{1}{\\sqrt{2}}$", "$-\\frac{1}{2}$",
        "$0$",
        "$\\frac{1}{2}$", "$\\frac{1}{\\sqrt{2}}$", "$\\frac{\\sqrt{3}}{2}$", "$1$"
    ], fontsize=11)
    ax.set_title(title_str, fontsize=15)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", fontsize=11)

# --- 2段グラフの作成 ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8.5), dpi=100)
plt.subplots_adjust(hspace=0.35)

# グラフ1: y = sin(x - t) と y = cos(x)
plot_wave_comparison(
    ax=ax1,
    y_fixed=np.cos(x),
    y_shifted=np.sin(x - t_rad),
    fixed_famous_y=np.sin(famous_x),
    label_fixed=r"$y = \cos(x)$ （固定）",
    label_shifted=rf"$y = \sin(x - t)$  ($t = {t_label}$)",
    title_str=r"① $y = \sin(x - t)$ と $y = \cos(x)$ の比較"
)

# グラフ2: y = cos(x - t) と y = sin(x)
plot_wave_comparison(
    ax=ax2,
    y_fixed=np.sin(x),
    y_shifted=np.cos(x - t_rad),
    fixed_famous_y=np.cos(famous_x),
    label_fixed=r"$y = \sin(x)$ （固定）",
    label_shifted=rf"$y = \cos(x - t)$  ($t = {t_label}$)",
    title_str=r"② $y = \cos(x - t)$ と $y = \sin(x)$ の比較"
)

st.pyplot(fig)

# --- 有名角の対応値テーブル（オプション表示） ---
with st.expander("基本周期内の有名角と関数値の対応表を確認する"):
    st.markdown(r"元の角度 $x_0$ における値が、平行移動によって **$x = x_0 + t$** の位置に現れます。")
    table_cols = st.columns(len(base_degs))
    for i, deg_0 in enumerate(base_degs):
        rad_0_sym = sym.Rational(deg_0, 180) * sym.pi
        shifted_deg = deg_0 + t_deg
        shifted_rad_sym = sym.Rational(shifted_deg, 180) * sym.pi
        with table_cols[i]:
            if unit == "60分法 (度)":
                st.markdown(f"元:** ${deg_0}^\\circ$")
                st.markdown(f"移動後: ${shifted_deg}^\\circ$")
            else:
                st.markdown(f"元: ${sym.latex(rad_0_sym)}$")
                st.markdown(f"移動後: ${sym.latex(shifted_rad_sym)}$")
