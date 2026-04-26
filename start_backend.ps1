$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$pythonCandidates = @(
    (Join-Path $PSScriptRoot ".venv-local\Scripts\python.exe"),
    (Join-Path $PSScriptRoot ".venv\Scripts\python.exe"),
    "py -3.12",
    "python"
)

$selectedPython = $null

foreach ($candidate in $pythonCandidates) {
    if ($candidate -like "*.exe") {
        if (Test-Path $candidate) {
            try {
                & $candidate --version *> $null
                $selectedPython = @($candidate)
                break
            } catch {
            }
        }
        continue
    }

    try {
        & powershell -NoProfile -Command "$candidate --version" *> $null
        $selectedPython = $candidate.Split(" ")
        break
    } catch {
    }
}

if (-not $selectedPython) {
    throw "No working Python interpreter was found. Install Python 3.12 or create .venv-local."
}

$pythonExe = $selectedPython[0]
$pythonArgs = @()
if ($selectedPython.Length -gt 1) {
    $pythonArgs = $selectedPython[1..($selectedPython.Length - 1)]
}

& $pythonExe @pythonArgs -m uvicorn backend_app:app --host 127.0.0.1 --port 8011
