#include <algorithm>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <functional>
#include <iostream>
#include <vector>

using Func = std::function<double(double)>;

struct SearchResult {
    double x;
    double fx;
    double a;
    double b;
    int evals;
    std::vector<std::pair<double, double>> history;
};

std::vector<long long> fibonacciNumbers(int n) {
    std::vector<long long> F(n + 1);
    F[0] = 0;
    if (n >= 1) F[1] = 1;
    for (int i = 2; i <= n; ++i) F[i] = F[i - 1] + F[i - 2];
    return F;
}

SearchResult fibonacciSearch(const Func& f, double a, double b, double tol) {
    const double L0 = b - a;
    int n = 3;
    while (fibonacciNumbers(n)[n] < 2.0 * L0 / tol) ++n;
    const std::vector<long long> F = fibonacciNumbers(n);

    SearchResult res;
    res.history.push_back({a, b});

    int k = n;
    double x1 = a + static_cast<double>(F[k - 2]) / F[k] * (b - a);
    double x2 = a + static_cast<double>(F[k - 1]) / F[k] * (b - a);
    double f1 = f(x1);
    double f2 = f(x2);
    res.evals = 2;

    while (k > 3) {
        if (f1 < f2) {
            b = x2;
            x2 = x1;
            f2 = f1;
            --k;
            x1 = a + static_cast<double>(F[k - 2]) / F[k] * (b - a);
            f1 = f(x1);
        } else {
            a = x1;
            x1 = x2;
            f1 = f2;
            --k;
            x2 = a + static_cast<double>(F[k - 1]) / F[k] * (b - a);
            f2 = f(x2);
        }
        ++res.evals;
        res.history.push_back({a, b});
    }

    res.x = 0.5 * (a + b);
    res.fx = f(res.x);
    ++res.evals;
    res.a = a;
    res.b = b;
    return res;
}

SearchResult goldenSectionSearch(const Func& f, double a, double b, double tol) {
    const double g = (std::sqrt(5.0) - 1.0) / 2.0;
    double x1 = b - g * (b - a);
    double x2 = a + g * (b - a);
    double f1 = f(x1);
    double f2 = f(x2);
    SearchResult res;
    res.evals = 2;

    while (b - a > tol) {
        if (f1 < f2) {
            b = x2;
            x2 = x1;
            f2 = f1;
            x1 = b - g * (b - a);
            f1 = f(x1);
        } else {
            a = x1;
            x1 = x2;
            f1 = f2;
            x2 = a + g * (b - a);
            f2 = f(x2);
        }
        ++res.evals;
    }

    res.x = 0.5 * (a + b);
    res.fx = f(res.x);
    ++res.evals;
    res.a = a;
    res.b = b;
    return res;
}

const std::vector<double> YEARS = {
    1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970,
    1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982,
    1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994,
    1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006,
    2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018,
    2019, 2020, 2021, 2022, 2023};

const std::vector<double> CO2 = {
    315.98, 316.91, 317.64, 318.45, 318.99, 319.62, 320.04, 321.37, 322.18,
    323.05, 324.62, 325.68, 326.32, 327.46, 329.68, 330.19, 331.13, 332.03,
    333.84, 335.41, 336.84, 338.76, 340.12, 341.48, 343.15, 344.87, 346.35,
    347.61, 349.31, 351.69, 353.20, 354.45, 355.70, 356.54, 357.21, 358.96,
    360.97, 362.74, 363.88, 366.84, 368.54, 369.71, 371.32, 373.45, 375.98,
    377.70, 379.98, 382.09, 384.02, 385.83, 387.64, 390.10, 391.85, 394.06,
    396.74, 398.81, 401.01, 404.41, 406.76, 408.72, 411.65, 414.21, 416.41,
    418.53, 421.08};

struct Fit {
    double c0;
    double amp;
    double sse;
};

Fit fitForRate(double r) {
    const std::size_t n = YEARS.size();
    std::vector<double> e(n);
    double meanE = 0.0;
    double meanY = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        e[i] = std::exp(r * (YEARS[i] - YEARS[0]));
        meanE += e[i];
        meanY += CO2[i];
    }
    meanE /= n;
    meanY /= n;
    double sxy = 0.0;
    double sxx = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        sxy += (e[i] - meanE) * (CO2[i] - meanY);
        sxx += (e[i] - meanE) * (e[i] - meanE);
    }
    Fit fit;
    fit.amp = sxy / sxx;
    fit.c0 = meanY - fit.amp * meanE;
    fit.sse = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        const double d = fit.c0 + fit.amp * e[i] - CO2[i];
        fit.sse += d * d;
    }
    return fit;
}

double sseOfRate(double r) { return fitForRate(r).sse; }

int main() {
    const double lo = 0.005;
    const double hi = 0.10;

    SearchResult test = fibonacciSearch(
        [](double x) { return (x - 2.0) * (x - 2.0) + 1.0; }, 0.0, 5.0, 1e-6);
    std::printf("Test f(x)=(x-2)^2+1 on [0,5]: x*=%.6f f*=%.6f evals=%d\n\n",
                test.x, test.fx, test.evals);

    SearchResult fib = fibonacciSearch(sseOfRate, lo, hi, 1e-8);
    Fit best = fitForRate(fib.x);
    const double rmse = std::sqrt(best.sse / YEARS.size());

    std::printf("Fibonacci search on NOAA Mauna Loa CO2 data (1959-2023)\n");
    std::printf("Optimal growth rate r* = %.6f per year\n", fib.x);
    std::printf("Final interval = [%.8f, %.8f]\n", fib.a, fib.b);
    std::printf("Function evaluations = %d\n", fib.evals);
    std::printf("Model: CO2(t) = %.2f + %.4f * exp(%.5f * (year - 1959))\n",
                best.c0, best.amp, fib.x);
    std::printf("SSE = %.2f ppm^2, RMSE = %.3f ppm\n", best.sse, rmse);
    std::printf("Doubling time of excess CO2 = %.1f years\n", std::log(2.0) / fib.x);
    for (int y : {2030, 2050}) {
        std::printf("Extrapolated CO2 in %d = %.1f ppm\n", y,
                    best.c0 + best.amp * std::exp(fib.x * (y - 1959)));
    }

    SearchResult gs = goldenSectionSearch(sseOfRate, lo, hi, 1e-8);
    const int gridN = 100000;
    double gridBest = lo;
    double gridMin = sseOfRate(lo);
    for (int i = 1; i <= gridN; ++i) {
        const double r = lo + (hi - lo) * i / gridN;
        const double s = sseOfRate(r);
        if (s < gridMin) {
            gridMin = s;
            gridBest = r;
        }
    }

    std::printf("\nMethod comparison (tolerance 1e-8)\n");
    std::printf("Fibonacci     r* = %.6f  evals = %d\n", fib.x, fib.evals);
    std::printf("Golden section r* = %.6f  evals = %d\n", gs.x, gs.evals);
    std::printf("Grid search    r* = %.6f  evals = %d\n", gridBest, gridN + 1);

    std::printf("\nEvaluations needed versus tolerance\n");
    std::printf("%-10s %-10s %-10s\n", "tol", "Fibonacci", "Golden");
    for (double tol : {1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8}) {
        SearchResult a = fibonacciSearch(sseOfRate, lo, hi, tol);
        SearchResult b = goldenSectionSearch(sseOfRate, lo, hi, tol);
        std::printf("%-10.0e %-10d %-10d\n", tol, a.evals, b.evals);
    }

    std::ofstream curve("sse_curve.csv");
    curve << "r,sse\n";
    for (int i = 0; i <= 400; ++i) {
        const double r = lo + (hi - lo) * i / 400.0;
        curve << r << "," << sseOfRate(r) << "\n";
    }

    std::ofstream hist("history.csv");
    hist << "iteration,a,b,width\n";
    for (std::size_t i = 0; i < fib.history.size(); ++i) {
        hist << i << "," << fib.history[i].first << "," << fib.history[i].second
             << "," << fib.history[i].second - fib.history[i].first << "\n";
    }

    std::ofstream fitCsv("fit.csv");
    fitCsv << "year,observed,fitted\n";
    for (std::size_t i = 0; i < YEARS.size(); ++i) {
        fitCsv << YEARS[i] << "," << CO2[i] << ","
               << best.c0 + best.amp * std::exp(fib.x * (YEARS[i] - YEARS[0]))
               << "\n";
    }

    return 0;
}
