"""Smoke test de l'adapter A'Space pour adk-recipes (contrat seul).

Hors-ligne : validation locale (manifest + structure) d'une recette dans
le repo, sans déployer ni exécuter aucune recette, sans appel réseau,
sans appel modèle. Les variables d'activation télémétrie sont
explicitement absentes.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GEL = "a93b9cc"
RECIPE = "core/python/rag-agent-search"


def _git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True,
                          check=True).stdout.strip()


def test_gel_is_ancestor():
    assert _git("merge-base", "HEAD", GEL) == _git("rev-parse", GEL)


def test_only_adapter_changed():
    out = _git("diff", "--name-only", GEL, "HEAD")
    assert out, "aucun fichier changé depuis le gel"
    assert all(p.startswith("aspace-adk-recipes-adapter/")
               for p in out.splitlines())


def test_contract():
    c = json.loads((HERE / "contract.json").read_text())
    assert c["upstream"]["frozen_commit"] == GEL
    assert c["version"] == "0.1.0"


def test_telemetry_env_absent():
    for var in ("AQA_TRACES_GCS_BUCKET", "LOGS_BUCKET_NAME"):
        assert var not in os.environ, f"{var} défini"


def test_validate_offline(monkeypatch):
    sys.path.insert(0, str(ROOT / "tools"))
    import validate
    # manifest + structure sur une recette réelle, en lecture seule.
    monkeypatch.setattr(sys, "argv", ["validate", "manifest", RECIPE])
    assert validate._dispatch() == 0
    monkeypatch.setattr(sys, "argv", ["validate", "structure", RECIPE])
    assert validate._dispatch() == 0


def test_validate_rejects_bad_scope(monkeypatch):
    sys.path.insert(0, str(ROOT / "tools"))
    import validate
    monkeypatch.setattr(
        sys, "argv", ["validate", "manifest", "core/python/nonexistent-recipe"])
    assert validate._dispatch() != 0
