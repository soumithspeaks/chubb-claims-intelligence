import subprocess
import sys
from pathlib import Path

def run_streamlit():
    python_path = sys.executable
    streamlit_script = str(Path(__file__).parent / 'app' / 'frontend' / 'enhanced_app.py')
    
    cmd = [
        python_path, '-m', 'streamlit', 'run',
        streamlit_script,
        '--server.port=8502',
        '--server.address=0.0.0.0',
        '--server.headless=true'
    ]
    
    print("Starting Streamlit...")
    process = subprocess.Popen(cmd)
    print("Streamlit should be running at http://localhost:8502")
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()

if __name__ == '__main__':
    run_streamlit()