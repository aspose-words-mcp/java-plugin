# Source preparation

`plugin.json` defines repository URLs, branches, prefixes, and layout metadata. Source paths are relative to the ingestion workspace. Use this checkout as the workspace for the commands below. If deploying [java-server](https://github.com/aspose-words-mcp/java-server), follow its [ingestion guide](https://github.com/aspose-words-mcp/java-server/blob/main/docs/ingestion.md) instead: source repositories go under `engine/`, while the Gist cache stays beside the plugin under `plugins/words-java/sources/`.

```sh
mkdir -p sources
git clone --filter=blob:none --sparse --branch master https://github.com/aspose-words-mcp/docs.git sources/documentation
git -C sources/documentation sparse-checkout set en/java
git clone --filter=blob:none --sparse --branch main https://github.com/aspose-words-mcp/reference.git sources/api-reference
git -C sources/api-reference sparse-checkout set english/java
```

For existing source checkouts, update their remotes before synchronization:

```sh
git -C sources/documentation remote set-url origin https://github.com/aspose-words-mcp/docs.git
git -C sources/api-reference remote set-url origin https://github.com/aspose-words-mcp/reference.git
```

A URL change does not refresh published indexes; synchronize sources and run ingestion/publication to update indexed content.

## Prepare Gist examples

After creating the virtual environment from the README:

```sh
PYTHONPATH=src .venv/bin/python -m adcs_words_java.gist_examples --source-root sources/documentation/en/java --cache sources/gist-examples.json
```

This explicit network step fetches referenced public Gist files and records pinned revisions and checksums. Files missing upstream are recorded as `unavailable` and their pages extract with a `GIST_EXAMPLE_UNAVAILABLE` warning. Existing valid entries remain pinned unless `--refresh` is requested. Extraction is offline and fails explicitly if a required cache entry is missing or invalid. Keep the default cache location. Do not prepare the cache concurrently.

On Windows without `LongPathsEnabled`, keep the checkout in a short directory (for example `C:\src\java-plugin`).

## Validate the full sources

```sh
.venv/bin/python scripts/audit_sources.py --docs-root sources/documentation --api-root sources/api-reference --output reports/source-audit.json
```

The audit checks extraction and records source revisions, counts, warnings, and errors. It does not publish data or test an MCP deployment.

## Reproducibility

Record each checkout's `git rev-parse HEAD` and verify `git status --short` is clean before ingestion. Preserve the Gist cache with ingestion records because source revisions alone do not pin external examples. Source corpora, caches, and generated output are excluded from Git.
