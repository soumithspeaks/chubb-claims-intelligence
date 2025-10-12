Write-Host "Activating Python Environment..."
& ./venv/Scripts/Activate.ps1

Write-Host "Installing required packages..."
pip install streamlit pillow

Write-Host "Launching Enhanced UI..."
streamlit run app/frontend/enhanced_app.py