"""
FastAPI Server connecting the Fibonacci Optimization Engine with the Mistral-styled Frontend.
"""

import subprocess
import os
import math
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import fibonacci_search as fib_engine

app = FastAPI(title="Fibonacci Search Optimization API", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class OptimizeRequest(BaseModel):
    problem_type: str = "noaa_co2"  # "noaa_co2", "quadratic_test", "custom"
    a: float = 0.005
    b: float = 0.10
    tol: float = 1e-8
    extrapolate_years: List[int] = [2030, 2040, 2050, 2060]
    c_param: Optional[float] = 2.0  # for quadratic test (x - c)^2 + d
    d_param: Optional[float] = 1.0


@app.get("/", response_class=HTMLResponse)
def get_index():
    index_file = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Index file not found.</h1>"


@app.get("/api/dataset")
def get_dataset():
    """Returns the NOAA Mauna Loa dataset."""
    return {
        "years": fib_engine.YEARS,
        "co2": fib_engine.CO2,
        "count": len(fib_engine.YEARS),
        "source": "NOAA Global Monitoring Laboratory, Mauna Loa Observatory (1959-2023)"
    }


@app.post("/api/optimize")
def run_optimization(req: OptimizeRequest):
    """
    Runs Fibonacci Search, Golden Section Search, and Grid Search with user inputs.
    """
    if req.b <= req.a:
        raise HTTPException(status_code=400, detail="Upper bracket 'b' must be strictly greater than lower bracket 'a'.")
    if req.tol <= 0:
        raise HTTPException(status_code=400, detail="Tolerance 'tol' must be positive.")

    if req.problem_type == "noaa_co2":
        f = fib_engine.sse_of_rate
        is_co2 = True
    elif req.problem_type == "quadratic_test":
        c = req.c_param if req.c_param is not None else 2.0
        d = req.d_param if req.d_param is not None else 1.0
        f = lambda x: (x - c) ** 2 + d
        is_co2 = False
    else:
        # Default quadratic
        f = lambda x: (x - 2.0) ** 2 + 1.0
        is_co2 = False

    # 1. Fibonacci Search
    fib_res = fib_engine.fibonacci_search(f, req.a, req.b, req.tol)

    # 2. Golden Section Search
    gs_res = fib_engine.golden_section_search(f, req.a, req.b, req.tol)

    # 3. Grid Search (sample 10,000 to 100,000 points depending on bracket)
    grid_points = 10000
    grid_best = req.a
    grid_min = f(req.a)
    for i in range(1, grid_points + 1):
        r = req.a + (req.b - req.a) * i / grid_points
        val = f(r)
        if val < grid_min:
            grid_min = val
            grid_best = r

    # Build response
    resp = {
        "fibonacci": {
            "x_opt": fib_res.x,
            "f_opt": fib_res.fx,
            "evals": fib_res.evals,
            "final_interval": [fib_res.a, fib_res.b],
            "history": [{"iteration": i, "a": h[0], "b": h[1], "width": h[1] - h[0]} for i, h in enumerate(fib_res.history)],
            "steps": fib_res.detailed_steps
        },
        "golden_section": {
            "x_opt": gs_res.x,
            "f_opt": gs_res.fx,
            "evals": gs_res.evals,
            "final_interval": [gs_res.a, gs_res.b]
        },
        "grid_search": {
            "x_opt": grid_best,
            "f_opt": grid_min,
            "evals": grid_points + 1
        }
    }

    # Tolerance matrix evaluation
    tol_benchmarks = []
    for test_tol in [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8]:
        fib_t = fib_engine.fibonacci_search(f, req.a, req.b, test_tol)
        gs_t = fib_engine.golden_section_search(f, req.a, req.b, test_tol)
        tol_benchmarks.append({
            "tol": test_tol,
            "fib_evals": fib_t.evals,
            "gs_evals": gs_t.evals
        })
    resp["tolerance_matrix"] = tol_benchmarks

    # If CO2 problem, compute model fit, curve and extrapolations
    if is_co2:
        fit = fib_engine.fit_for_rate(fib_res.x)
        n = len(fib_engine.YEARS)
        rmse = math.sqrt(fit.sse / n)
        doubling_time = math.log(2.0) / fib_res.x if fib_res.x > 0 else 0.0

        # Predictions for data years
        base_year = fib_engine.YEARS[0]
        fitted_points = []
        for yr, obs in zip(fib_engine.YEARS, fib_engine.CO2):
            pred = fit.c0 + fit.amp * math.exp(fib_res.x * (yr - base_year))
            fitted_points.append({"year": yr, "observed": obs, "fitted": pred})

        # Extrapolations
        extrapolations = []
        for y in req.extrapolate_years:
            val = fit.c0 + fit.amp * math.exp(fib_res.x * (y - base_year))
            extrapolations.append({"year": y, "co2_ppm": val})

        # SSE loss curve for plotting
        sse_curve = []
        num_curve_pts = 100
        for i in range(num_curve_pts + 1):
            r = req.a + (req.b - req.a) * i / num_curve_pts
            s = fib_engine.sse_of_rate(r)
            sse_curve.append({"r": r, "sse": s})

        resp["co2_model"] = {
            "c0": fit.c0,
            "amp": fit.amp,
            "growth_rate": fib_res.x,
            "sse": fit.sse,
            "rmse": rmse,
            "doubling_time_years": doubling_time,
            "fitted_points": fitted_points,
            "extrapolations": extrapolations,
            "sse_curve": sse_curve
        }

    return resp


@app.post("/api/run-cpp")
def run_cpp():
    """
    Executes the compiled C++ binary 'fibonacci_search.exe' and returns its raw terminal output.
    """
    exe_path = os.path.join(BASE_DIR, "fibonacci_search.exe")
    cpp_path = os.path.join(BASE_DIR, "fibonacci_search.cpp")

    # If exe doesn't exist, compile it
    if not os.path.exists(exe_path):
        try:
            compile_res = subprocess.run(
                ["g++", "-O2", "-std=c++14", "-o", "fibonacci_search.exe", "fibonacci_search.cpp"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=30
            )
            if compile_res.returncode != 0:
                raise HTTPException(status_code=500, detail=f"C++ Compilation failed: {compile_res.stderr}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to invoke g++ compiler: {str(e)}")

    try:
        run_res = subprocess.run(
            [exe_path],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "exit_code": run_res.returncode,
            "stdout": run_res.stdout,
            "stderr": run_res.stderr,
            "compiled_file": "fibonacci_search.cpp",
            "binary_file": "fibonacci_search.exe"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run C++ binary: {str(e)}")


@app.get("/api/csv/{filename}")
def download_csv(filename: str):
    """Downloads one of the generated CSV files."""
    if filename not in ["fit.csv", "history.csv", "sse_curve.csv"]:
        raise HTTPException(status_code=404, detail="File not found")
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        # Trigger C++ or python to generate
        fib_engine.main()
    return FileResponse(filepath, media_type="text/csv", filename=filename)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
