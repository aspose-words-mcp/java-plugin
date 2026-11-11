"""Pinned, offline Gist examples owned by the Words documentation plugin.

Run this module explicitly to populate the cache; extraction never fetches URLs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CACHE = PLUGIN_ROOT / "sources/gist-examples.json"
GIST = re.compile(r"{{(?P<open>[<%])\s*gist\b(?P<args>.*?)\s*(?P<close>[>%])}}", re.S)


def references(text: str):
    for match in GIST.finditer(text):
        args = shlex.split(match["args"])
        if (
            (match["open"], match["close"]) not in {("<", ">"), ("%", "%")}
            or len(args) != 3
            or not re.fullmatch(r"[\w-]+", args[0])
            or not re.fullmatch(r"[a-fA-F0-9]+", args[1])
            or not args[2] or "/" in args[2] or "\\" in args[2]
            or args[2] in {".", ".."}
        ):
            raise ValueError("Gist examples require an owner, hexadecimal ID and filename")
        yield match, tuple(args)


def key(reference: tuple[str, str, str]) -> str:
    return "/".join(reference)


def read_cache(path: Path) -> dict:
    if not path.exists():
        return {"schema": 1, "examples": {}}
    cache = json.loads(path.read_text(encoding="utf-8"))
    if cache.get("schema") != 1 or not isinstance(cache.get("examples"), dict):
        raise ValueError("Invalid Words Gist example cache")
    return cache


def checked_code(entry: dict) -> str:
    code = entry["code"]
    if (
        not isinstance(code, str) or not code.strip()
        or hashlib.sha256(code.encode()).hexdigest() != entry["sha256"]
        or not re.fullmatch(r"[a-fA-F0-9]{40}", entry["revision"])
    ):
        raise ValueError("Gist cache revision/content checksum validation failed")
    return code


UNAVAILABLE_MARKER = "<!-- adcs:gist-unavailable {key} -->"
UNAVAILABLE_RE = re.compile(r"^<!-- adcs:gist-unavailable (\S+) -->$", re.M)


def validated_entry(entry: dict) -> str | None:
    """Return code, or None for an example recorded as absent upstream."""
    if entry.get("unavailable") is True:
        if (
            not re.fullmatch(r"[a-fA-F0-9]{40}", str(entry.get("revision", "")))
            or not str(entry.get("reason", "")).strip()
        ):
            raise ValueError("Gist cache unavailable-entry validation failed")
        return None
    return checked_code(entry)


def expand(text: str, *, cache_path: Path = DEFAULT_CACHE) -> str:
    matches = list(references(text))
    if not matches:
        return text
    cache = read_cache(cache_path)
    for match, reference in reversed(matches):
        entry = cache["examples"].get(key(reference))
        if entry is None:
            raise ValueError(
                f"Missing Gist example {key(reference)}; run gist_examples preparation"
            )
        code = validated_entry(entry)
        if code is None:
            # Recorded during preparation as absent from the pinned Gist revision.
            # Keep the page; the docs extractor turns this marker into a warning.
            marker = UNAVAILABLE_MARKER.format(key=key(reference))
            text = text[:match.start()] + "\n" + marker + "\n" + text[match.end():]
            continue
        extension = Path(reference[2]).suffix.lower()
        language = {
            ".java": "java", ".kt": "kotlin", ".xml": "xml", ".json": "json",
            ".cs": "csharp", ".vb": "vbnet",
        }.get(extension, "text")
        # The existing Markdown parser supports triple fences. Refuse embedded
        # closing fences instead of silently corrupting the surrounding content.
        if any(line.lstrip().startswith("```") for line in code.splitlines()):
            raise ValueError(f"Unsupported Markdown fence inside Gist {key(reference)}")
        replacement = f"\n```{language}\n{code.rstrip()}\n```\n"
        text = text[:match.start()] + replacement + text[match.end():]
    return text


def prepare(source_root: Path, cache_path: Path, *, refresh: bool = False) -> dict:
    if not source_root.is_dir():
        raise ValueError(f"Documentation source directory does not exist: {source_root}")
    refs = sorted({
        reference for path in source_root.rglob("*.md")
        for _, reference in references(path.read_text(encoding="utf-8-sig"))
    })
    if not refs:
        raise ValueError("No Gist examples found in the selected documentation source")
    cache = read_cache(cache_path)
    pending = []
    for reference in refs:
        existing = cache["examples"].get(key(reference))
        if existing is not None and not refresh:
            validated_entry(existing)
        else:
            pending.append(reference)
    unavailable: list[str] = []
    with TemporaryDirectory(prefix="words-gists-") as temporary:
        for gist_id in sorted({ref[1] for ref in pending}):
            checkout = Path(temporary) / gist_id
            subprocess.run(
                # No working tree: files are read as blobs below, so long Gist file
                # names never become filesystem paths (Windows MAX_PATH).
                ["git", "-c", "core.longpaths=true", "clone", "--depth", "1",
                 "--no-checkout", "https://gist.github.com/" + gist_id + ".git",
                 str(checkout)],
                check=True, timeout=180,
            )
            revision = subprocess.check_output(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True, timeout=30,
            ).strip()
            listing = subprocess.check_output(
                ["git", "-C", str(checkout), "ls-tree", "-z", revision], timeout=30,
            ).decode("utf-8")
            blobs = {}
            for record in filter(None, listing.split("\0")):
                meta, _, name = record.partition("\t")
                if meta.split()[1] == "blob":
                    blobs[name] = meta.split()[2]
            for reference in (ref for ref in pending if ref[1] == gist_id):
                if reference[2] not in blobs:
                    # Upstream documentation references a file the Gist does not
                    # contain. Record that fact with its revision as evidence.
                    cache["examples"][key(reference)] = {
                        "unavailable": True, "revision": revision,
                        "reason": "file not present in Gist revision",
                        "source_url":
                            f"https://gist.github.com/{reference[0]}/{gist_id}/{revision}",
                    }
                    unavailable.append(key(reference))
                    continue
                code = subprocess.check_output(
                    ["git", "-C", str(checkout), "cat-file", "blob", blobs[reference[2]]],
                    timeout=30,
                ).decode("utf-8-sig")
                entry = {
                    "revision": revision, "code": code,
                    "sha256": hashlib.sha256(code.encode()).hexdigest(),
                    "source_url": f"https://gist.github.com/{reference[0]}/{gist_id}/{revision}",
                }
                checked_code(entry)
                cache["examples"][key(reference)] = entry
    # Write only after every referenced file has been fetched and validated.
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = cache_path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary_path.replace(cache_path)
    newly_unavailable = len(unavailable)
    unavailable += [
        key(ref) for ref in refs
        if key(ref) not in unavailable and cache["examples"][key(ref)].get("unavailable")
    ]
    return {
        "references": len(refs), "downloaded": len(pending) - newly_unavailable,
        "unavailable": sorted(unavailable), "cache": str(cache_path),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root", type=Path, default=PLUGIN_ROOT / "sources/documentation/en/java"
    )
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--refresh", action="store_true", help="Explicitly update pinned examples")
    args = parser.parse_args()
    print(json.dumps(prepare(args.source_root, args.cache, refresh=args.refresh)))


if __name__ == "__main__":
    main()
