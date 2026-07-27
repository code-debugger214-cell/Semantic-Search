"""
Entrypoint script to launch the Streamlit Web Application.

Usage:
    python run_app.py
"""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    ui_path = Path(__file__).parent / "app" / "ui.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(ui_path)]
    print(f"Launching Streamlit App: {' '.join(cmd)}")
    subprocess.run(cmd)
