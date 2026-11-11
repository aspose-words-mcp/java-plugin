"""Shared request builder for the stdlib unittest suite (no engine needed)."""

import json
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((PLUGIN / "plugin.json").read_text(encoding="utf-8"))
FIXTURES = PLUGIN / "tests" / "fixtures"


def request(kind, raw, relative, **overrides):
    source = MANIFEST["sources"][kind]
    payload = {
        "contract": MANIFEST["contract"], "plugin_id": MANIFEST["plugin_id"],
        "product_id": MANIFEST["product_id"], "language": MANIFEST["language"],
        "operation": "extract", "source_kind": kind, "repo_id": source["repo_id"],
        "product_family": "aspose", "source_path": source["path"] + "/" + relative,
        "relative_repo_path": relative, "source_prefix": source["prefix"],
        "layout_detection": source["layout"], "source_revision": "fixture-sha",
        "canonical_base_url": source["canonical_base_url"], "raw_markdown": raw,
    }
    payload.update(overrides)
    return payload


def run_worker(payload):
    """Run the source launcher exactly as the engine does: isolated subprocess."""
    return subprocess.run(
        [sys.executable, "-I", str(PLUGIN / "worker.py")],
        input=json.dumps(payload), capture_output=True, text=True,
    )


def extract_api(fixture, type_slug):
    relative = f"english/java/com.aspose.words/{type_slug}/_index.md"
    raw = (FIXTURES / fixture).read_text(encoding="utf-8")
    result = run_worker(request("apiref", raw, relative))
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)["result"]
