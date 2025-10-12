import subprocess
import os
import sys
from pathlib import Path

def main():
    """Launch both FastAPI backend and Gradio frontend"""
    project_root = Path(__file__).parent.parent
    
    # Start FastAPI backend
    backend_process = subprocess.Popen(
        [sys.executable, "app/main.py"],
        cwd=str(project_root)
    )
    
    # Start Gradio frontend
    frontend_process = subprocess.Popen(
        [sys.executable, "app/frontend/app.py"],
        cwd=str(project_root)
    )
    
    try:
        # Wait for both processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    main()