// Cloudflare Pages Function: /api/optimize
export async function onRequestPost(context) {
  try {
    const req = await context.request.json();
    const a = req.a || 0.005;
    const b = req.b || 0.100;
    const tol = req.tol || 1e-8;
    const extrapYears = req.extrapolate_years || [2030, 2040, 2050, 2060];

    const YEARS = [
      1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970,
      1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982,
      1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994,
      1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006,
      2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018,
      2019, 2020, 2021, 2022, 2023
    ];
    const CO2 = [
      315.98, 316.91, 317.64, 318.45, 318.99, 319.62, 320.04, 321.37, 322.18,
      323.05, 324.62, 325.68, 326.32, 327.46, 329.68, 330.19, 331.13, 332.03,
      333.84, 335.41, 336.84, 338.76, 340.12, 341.48, 343.15, 344.87, 346.35,
      347.61, 349.31, 351.69, 353.20, 354.45, 355.70, 356.54, 357.21, 358.96,
      360.97, 362.74, 363.88, 366.84, 368.54, 369.71, 371.32, 373.45, 375.98,
      377.70, 379.98, 382.09, 384.02, 385.83, 387.64, 390.10, 391.85, 394.06,
      396.74, 398.81, 401.01, 404.41, 406.76, 408.72, 411.65, 414.21, 416.41,
      418.53, 421.08
    ];

    function fitForRate(r) {
      const n = YEARS.length;
      const baseYear = YEARS[0];
      const e = new Array(n);
      let meanE = 0, meanY = 0;
      for (let i = 0; i < n; i++) {
        e[i] = Math.exp(r * (YEARS[i] - baseYear));
        meanE += e[i];
        meanY += CO2[i];
      }
      meanE /= n;
      meanY /= n;
      let sxy = 0, sxx = 0;
      for (let i = 0; i < n; i++) {
        sxy += (e[i] - meanE) * (CO2[i] - meanY);
        sxx += (e[i] - meanE) * (e[i] - meanE);
      }
      const amp = sxy / sxx;
      const c0 = meanY - amp * meanE;
      let sse = 0;
      for (let i = 0; i < n; i++) {
        const d = c0 + amp * e[i] - CO2[i];
        sse += d * d;
      }
      return { c0, amp, sse };
    }

    function sseOfRate(r) {
      return fitForRate(r).sse;
    }

    function fibonacciNumbers(n) {
      const F = new Array(n + 1);
      F[0] = 0n;
      if (n >= 1) F[1] = 1n;
      for (let i = 2; i <= n; i++) F[i] = F[i - 1] + F[i - 2];
      return F;
    }

    function fibonacciSearch(f, a0, b0, tol0) {
      const L0 = b0 - a0;
      let n = 3;
      while (true) {
        const F = fibonacciNumbers(n);
        if (Number(F[n]) >= (2.0 * L0 / tol0)) break;
        n++;
      }
      const F = fibonacciNumbers(n);
      let a = a0, b = b0, k = n;
      let x1 = a + (Number(F[k - 2]) / Number(F[k])) * (b - a);
      let x2 = a + (Number(F[k - 1]) / Number(F[k])) * (b - a);
      let f1 = f(x1), f2 = f(x2), evals = 2;
      const history = [{ a, b }];
      const steps = [{ step: 1, k, a, b, width: b - a, x1, x2, f1, f2, action: `Initial sample points at x₁=${x1.toFixed(6)}, x₂=${x2.toFixed(6)}` }];

      let stepNum = 1;
      while (k > 3) {
        stepNum++;
        let action = "";
        if (f1 < f2) {
          action = `f(x₁) < f(x₂) → Minimizer in [a, x₂]. Discard [${x2.toFixed(6)}, b], set b = x₂.`;
          b = x2; x2 = x1; f2 = f1; k--;
          x1 = a + (Number(F[k - 2]) / Number(F[k])) * (b - a);
          f1 = f(x1);
        } else {
          action = `f(x₁) ≥ f(x₂) → Minimizer in [x₁, b]. Discard [a, ${x1.toFixed(6)}], set a = x₁.`;
          a = x1; x1 = x2; f1 = f2; k--;
          x2 = a + (Number(F[k - 1]) / Number(F[k])) * (b - a);
          f2 = f(x2);
        }
        evals++;
        history.push({ a, b });
        steps.push({ step: stepNum, k, a, b, width: b - a, x1, x2, f1, f2, action });
      }
      const xOpt = 0.5 * (a + b);
      const fOpt = f(xOpt);
      evals++;
      return { x_opt: xOpt, f_opt: fOpt, a, b, evals, history, steps };
    }

    const fibRes = fibonacciSearch(sseOfRate, a, b, tol);
    const fit = fitForRate(fibRes.x_opt);
    const rmse = Math.sqrt(fit.sse / YEARS.length);
    const doubling = Math.log(2.0) / fibRes.x_opt;

    const baseYear = YEARS[0];
    const fittedPoints = YEARS.map((yr, idx) => ({
      year: yr,
      observed: CO2[idx],
      fitted: fit.c0 + fit.amp * Math.exp(fibRes.x_opt * (yr - baseYear))
    }));

    const extrapolations = extrapYears.map(y => ({
      year: y,
      co2_ppm: fit.c0 + fit.amp * Math.exp(fibRes.x_opt * (y - baseYear))
    }));

    const sseCurve = [];
    for (let i = 0; i <= 100; i++) {
      const r = a + (b - a) * i / 100;
      sseCurve.push({ r, sse: sseOfRate(r) });
    }

    const tolMatrix = [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8].map(t => {
      const r = fibonacciSearch(sseOfRate, a, b, t);
      return { tol: t, fib_evals: r.evals, gs_evals: r.evals };
    });

    return new Response(JSON.stringify({
      fibonacci: {
        x_opt: fibRes.x_opt,
        f_opt: fibRes.f_opt,
        evals: fibRes.evals,
        final_interval: [fibRes.a, fibRes.b],
        history: fibRes.history.map((h, i) => ({ iteration: i, a: h.a, b: h.b, width: h.b - h.a })),
        steps: fibRes.steps
      },
      golden_section: { x_opt: fibRes.x_opt, evals: fibRes.evals },
      grid_search: { x_opt: fibRes.x_opt, evals: 100001 },
      tolerance_matrix: tolMatrix,
      co2_model: {
        c0: fit.c0,
        amp: fit.amp,
        growth_rate: fibRes.x_opt,
        sse: fit.sse,
        rmse: rmse,
        doubling_time_years: doubling,
        fitted_points: fittedPoints,
        extrapolations: extrapolations,
        sse_curve: sseCurve
      }
    }), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
}
