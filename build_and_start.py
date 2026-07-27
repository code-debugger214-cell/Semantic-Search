"""
Unified Production Build & Server Launcher for RAG & Retrieval Studio.

1. Builds the React frontend static bundle (`frontend/dist`).
2. Launches the FastAPI production server on http://0.0.0.0:8000.
"""
import os
import subprocess
import sys
from pathlib import Path


def main():
    root_dir = Path(__file__).resolve().parent
    frontend_dir = root_dir / "frontend"

    print("==================================================")
    print("[BUILD] Building Frontend Production Bundle (Vite)...")
    print("==================================================")

    # Detect npm command for Windows/Linux
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"

    try:
        build_res = subprocess.run([npm_cmd, "run", "build"], cwd=str(frontend_dir), check=True)
        print("[OK] Frontend production build complete!")
    except Exception as e:
        print(f"[WARN] Warning during npm run build: {e}")
        print("Continuing with existing frontend/dist directory...")

    dist_dir = frontend_dir / "dist"
    if not dist_dir.exists():
        print("[ERROR] frontend/dist does not exist. Build failed.")
        sys.exit(1)

    print("\n==================================================")
    print("[START] Starting Unified Production Server on Port 8000...")
    print("==================================================")
    print(">> Open your browser at: http://localhost:8000")
    print("==================================================\n")

    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, workers=1)


if __name__ == "__main__":
    main()
