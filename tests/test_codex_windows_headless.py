"""Exercise the actual FreeCADCmd CLI, whose -c differs from Python's."""
import os
from pathlib import Path

import pytest

from freecad_mcp.headless import run_headless

FREECADCMD = Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")
pytestmark = pytest.mark.skipif(os.name != "nt" or not FREECADCMD.exists(), reason="Local Windows FreeCAD integration")


def test_real_freecadcmd_builds_valid_solid(tmp_path, monkeypatch):
    monkeypatch.setattr("freecad_mcp.headless._script_dir", lambda: tmp_path)
    result = run_headless(
        "import Part\ns = Part.makeBox(40,25,8)\nassert s.isValid()\nprint('volume:', s.Volume)",
        30, [str(FREECADCMD)],
    )
    assert result["success"], result
    assert "volume: 8000" in result["output"]
    assert not list(tmp_path.glob("*.py"))


def test_real_freecadcmd_reports_script_failure(tmp_path, monkeypatch):
    monkeypatch.setattr("freecad_mcp.headless._script_dir", lambda: tmp_path)
    result = run_headless("raise ValueError('integration-failure')", 30, [str(FREECADCMD)])
    assert not result["success"], result
    assert result["returncode"] == 1
    assert "ValueError: integration-failure" in result["output"]
    assert not list(tmp_path.glob("*.py"))
