"""Codex stdio entry point with the local Windows FreeCAD executable on PATH."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FREECAD_BIN = Path(r"C:\Program Files\FreeCAD 1.1\bin")
os.environ["PATH"] = str(FREECAD_BIN) + os.pathsep + os.environ.get("PATH", "")
os.environ.setdefault("FREECAD_MCP_WORK_DIR", str(ROOT / "work" / "headless"))

from freecad_mcp.server import main

if __name__ == "__main__":
    main()
