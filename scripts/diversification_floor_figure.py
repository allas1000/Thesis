"""Draw the diversification figure for Section 5 of the thesis.

The relative volatility of the average insured loss across n equicorrelated
firms is

    sd(mean of n) / sd(single) = sqrt(1/n + (1 - 1/n) * rho_L),

where rho_L is a common Pearson correlation of insured losses. As n grows the
expression tends to sqrt(rho_L) rather than to zero, so dependence imposes a
floor that no amount of pooling removes.

rho_L is a scenario parameter and the model audit does not estimate it. The
curves are drawn at the round hypothetical values 0, 0.05, 0.20, and 0.70.

Writes figures/h3_diversification_floor.png. The figure carries no title, since
the LaTeX caption supplies it.

Run from anywhere:

    python scripts/diversification_floor_figure.py
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter

C_STRONG = "#2e5b88"
C_MID = "#7ba7cc"
C_WEAK = "#a9c4dd"
C_IND = "#808080"
C_GRID = "#e6e6e6"

n = np.logspace(0, np.log10(200), 600)


def rel_sd(n, rho):
    return np.sqrt(1.0 / n + (1.0 - 1.0 / n) * rho)


fig, ax = plt.subplots(figsize=(10.8, 6.0), dpi=225)

ax.plot(n, rel_sd(n, 0.0), color=C_IND, lw=2.4, ls=(0, (6, 3)),
        label=r"Independent losses ($\rho_L = 0$)")
ax.plot(n, rel_sd(n, 0.05), color=C_WEAK, lw=2.8,
        label=r"Weak dependence ($\rho_L = 0.05$)")
ax.plot(n, rel_sd(n, 0.20), color=C_MID, lw=2.8,
        label=r"Moderate dependence ($\rho_L = 0.20$)")
ax.plot(n, rel_sd(n, 0.70), color=C_STRONG, lw=2.8,
        label=r"Strong dependence ($\rho_L = 0.70$)")

# Floors at sqrt(rho). The x positions and vertical offsets keep each label
# clear of every curve, so they are tuned by eye rather than derived.
floors = [
    (0.70, C_STRONG, 2.3, -0.042, r"floor $\sqrt{0.70} = 0.84$"),
    (0.20, C_MID, 10.0, -0.025, r"floor $\sqrt{0.20} = 0.45$"),
    (0.05, C_WEAK, 40.0, -0.038, r"floor $\sqrt{0.05} = 0.22$"),
]
for rho, col, xpos, dy, lab in floors:
    f = np.sqrt(rho)
    ax.axhline(f, color=col, lw=1.4, ls=":")
    ax.text(xpos, f + dy, lab, color=col, fontsize=15, ha="left", va="center")

ax.set_xscale("log")
ax.set_xlim(1, 200)
ax.set_ylim(0, 1.0)
ticks = [1, 2, 5, 10, 20, 50, 100, 200]
ax.xaxis.set_major_locator(FixedLocator(ticks))
ax.xaxis.set_major_formatter(FixedFormatter([str(t) for t in ticks]))
ax.xaxis.set_minor_formatter(plt.NullFormatter())
ax.set_yticks(np.arange(0, 1.01, 0.2))

ax.set_xlabel("Number of insured firms in the portfolio (log scale)", fontsize=17)
ax.set_ylabel("Relative standard deviation of average loss", fontsize=16)

ax.grid(True, which="major", color=C_GRID, lw=1.0)
ax.grid(True, which="minor", axis="x", color="#f0f0f0", lw=0.8)
ax.set_axisbelow(True)
for s in ax.spines.values():
    s.set_color("black")
    s.set_linewidth(1.1)
ax.tick_params(labelsize=16)

ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.815), fontsize=14,
          framealpha=1.0, edgecolor="#cccccc", borderpad=0.6, labelspacing=0.5)

fig.tight_layout()
OUT = Path(__file__).resolve().parent.parent / "figures" / "h3_diversification_floor.png"
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=225, facecolor="white")
print("written", OUT)
