import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 11

t = np.linspace(0, 10, 200)
saine = 1.0 + 0.06 * t          # structure saine : cout quasi constant
dette = 1.0 + 0.035 * np.exp(0.52 * t)   # dette : cout qui explose

fig, ax = plt.subplots(figsize=(7.2, 3.6))
ax.plot(t, saine, color="#2E8B57", lw=2.6, label="Structure saine")
ax.plot(t, dette, color="#D9822B", lw=2.6, label="Dette architecturale")
ax.fill_between(t, saine, dette, where=dette > saine, color="#D9822B", alpha=0.08)
ax.annotate("le prix de la dette", xy=(8.4, 4.6), fontsize=10, color="#D9822B")
ax.set_xlabel("Temps de vie du projet")
ax.set_ylabel("Coût d'ajout d'une fonctionnalité")
ax.set_xticks([]); ax.set_yticks([])
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig("figA_cout_changement.pdf")
fig.savefig("figA_cout_changement.png", dpi=110)
print("figA OK")
