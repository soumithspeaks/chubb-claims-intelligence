import subprocess
import sys
import os
from pathlib import Path

def run_backend():
    """Run the FastAPI backend server"""
    try:
        # Add the parent directory to Python path
        current_dir = Path(__file__).parent.absolute()
        sys.path.append(str(current_dir))
        
        # Import and run the FastAPI app
        from app.api.main import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"Error starting backend: {e}")
        sys.exit(1)

def run_frontend():
    """Run the Next.js frontend development server"""
    try:
        frontend_dir = Path(__file__).parent / "chubb-claims-intelligence"
        if not frontend_dir.exists():
            print(f"Frontend directory not found at {frontend_dir}")
            sys.exit(1)
            
        # Install dependencies if needed
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        # Start the development server
        subprocess.run(["npm", "run", "dev"], cwd=frontend_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running frontend: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    """Main entry point to run both frontend and backend"""
    try:
        # Start backend in a separate process
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.api.main:app", "--reload", "--port", "8000"],
            cwd=Path(__file__).parent
        )
        
        # Start frontend
        run_frontend()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_process.terminate()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()