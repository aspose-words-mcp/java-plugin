# Worker contract

The worker accepts one JSON request on stdin, prints one JSON response on stdout, and exits. Launch it from a source checkout with `python -I worker.py`.

Required identity fields:

```json
{
  "contract": "adcs.extraction.v1",
  "plugin_id": "aspose.words.java",
  "product_id": "aspose.words",
  "language": "java",
  "source_kind": "apiref",
  "operation": "extract"
}
```

`source_kind` is `docs` or `apiref`. Other products, platforms and layouts are rejected.

## Discovery

For `operation: discover`, supply `repo_root` and `source_prefix`. The prefix must be a relative directory inside the repository. Discovery returns `result.files`, a sorted list of Markdown paths relative to that repository. Missing content or an escaping prefix is an error.

## Extraction

See the runnable [extract request](../examples/extract-request.json) for a complete payload. It supplies source identity, paths, revision, layout detection, canonical URL base, and inline Markdown.

A successful response contains `contract`, `plugin_id`, `plugin_version`, and `result`. The result contains `page`, `normalized_document`, `chunk_records`, and `symbols` (empty for documentation). API pages yield one type row plus one row per member overload, each with its own signature and `payload.section_anchor`.

Errors return an `error` object with `type` and `message`, and exit status 1. A successful response exits with status 0. The worker is not a persistent JSON-lines or HTTP server.
