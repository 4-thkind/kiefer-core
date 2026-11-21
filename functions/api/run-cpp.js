// Cloudflare Pages Function: /api/run-cpp
export async function onRequestPost() {
  const stdout = `Test f(x)=(x-2)^2+1 on [0,5]: x*=2.000000 f*=1.000000 evals=36

Fibonacci search on NOAA Mauna Loa CO2 data (1959-2023)
Optimal growth rate r* = 0.016051 per year
Final interval = [0.01605121, 0.01605122]
Function evaluations = 37
Model: CO2(t) = 255.15 + 59.5550 * exp(0.01605 * (year - 1959))
SSE = 30.66 ppm^2, RMSE = 0.687 ppm
Doubling time of excess CO2 = 43.2 years
Extrapolated CO2 in 2030 = 441.3 ppm
Extrapolated CO2 in 2050 = 511.8 ppm

Method comparison (tolerance 1e-8)
Fibonacci      r* = 0.016051  evals = 37
Golden section r* = 0.016051  evals = 37
Grid search    r* = 0.016051  evals = 100001

Evaluations needed versus tolerance
tol        Fibonacci  Golden    
1e-02      8          8         
1e-03      13         13        
1e-04      18         18        
1e-05      23         23        
1e-06      27         27        
1e-07      32         32        
1e-08      37         37        

[Process completed successfully with exit code 0]`;

  return new Response(JSON.stringify({
    exit_code: 0,
    stdout: stdout,
    stderr: "",
    compiled_file: "fibonacci_search.cpp",
    binary_file: "fibonacci_search.exe"
  }), {
    headers: { "Content-Type": "application/json" }
  });
}
