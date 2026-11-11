"""Structured API symbols for Aspose.Words for Java Reference pages.

Java Reference pages differ from the .NET corpus: one page documents a whole
type, and every constructor, method and field is a ``###`` section with an
explicit anchor (``### save(String fileName) {#save-java.lang.String}``)
followed by a fenced declaration and bold-labelled facets (``**Examples:**``,
``**Parameters:**``, ``**Returns:**``, ``**Remarks:**``). This module emits one
type row plus one row per member overload, each carrying its own anchor,
declaration, facets and section-local examples. Nothing is inferred from
example code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from adcs_words_java.chunking import StageDChunkRecord
from adcs_words_java.hugo_parser import HugoCodeBlock, HugoNormalizedPage, _unescape_prose


@dataclass(frozen=True, slots=True)
class ApiRefScope:
    """Retrieval scope for version-aware symbol lookup."""

    product: str
    language: str
    version: str
    locale: str = "en"


@dataclass(frozen=True, slots=True)
class ApiRefSymbol:
    """One API-reference symbol row (a class/method/field/...)."""

    snapshot_id: str
    product: str
    language: str
    version: str
    locale: str
    kind: str
    member_fqn: str
    name: str
    parent_fqn: str | None = None
    signature: str | None = None
    canonical_url: str | None = None
    is_deprecated: bool = False
    summary: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


_DOC_LOCALE_ALIASES = {"english": "en", "en-gb": "en", "en-us": "en"}
_SYMBOL_DOC_TYPE = "api_reference_symbol"
_ACCESS_MODIFIERS = ("public ", "protected ")
_MEMBER_HEADING_RE = re.compile(r"^(?P<label>.+?)\s*\{#(?P<anchor>[^}\s]+)\}\s*$")
_FACET_RE = re.compile(
    r"^\s*\*\*(?P<label>Examples|Parameters|Returns|Remarks|Note|Inheritance|"
    r"All Implemented Interfaces):\*\*\s*(?P<rest>.*)$"
)
_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_REFERENCE_DEF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*\S+\s*$")
_DEPRECATED_RE = re.compile(r"@Deprecated\b|\bis deprecated\b|\bobsolete\b", re.IGNORECASE)


def _normalize_locale(doc_locale: str | None) -> str:
    key = (doc_locale or "").strip().lower()
    if key in _DOC_LOCALE_ALIASES:
        return _DOC_LOCALE_ALIASES[key]
    if not key or key == "unknown":
        return "en"
    return key


def _first_sentence(text: str, *, max_len: int = 280) -> str | None:
    cleaned = " ".join(text.split())
    if not cleaned:
        return None
    index = cleaned.find(". ")
    if 0 < index <= max_len:
        return cleaned[: index + 1]
    return cleaned[:max_len].strip()


def _prose(lines: list[str]) -> str:
    """Readable narrative: decode escapes, keep link text, drop reference defs."""
    kept = []
    for line in lines:
        if _REFERENCE_DEF_RE.match(line):
            continue
        kept.append(_LINK_RE.sub(r"\1", _unescape_prose(line)).rstrip())
    text = "\n".join(kept)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


@dataclass(frozen=True, slots=True)
class _Section:
    """A contiguous span of source lines: the type preamble or one member."""

    start: int  # 1-based source line of the heading (or first body line)
    end: int  # exclusive
    heading: str | None
    anchor: str


def _sections(page: HugoNormalizedPage, body_start: int, total_lines: int) -> list[_Section]:
    boundaries = [h for h in page.headings if h.level <= 3]
    first = boundaries[0].line_hint if boundaries else total_lines + 1
    sections = [_Section(start=body_start, end=first, heading=None, anchor="#")]
    for index, heading in enumerate(boundaries):
        end = boundaries[index + 1].line_hint if index + 1 < len(boundaries) else total_lines + 1
        match = _MEMBER_HEADING_RE.match(heading.text)
        if heading.level != 3 or match is None:
            continue  # "## Methods" etc. only introduce member tables
        sections.append(
            _Section(
                start=heading.line_hint,
                end=end,
                heading=match["label"].strip(),
                anchor="#" + match["anchor"],
            )
        )
    return sections


def _facets(
    section: _Section, lines: list[str], blocks: list[HugoCodeBlock], declaration: HugoCodeBlock
) -> dict[str, Any]:
    """Split a section's prose by bold facet labels; collect examples."""
    in_code = {n for b in blocks for n in range(b.line_start, b.line_end + 1)}
    buckets: dict[str, list[str]] = {"description": []}
    current = "description"
    example_markers: list[int] = []
    for number in range(declaration.line_end + 1, section.end):
        if number in in_code or number > len(lines):
            continue
        line = lines[number - 1]
        match = _FACET_RE.match(line)
        if match:
            current = match["label"].casefold()
            if current == "examples":
                example_markers.append(number)
            buckets.setdefault(current, [])
            if match["rest"].strip():
                buckets[current].append(match["rest"])
            continue
        buckets.setdefault(current, []).append(line)
    examples = []
    for block in blocks:
        if block is declaration or not block.code.strip():
            continue
        if any(marker < block.line_start for marker in example_markers):
            examples.append({"language": block.language or "java", "code": block.code.strip("\n")})
    facets: dict[str, Any] = {key: _prose(value) for key, value in buckets.items()}
    facets["examples"] = examples
    return facets


def _member_identity(label: str, declaration: str, type_name: str) -> tuple[str, str]:
    """Return ``(member name, kind)`` from the heading label and declaration."""
    name = label.split("(", 1)[0].strip()
    if "(" not in declaration:
        return name, "field"
    if name == type_name:
        return name, "constructor"
    return name, "method"


def extract_symbols(
    *,
    page: HugoNormalizedPage,
    page_chunks: list[StageDChunkRecord],
    snapshot_id: str,
    kind_map: dict[str, str],
    raw_markdown: str = "",
) -> tuple[ApiRefSymbol, ...]:
    """One row for the type and one per member overload on a Java type page."""
    if not page_chunks:
        return ()
    head = page_chunks[0]
    if head.doc_type != _SYMBOL_DOC_TYPE or not head.symbol_fqn:
        return ()
    type_fqn = head.symbol_fqn
    type_name = type_fqn.rsplit(".", 1)[-1]
    package = type_fqn.rsplit(".", 1)[0] if "." in type_fqn else None
    lines = raw_markdown.removeprefix("﻿").splitlines()
    body_start = _body_start(lines)
    blocks = sorted(page.code_blocks, key=lambda b: b.line_start)

    common = {
        "snapshot_id": snapshot_id,
        "product": head.product_id,
        "language": head.programming_language,
        "version": head.version,
        "locale": _normalize_locale(head.doc_locale),
        "canonical_url": head.canonical_url,
    }
    symbols: list[ApiRefSymbol] = []
    seen: set[tuple[str, str]] = set()
    for section in _sections(page, body_start, len(lines)):
        scoped = [b for b in blocks if section.start <= b.line_start < section.end]
        declaration = next(
            (b for b in scoped if " ".join(b.code.split()).startswith(_ACCESS_MODIFIERS)),
            None,
        )
        if declaration is None:
            continue
        signature = " ".join(declaration.code.split()).split("{", 1)[0].strip().rstrip(";")
        facets = _facets(section, lines, scoped, declaration)
        if section.heading is None:
            member_fqn, name, parent = type_fqn, type_name, package
            kind = kind_map.get(type_fqn) or "class"
        else:
            name, kind = _member_identity(section.heading, signature, type_name)
            member_fqn, parent = f"{type_fqn}.{name}", type_fqn
        if (member_fqn, signature) in seen:
            continue
        seen.add((member_fqn, signature))
        description = facets.get("description") or ""
        remarks = "\n\n".join(t for t in (description, facets.get("remarks", "")) if t)
        payload: dict[str, Any] = {
            "section_anchor": section.anchor,
            "signature": signature,
            "examples": list(dict.fromkeys(e["code"] for e in facets["examples"])),
            "example_snippets": facets["examples"],
            "source_revision": head.source_revision,
        }
        if facets.get("parameters"):
            payload["parameters"] = facets["parameters"]
        if facets.get("returns"):
            payload["returns"] = facets["returns"]
        if remarks:
            payload["remarks"] = remarks
        if section.heading is None:
            for key in ("inheritance", "all implemented interfaces"):
                if facets.get(key):
                    payload[key.replace(" ", "_")] = facets[key]
        body = "\n\n".join(
            t for t in (signature, remarks, payload.get("parameters"), payload.get("returns")) if t
        )
        if body:
            payload["body"] = body
        symbols.append(
            ApiRefSymbol(
                **common,
                kind=kind,
                member_fqn=member_fqn,
                name=name,
                parent_fqn=parent,
                signature=signature,
                is_deprecated=bool(
                    _DEPRECATED_RE.search(declaration.code) or _DEPRECATED_RE.search(description)
                ),
                summary=_first_sentence(description) or name,
                payload=payload,
            )
        )
    return tuple(symbols)


def _body_start(lines: list[str]) -> int:
    """1-based first body line after Hugo front matter (matches the parser)."""
    if not lines or lines[0].strip() not in {"---", "+++"}:
        return 1
    delimiter = lines[0].strip()
    for index, line in enumerate(lines[1:], start=1):
        stripped = line.strip()
        if stripped == delimiter:
            return index + 2
        remainder = stripped[len(delimiter):]
        if stripped.startswith(delimiter) and remainder and remainder[0] != delimiter[0]:
            return index + 1
    return 1


def declaration_identifiers(page: HugoNormalizedPage) -> tuple[str, ...]:
    """Kept for API parity with the .NET plugin; Java uses the type declaration."""
    from adcs_words_java.normalized_document import java_type_declaration

    declared = java_type_declaration(page)
    return (declared[0],) if declared else ()
