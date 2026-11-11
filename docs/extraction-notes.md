# Aspose.Words for Java extractor: notes

This package owns discovery, documentation and API Reference extraction,
normalization, semantic chunking and structured API symbol extraction for
**Aspose.Words for Java** (`plugin_id: aspose.words.java`, `language: java`).
It has no runtime dependency on the engine or on another plugin.

## Source repositories

| Source | Repository | Branch | Prefix | Canonical base |
| --- | --- | --- | --- | --- |
| docs | `aspose-words-mcp/docs` | `master` | `en/java` | `https://docs.aspose.com/words/java` |
| apiref | `aspose-words-mcp/reference` | `main` | `english/java` | `https://reference.aspose.com/words/java` |

`plugin.json` is authoritative. See [source preparation](source-preparation.md)
for clone and Gist-cache commands and [source-audit.json](source-audit.json) for
the latest full-source extraction counts.

## Java API Reference model

Java Reference pages differ structurally from .NET:

- **One page per type.** `english/java/<package>/<type>/_index.md` documents the
  whole type. Constructors, methods and fields are `###` sections with explicit
  anchors, e.g. `### save(String fileName) {#save-java.lang.String}`, each
  followed by a fenced declaration and bold facets (`**Examples:**`,
  `**Parameters:**`, `**Returns:**`, `**Remarks:**`).
- **Identity.** FQNs are Java identities: `com.aspose.words.Document`,
  `com.aspose.words.Document.save`, `com.aspose.words.SaveFormat.DOCX`. The
  package keeps its directory spelling (`com.aspose.words.net.System.Data`); the
  type name comes from the leading declaration. Package and root pages are
  `api_reference_namespace` documents without symbols.
- **Symbols.** One type row (kind `class`/`interface`/`enum` from the
  declaration, parent = package) plus one row per member overload (kind
  `constructor`/`method`/`field`, parent = type). Overloads share `member_fqn`
  and differ by `signature` and `payload.section_anchor`. Each row carries its
  own parameters, returns, remarks and section-local examples
  (`example_snippets[].language = "java"`). Declarations are never examples.
- **Chunks.** Every chunk carries the anchor of the member it belongs to and a
  chunk never spans two members, so citations deep-link to
  `.../document/#save-java.lang.String`. Declarations are `api_signature` units,
  not executable snippets. `section_path` is `(type, member label, unit)` instead
  of every heading on the page. Chunk `symbol_fqn` stays the page type.
- **Canonical URLs.** Front-matter `/java/...` URLs resolve under the configured
  Java base; `/javascript/...` is not rewritten. Other rules match words-net.

### Upstream source defects handled

- `htmlversion` and `htmlsaveoptions`: HTML stripped from an example leaves an
  unbalanced fence. The parser closes a runaway fence at the next anchored member
  heading and emits `CODE_FENCE_RECOVERED_AT_MEMBER_HEADING` (7 occurrences).
- Prose contains literal `\uXXXX` sequences (`Anthropic’s`); they are decoded.
- The Java docs label many Java snippets `highlight csharp`. A `csharp` block is
  relabelled `java` only when it has clear Java evidence (`String[]`,
  `System.out.`, `import com.aspose`, a `.getX(...);`-style statement) and no C#
  idiom. Genuine C# (release-note API diffs), PHP-via-Java, shell and LINQ
  template snippets keep their declared label. On the July 2022 checkout this
  relabels 194 of 1,279 `csharp` blocks.

## Retrieval profile (serving only)

`retrieval-profile.json` (1.0.0) mirrors the Words/.NET intent with Java identities:

- mail merge → `com.aspose.words.MailMerge.execute`; with regions →
  `com.aspose.words.MailMerge.executeWithRegions`;
- Word/DOC/DOCX "to PDF"/"as PDF" → `com.aspose.words.Document.save`,
  `com.aspose.words.PdfSaveOptions`.

Java has no LowCode package: the .NET `Aspose.Words.LowCode` types live directly
in `com.aspose.words`. `excluded_namespaces` therefore lists the 25 equivalent
types (`Converter`, `MailMerger`, `Merger`, `Watermarker`, their `*Context`
types, ...) individually. Boundary matching keeps `MailMerge` and
`MergeFieldImageDimension` eligible. Profiles require the engine change that
accepts `com.<product>.` symbol prefixes. Restart the API to load profile changes.

## Verification (11 November 2026)

`PYTHONPATH=src python -m unittest discover -s tests`: all tests pass.
`scripts/audit_sources.py` on the sources above:

| Source | Revision | Pages | Errors | Chunks | Symbols | Warnings |
| --- | --- | --- | --- | --- | --- | --- |
| docs `en/java` | `1e946b4e` | 424 | 0 | 755 | 0 | 5 `UNCLOSED_CODE_FENCE` (upstream) |
| apiref `english/java` | `90aec069` | 836 | 0 | 19,976 | 18,439 | 7 `CODE_FENCE_RECOVERED_AT_MEMBER_HEADING` |

Symbols: 786 classes, 41 interfaces, 2 enums, 253 constructors, 13,499 methods,
3,858 fields. The documentation references 488 Gist files in 106 Gists; the
audit used placeholder examples. Prepare the real cache on a host that can
reach `gist.github.com` before publishing.
