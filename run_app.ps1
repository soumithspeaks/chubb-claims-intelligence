# First, check if Python virtual environment exists
if (-not (Test-Path ".\venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Install Python requirements
Write-Host "Installing Python requirements..."
pip install -r requirements.txt

# Start FastAPI backend in a new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; uvicorn app.api.claims_api:app --reload --port 8000"

# Start Next.js frontend in a new terminal
Set-Location chubb-claims-intelligence
npm install
npm run dev