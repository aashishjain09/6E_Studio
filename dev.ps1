$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvPath = Join-Path $root "venv"

if (-Not (Test-Path $venvPath)) {
    python -m venv $venvPath
}

$activate = Join-Path $venvPath "Scripts\Activate.ps1"
if (-Not (Test-Path $activate)) {
    Write-Error "Unable to locate virtual environment activation script at $activate"
    exit 1
}

Write-Host "Activating virtual environment..."
& $activate

Write-Host "Installing backend dependencies..."
pip install --upgrade pip
pip install -r "$root\backend\requirements.txt"
Write-Host "Installing frontend dependencies..."
pip install -r "$root\frontend\requirements.txt"

Write-Host "Starting backend and frontend in development mode..."
Start-Process -NoNewWindow -FilePath "$venvPath\Scripts\python.exe" -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"
Start-Process -NoNewWindow -FilePath "$venvPath\Scripts\python.exe" -ArgumentList "-m", "streamlit", "run", "$root\frontend\app.py", "--server.port=8501"

Write-Host "Backend: http://127.0.0.1:8000"
Write-Host "Frontend: http://127.0.0.1:8501"
