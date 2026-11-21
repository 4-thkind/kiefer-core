# Fibonacci Search Method for One-Dimensional Optimization
### Application: Estimating Atmospheric $\text{CO}_2$ Growth Rate from NOAA Mauna Loa Observatory Data

This project implements the **Fibonacci Search Method** for derivative-free one-dimensional line search optimization, applied to fitting an exponential-plus-offset growth model to the 65-year continuous atmospheric carbon dioxide ($\text{CO}_2$) record (1959–2023) from the NOAA Mauna Loa Observatory in Hawaii (the famous Keeling Curve).

---

## 1. Project Overview & Mathematical Formulation

### 1.1 The Fibonacci Search Algorithm (Kiefer, 1953)
Given a unimodal function $f(x)$ over an initial uncertainty bracket $[a_0, b_0]$ and a desired tolerance $\text{tol}$, the Fibonacci search places two interior test points at consecutive Fibonacci ratios:
$$x_1 = a + \frac{F_{k-2}}{F_k}(b - a), \quad x_2 = a + \frac{F_{k-1}}{F_k}(b - a)$$

- **Point Reuse Property**: In each subsequent iteration $k$, one of the previous interior points becomes exactly one of the new interior points, requiring **only one new function evaluation per iteration**.
- **Minimax Optimality**: Kiefer (1953) proved that for a fixed number of function evaluations $N$, no sequential search strategy can guarantee a smaller final bracket of uncertainty:
$$L_{\text{final}} \approx \frac{L_0}{F_{N+1}}$$

### 1.2 Atmospheric $\text{CO}_2$ Exponential Model via Variable Projection
The growth of atmospheric $\text{CO}_2$ is modeled as:
$$\text{CO}_2(t) = C_0 + A \cdot e^{r (t - 1959)}$$

Using **variable projection**, for any candidate growth rate $r$, the linear parameters $C_0$ and $A$ are solved in closed form via linear regression of $\text{CO}_2$ on $e_i = e^{r(t_i - 1959)}$. This reduces the 3D nonlinear least-squares problem into a smooth, 1D strictly unimodal objective:
$$\text{SSE}(r) = \min_{C_0, A} \sum_{i=1}^{65} \left(C_0 + A e^{r(t_i - 1959)} - y_i\right)^2$$
which is solved across the bracket $[0.005, 0.100]$.

---

## 2. Results Summary

| Metric | Fibonacci Search Value | Verification / Baseline |
|---|---|---|
| **Optimal Growth Rate ($r^*$)** | **0.016051** per year | Verified by Golden Section & 100,001 Grid |
| **Final Bracket** | `[0.01605121, 0.01605122]` | Width $< 10^{-8}$ |
| **Function Evaluations** | **37 evaluations** | **2,700× fewer** than Grid Search ($100,001$ evals) |
| **Fitted Model** | $\text{CO}_2(t) = 255.15 + 59.5550 \cdot e^{0.01605(t - 1959)}$ | $R^2 > 0.999$ |
| **Model RMSE / SSE** | $\text{RMSE} = 0.687\text{ ppm}$ | $\text{SSE} = 30.66\text{ ppm}^2$ |
| **Excess $\text{CO}_2$ Doubling Time** | **43.2 years** ($\ln(2)/r^*$) | — |
| **Forecast: 2030** | **441.3 ppm** | — |
| **Forecast: 2050** | **511.8 ppm** | — |

---

## 3. Project Structure

```
Xcm project/
├── DESIGN.md                  # Mistral AI design system tokens and specifications
├── Fibonacci_Search_Project.pdf # Research project paper & mathematical proof
├── fibonacci_search.cpp       # C++17 native implementation (zero external dependencies)
├── fibonacci_search.exe       # Compiled MinGW native binary
├── fibonacci_search.py        # Python 3.12 implementation
├── server.py                  # FastAPI / Uvicorn backend API server
├── index.html                 # Interactive Mistral AI styled web interface
├── run.bat                    # One-click Windows runner batch script
├── fit.csv                    # Generated year, observed, fitted CO2 values
├── history.csv                # Generated iteration-by-iteration bracket history
└── sse_curve.csv              # Generated SSE(r) loss curve points
```

---

## 4. How to Run

### Option A: One-Click Runner (Windows)
Double-click `run.bat` or run:
```bat
.\run.bat
```
This compiles the C++ code, executes the benchmark, and launches the interactive web interface at `http://127.0.0.1:8000`.

### Option B: Running the C++ Binary Directly
```bash
g++ -O2 -std=c++14 -o fibonacci_search.exe fibonacci_search.cpp
.\fibonacci_search.exe
```

### Option C: Running the Python Script Directly
```bash
python fibonacci_search.py
```

### Option D: Running the Web Frontend & API Server
```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your web browser.

> **Offline/Standalone Note**: `index.html` also contains an embedded client-side mathematical engine, allowing you to double-click and open it directly in any browser without needing a server.

---

## 5. Frontend Features & `DESIGN.md` Adherence

The UI strictly adheres to `DESIGN.md` (Mistral AI Design Analysis):
- **Sunset Hero Band**: Atmospheric warm gradient (`#ffa110` → `#ff8a00` → `#fa520f`) with subtle mountain contour and elegant serif typography (**PP Editorial Old** fallback pairing with **Inter** for UI prose and **JetBrains Mono** for code).
- **Sunset Stripe Band**: The signature multi-stop closing gradient band (`#fa520f` → `#ffa110` → `#ffb83e` → `#ffd900` → `#fff8e0`) spanning the page width above the cream footer.
- **Cream Surfaces**: Form panels and feature cards styled in warm cream (`#fff8e0`) with deep beige border (`#e6d5a8`).
- **Button & Card Radii**: Strict 8px (`rounded.md`) for action buttons and 12px (`rounded.lg`) for cards; no pill-shaped buttons.
- **Interactive 1D Coordinate Stepper**: Step-by-step interactive playback visualizer showing interval reduction and point reuse.
- **Dynamic Charts**: Interactive plots of Keeling curve data vs exponential fit, projections to 2060, and unimodal objective curve $\text{SSE}(r)$.
- **Live Terminal**: Integrated console button that invokes the compiled C++ binary and streams stdout to the web screen.
