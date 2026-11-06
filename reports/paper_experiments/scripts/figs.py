"""Figures for the paper, from the measured stratified results."""
import json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
S = Path(sys.argv[1]); r = json.load(open(S/"out/e03.json"))
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 9})
INK, MUTE, BLUE, ORANGE = "#222222", "#666666", "#2563a8", "#d9822b"

# Fig. 1: the cascade
fig, ax = plt.subplots(figsize=(4.8, 1.75)); ax.set_xlim(0, 100); ax.set_ylim(0, 36); ax.axis("off")
boxes = [(1, "URL", ""), (19, "A\nBlocklists", "0.13 ms"), (40, "B\nTypo-\nsquatting", "0.52 ms"),
         (61, "C\nBiLSTM +\nXGBoost", "32.7 ms"), (82, "D\nLLM page\nreader", "about 2 s")]
w = {0: 12}
for i, (x, t, lat) in enumerate(boxes):
    bw = 12 if i == 0 else 17
    ax.add_patch(FancyBboxPatch((x, 17), bw, 14, boxstyle="round,pad=0.2,rounding_size=1", fc="#eef3f9" if i else "white", ec=BLUE if i else MUTE, lw=.9))
    ax.text(x + bw/2, 24, t, ha="center", va="center", fontsize=7.5, color=INK)
    if lat: ax.text(x + bw/2, 33.2, lat, ha="center", fontsize=6.5, color=MUTE)
    if i < 4:
        nx = boxes[i+1][0]
        ax.annotate("", xy=(nx-.4, 24), xytext=(x+bw+.4, 24), arrowprops=dict(arrowstyle="->", color=INK, lw=.8))
for x, t in ((27.5, "listed:\nphishing"), (69.5, "low score, no\nB flag: clean"), (90.5, "verdict, or\nfallback warning")):
    ax.annotate("", xy=(x, 10.5), xytext=(x, 16.6), arrowprops=dict(arrowstyle="->", color=MUTE, lw=.7))
    ax.text(x, 9.5, t, ha="center", va="top", fontsize=6.5, color=INK)
fig.savefig(S/"fig/fig1.png", dpi=300, bbox_inches="tight"); plt.close(fig)

# Fig. 2: two panels, one measure each
names = [("test", "Test"), ("phreshphish", "PhreshPhish"), ("vn", "Vietnamese")]
fig, axs = plt.subplots(1, 2, figsize=(4.8, 2.05))
for ax, title, f in ((axs[0], "Clean URLs cleared (%)", lambda x: 100*x["cleared_BC"]/max(x["n_cl"], 1)),
                     (axs[1], "Phishing URLs missed (%)", lambda x: 100*x["miss_BC"]/max(x["n_ph"], 1))):
    for j, (key, col, lab) in enumerate((("ranked", BLUE, "Domain in Tranco"), ("unranked", ORANGE, "Domain not in Tranco"))):
        for i, (s, _) in enumerate(names):
            v = f(r[s][key]); b = ax.bar(i + (j-.5)*.38, v, .35, color=col, label=lab if i == 0 else None)
            ax.text(i + (j-.5)*.38, v + 1.2 * (ax is axs[0]) * 1.5 + .5 * (ax is axs[1]), f"{v:.1f}" if ax is axs[0] else f"{v:.2f}", ha="center", fontsize=6.5, color=INK)
    ax.set_xticks(range(3)); ax.set_xticklabels([n for _, n in names], fontsize=7.5)
    ax.set_title(title, fontsize=8.5, loc="left", color=INK)
    for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
    ax.tick_params(left=False, labelleft=False, length=0); ax.spines["bottom"].set_color(MUTE)
axs[0].set_ylim(0, 92); axs[1].set_ylim(0, 26)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=2, frameon=False, fontsize=7.5, bbox_to_anchor=(.5, -.06))
fig.tight_layout(rect=(0, .05, 1, 1)); fig.savefig(S/"fig/fig2.png", dpi=300, bbox_inches="tight")
