"""
Fibonacci Search Method for One-Dimensional Optimization
Application: Estimating the Atmospheric CO2 Growth Rate from NOAA Mauna Loa Observatory Data

Based on C++17 implementation by Google DeepMind / Optimization Project.
"""

import math
from typing import Callable, List, Tuple, Dict, Any

# NOAA Mauna Loa Observatory annual mean CO2 (1959-2023)
YEARS: List[float] = [
    1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970,
    1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982,
    1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994,
    1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006,
    2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018,
    2019, 2020, 2021, 2022, 2023
]

CO2: List[float] = [
    315.98, 316.91, 317.64, 318.45, 318.99, 319.62, 320.04, 321.37, 322.18,
    323.05, 324.62, 325.68, 326.32, 327.46, 329.68, 330.19, 331.13, 332.03,
    333.84, 335.41, 336.84, 338.76, 340.12, 341.48, 343.15, 344.87, 346.35,
    347.61, 349.31, 351.69, 353.20, 354.45, 355.70, 356.54, 357.21, 358.96,
    360.97, 362.74, 363.88, 366.84, 368.54, 369.71, 371.32, 373.45, 375.98,
    377.70, 379.98, 382.09, 384.02, 385.83, 387.64, 390.10, 391.85, 394.06,
    396.74, 398.81, 401.01, 404.41, 406.76, 408.72, 411.65, 414.21, 416.41,
    418.53, 421.08
]


class SearchResult:
    def __init__(self, x: float = 0.0, fx: float = 0.0, a: float = 0.0, b: float = 0.0, evals: int = 0):
        self.x = x
        self.fx = fx
        self.a = a
        self.b = b
        self.evals = evals
        self.history: List[Tuple[float, float]] = []
        self.detailed_steps: List[Dict[str, Any]] = []


def fibonacci_numbers(n: int) -> List[int]:
    """Generates Fibonacci numbers F_0, F_1, ..., F_n."""
    F = [0] * (n + 1)
    F[0] = 0
    if n >= 1:
        F[1] = 1
    for i in range(2, n + 1):
        F[i] = F[i - 1] + F[i - 2]
    return F


def fibonacci_search(f: Callable[[float], float], a: float, b: float, tol: float) -> SearchResult:
    """
    Minimizes unimodal function f over [a, b] to within tol using Fibonacci Search.
    Optimal interval reduction strategy (Kiefer, 1953).
    """
    L0 = b - a
    n = 3
    # Step 1: choose smallest n such that F_n >= 2 * (b - a) / tol
    while True:
        F = fibonacci_numbers(n)
        if F[n] >= 2.0 * L0 / tol:
            break
        n += 1

    F = fibonacci_numbers(n)
    res = SearchResult()
    res.history.append((a, b))

    k = n
    x1 = a + (F[k - 2] / F[k]) * (b - a)
    x2 = a + (F[k - 1] / F[k]) * (b - a)
    f1 = f(x1)
    f2 = f(x2)
    res.evals = 2

    res.detailed_steps.append({
        "step": 1,
        "k": k,
        "a": a,
        "b": b,
        "width": b - a,
        "x1": x1,
        "x2": x2,
        "f1": f1,
        "f2": f2,
        "action": "Initial 2 evaluations"
    })

    step_count = 1
    while k > 3:
        step_count += 1
        if f1 < f2:
            # Minimizer lies in [a, x2]
            action = f"f(x1) < f(x2) -> Discard [x2, b], set b = {x2:.8f}"
            b = x2
            x2 = x1
            f2 = f1
            k -= 1
            x1 = a + (F[k - 2] / F[k]) * (b - a)
            f1 = f(x1)
        else:
            # Minimizer lies in [x1, b]
            action = f"f(x1) >= f(x2) -> Discard [a, x1], set a = {x1:.8f}"
            a = x1
            x1 = x2
            f1 = f2
            k -= 1
            x2 = a + (F[k - 1] / F[k]) * (b - a)
            f2 = f(x2)

        res.evals += 1
        res.history.append((a, b))
        res.detailed_steps.append({
            "step": step_count,
            "k": k,
            "a": a,
            "b": b,
            "width": b - a,
            "x1": x1,
            "x2": x2,
            "f1": f1,
            "f2": f2,
            "action": action
        })

    res.x = 0.5 * (a + b)
    res.fx = f(res.x)
    res.evals += 1
    res.a = a
    res.b = b
    return res


def golden_section_search(f: Callable[[float], float], a: float, b: float, tol: float) -> SearchResult:
    """Golden Section Search on [a, b] using ratio (sqrt(5) - 1) / 2."""
    g = (math.sqrt(5.0) - 1.0) / 2.0
    x1 = b - g * (b - a)
    x2 = a + g * (b - a)
    f1 = f(x1)
    f2 = f(x2)

    res = SearchResult()
    res.history.append((a, b))
    res.evals = 2

    while (b - a) > tol:
        if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1
            x1 = b - g * (b - a)
            f1 = f(x1)
        else:
            a = x1
            x1 = x2
            f1 = f2
            x2 = a + g * (b - a)
            f2 = f(x2)
        res.evals += 1
        res.history.append((a, b))

    res.x = 0.5 * (a + b)
    res.fx = f(res.x)
    res.evals += 1
    res.a = a
    res.b = b
    return res


class FitResult:
    def __init__(self, c0: float, amp: float, sse: float):
        self.c0 = c0
        self.amp = amp
        self.sse = sse


def fit_for_rate(r: float, years: List[float] = YEARS, co2: List[float] = CO2) -> FitResult:
    """
    Fits model CO2(t) = C0 + A * exp(r * (t - 1959)) using variable projection.
    Returns optimal C0, A (amp), and SSE.
    """
    n = len(years)
    base_year = years[0]
    e = [math.exp(r * (years[i] - base_year)) for i in range(n)]

    mean_e = sum(e) / n
    mean_y = sum(co2) / n

    sxy = sum((e[i] - mean_e) * (co2[i] - mean_y) for i in range(n))
    sxx = sum((e[i] - mean_e) * (e[i] - mean_e) for i in range(n))

    amp = sxy / sxx
    c0 = mean_y - amp * mean_e

    sse = sum((c0 + amp * e[i] - co2[i]) ** 2 for i in range(n))
    return FitResult(c0=c0, amp=amp, sse=sse)


def sse_of_rate(r: float) -> float:
    return fit_for_rate(r).sse


def main():
    lo = 0.005
    hi = 0.10

    # 1. Test function
    test = fibonacci_search(lambda x: (x - 2.0) ** 2 + 1.0, 0.0, 5.0, 1e-6)
    print(f"Test f(x)=(x-2)^2+1 on [0,5]: x*={test.x:.6f} f*={test.fx:.6f} evals={test.evals}\n")

    # 2. Real-world NOAA Mauna Loa CO2 Optimization
    fib = fibonacci_search(sse_of_rate, lo, hi, 1e-8)
    best = fit_for_rate(fib.x)
    rmse = math.sqrt(best.sse / len(YEARS))

    print("Fibonacci search on NOAA Mauna Loa CO2 data (1959-2023)")
    print(f"Optimal growth rate r* = {fib.x:.6f} per year")
    print(f"Final interval = [{fib.a:.8f}, {fib.b:.8f}]")
    print(f"Function evaluations = {fib.evals}")
    print(f"Model: CO2(t) = {best.c0:.2f} + {best.amp:.4f} * exp({fib.x:.5f} * (year - 1959))")
    print(f"SSE = {best.sse:.2f} ppm^2, RMSE = {rmse:.3f} ppm")
    print(f"Doubling time of excess CO2 = {math.log(2.0) / fib.x:.1f} years")

    for y in [2030, 2050]:
        pred = best.c0 + best.amp * math.exp(fib.x * (y - 1959))
        print(f"Extrapolated CO2 in {y} = {pred:.1f} ppm")

    # 3. Method comparison
    gs = golden_section_search(sse_of_rate, lo, hi, 1e-8)
    grid_n = 100000
    grid_best = lo
    grid_min = sse_of_rate(lo)
    for i in range(1, grid_n + 1):
        r = lo + (hi - lo) * i / grid_n
        s = sse_of_rate(r)
        if s < grid_min:
            grid_min = s
            grid_best = r

    print("\nMethod comparison (tolerance 1e-8)")
    print(f"Fibonacci      r* = {fib.x:.6f}  evals = {fib.evals}")
    print(f"Golden section r* = {gs.x:.6f}  evals = {gs.evals}")
    print(f"Grid search    r* = {grid_best:.6f}  evals = {grid_n + 1}")

    print("\nEvaluations needed versus tolerance")
    print(f"{'tol':<10} {'Fibonacci':<10} {'Golden':<10}")
    for tol in [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8]:
        a = fibonacci_search(sse_of_rate, lo, hi, tol)
        b = golden_section_search(sse_of_rate, lo, hi, tol)
        print(f"{tol:<10.0e} {a.evals:<10} {b.evals:<10}")


if __name__ == "__main__":
    main()
