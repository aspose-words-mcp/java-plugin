# Aspose.Words for Java extraction plugin

Documentation and API reference extraction for Aspose.Words for Java, implementing the `adcs.extraction.v1` worker contract. The plugin normalizes Markdown, extracts Java examples and API symbols, produces chunks, and supplies a declarative retrieval profile for the [Aspose Context Engine](https://github.com/aspose-core-mcp/context-engine).

Extraction uses the Python standard library and has no engine or other-plugin runtime dependency. Product identity is `aspose.words`; API identities are Java packages such as ``com.aspose.words.Document.save``.

## Project family

These repositories provide documentation-backed MCP services for Aspose.Words for Java. The shared engine is maintained under **aspose-core-mcp**; the Words/Java components are maintained under **aspose-words-mcp**.

| Repository | Responsibility |
| --- | --- |
| [context-engine](https://github.com/aspose-core-mcp/context-engine) | Shared documentation ingestion, indexing, retrieval, and MCP infrastructure |
| [java-plugin](https://github.com/aspose-words-mcp/java-plugin) **(this repository)** | Aspose.Words for Java documentation/API extraction and retrieval profile |
| [java-server](https://github.com/aspose-words-mcp/java-server) | Deployment helpers that combine pinned engine and plugin versions |

Use the [Words/Java server setup guide](https://github.com/aspose-words-mcp/java-server/blob/main/docs/setup.md) to deploy the engine with this plugin registered, then follow [client setup](https://github.com/aspose-words-mcp/java-server/blob/main/docs/clients.md).

## Quick start

Requires Python 3.12 or newer. From this repository root:

```sh
python3.12 -m venv .venv
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -I worker.py < examples/extract-request.json
```

The example runs offline against inline Markdown and prints one JSON response with a normalized document, chunks, and Java API symbols. See the [worker contract](docs/worker-contract.md) for discovery and extraction requests.

Use a source checkout for deployment: the manifest, retrieval profile, and prepared Gist cache are not included in the Python wheel. An installed package exposes `adcs-words-java-extract` and `python -I -m adcs_words_java.worker`.

## Prepare and ingest content

1. Follow [source preparation](docs/source-preparation.md) to clone the documentation and API repositories and prepare referenced Gist examples.
2. Register the plugin with the engine using the [integration guide](docs/engine-integration.md).
3. Validate extraction, configure runtime stores, and publish indexed content explicitly.

The plugin does not launch an MCP server or publish data on its own. Source configuration is authoritative in `plugin.json`; citations use `docs.aspose.com/words/java` and `reference.aspose.com/words/java`.

## Java specifics

- One API page per type: one type row plus one row per member overload, each with its own anchor (`#save-java.lang.String`), signature, parameters, returns, remarks and section-local examples. Chunks never span two members; declarations are `api_signature` units.
- `csharp`-labelled documentation blocks are relabelled `java` only with clear Java evidence and no C# idiom.
- The retrieval profile prefers `MailMerge.execute`/`executeWithRegions` for mail merge and `Document.save` with `PdfSaveOptions` for Word to PDF, and excludes the 25 `com.aspose.words` types equivalent to the .NET LowCode namespace.

See [extraction notes](docs/extraction-notes.md) for details and handled upstream defects.

## Validation

GitHub Actions runs the offline regression suite and extraction example on Python 3.12 and 3.13. See [CONTRIBUTING.md](CONTRIBUTING.md) for local checks.

The [source audit](docs/source-audit.json) records extraction of 424 documentation pages (755 chunks) and 836 API pages (19,976 chunks, 18,439 symbols) with no errors at the revisions recorded there. Documentation was audited with placeholder Gist examples; prepare the real cache before publishing. It does not establish deployed retrieval quality. Rerun the audit against prepared sources as described in the source preparation guide.

## License and provenance

[MIT License](LICENSE). Derived from the Words/.NET extraction plugin (originally the MIT-licensed ADCS pilot) and maintained independently for the Java corpus. Fixture origins and revisions are documented in [tests/fixtures/README.md](tests/fixtures/README.md).
