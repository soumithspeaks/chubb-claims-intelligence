import subprocess
import sys
from pathlib import Path

# Get the absolute path of the project root
project_root = Path(__file__).parent

# Add the project root to Python path
sys.path.insert(0, str(project_root))

# Run the Streamlit app
if __name__ == "__main__":
    app_path = project_root / "app" / "frontend" / "enhanced_app.py"
    subprocess.run([
        "streamlit",
        "run",
        str(app_path),
        "--server.port=8501",
        "--server.address=localhost"
    ])