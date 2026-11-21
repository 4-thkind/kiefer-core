"""
Script to generate high-resolution figures and a publication-quality 3-page PDF report.
"""

import os
import math
import matplotlib.pyplot as plt
import numpy as np

import fibonacci_search as fib

# 1. Generate Figures
os.makedirs("report_assets", exist_ok=True)
fig_path = os.path.join("report_assets", "figure_plots.png")

# Compute fit and SSE curve
opt_res = fib.fibonacci_search(fib.sse_of_rate, 0.005, 0.10, 1e-8)
best = fib.fit_for_rate(opt_res.x)

# Create 2-panel figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 3.6), dpi=300)

# Panel 1: Observed vs Fit + Extrapolation
years_obs = np.array(fib.YEARS)
co2_obs = np.array(fib.CO2)

years_curve = np.linspace(1959, 2050, 200)
co2_curve = best.c0 + best.amp * np.exp(opt_res.x * (years_curve - 1959))

ax1.scatter(years_obs, co2_obs, color="#1e293b", s=14, label="NOAA Observed (1959–2023)", zorder=3)
ax1.plot(years_curve[:140], co2_curve[:140], color="#fa520f", linewidth=2.0, label=f"Fitted Model (r*={opt_res.x:.6f})")
ax1.plot(years_curve[139:], co2_curve[139:], color="#fa520f", linestyle="--", linewidth=1.8, label="Extrapolation (2024–2050)")
ax1.scatter([2030, 2050], [best.c0 + best.amp * math.exp(opt_res.x * (2030 - 1959)),
                           best.c0 + best.amp * math.exp(opt_res.x * (2050 - 1959))],
            color="#ef4444", s=35, zorder=4)
ax1.annotate("2030: 441.3 ppm", (2030, 441.3), textcoords="offset points", xytext=(-25, 10), fontsize=7.5, fontweight="bold")
ax1.annotate("2050: 511.8 ppm", (2050, 511.8), textcoords="offset points", xytext=(-35, 10), fontsize=7.5, fontweight="bold")

ax1.set_title("(a) Atmospheric CO2: Observations & Fitted Trajectory", fontsize=9.5, fontweight="bold", pad=8)
ax1.set_xlabel("Year", fontsize=8.5)
ax1.set_ylabel("CO2 Mole Fraction (ppm)", fontsize=8.5)
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.legend(fontsize=7.5, loc="upper left")

# Panel 2: Unimodal SSE(r) Loss Curve
r_vals = np.linspace(0.005, 0.08, 200)
sse_vals = [fib.sse_of_rate(r) for r in r_vals]

ax2.plot(r_vals, sse_vals, color="#0284c7", linewidth=2.0, label="Objective SSE(r)")
ax2.axvline(opt_res.x, color="#fa520f", linestyle="--", linewidth=1.5, label=f"Minimizer r* = {opt_res.x:.6f}")
ax2.scatter([opt_res.x], [best.sse], color="#fa520f", s=40, zorder=4)
ax2.annotate(f"Min SSE = {best.sse:.2f}", (opt_res.x, best.sse), textcoords="offset points", xytext=(12, 10),
             fontsize=7.5, fontweight="bold", color="#fa520f")

ax2.set_title("(b) Strictly Unimodal Loss Objective SSE(r)", fontsize=9.5, fontweight="bold", pad=8)
ax2.set_xlabel("Growth Rate r (per year)", fontsize=8.5)
ax2.set_ylabel("Sum of Squared Errors (ppm²)", fontsize=8.5)
ax2.grid(True, linestyle=":", alpha=0.6)
ax2.legend(fontsize=7.5, loc="upper right")

plt.tight_layout()
plt.savefig(fig_path, bbox_inches="tight")
plt.close()
print("Figure generated successfully at:", fig_path)
