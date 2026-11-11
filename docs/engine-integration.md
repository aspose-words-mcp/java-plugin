# Context engine integration

Use [plugin-based ingestion](https://github.com/aspose-core-mcp/context-engine/blob/main/docs/engine-only.md) with an engine implementing `adcs.extraction.v1`. Install and configure the engine separately; it owns runtime stores, indexing, publication, and serving.

Serving Words/Java needs an engine whose retrieval profiles accept Java package identities (`com.<product>.`) and which defines the `/words/java/mcp/v1/streamable-http` route.

## Recommended Words/Java deployment

Use [aspose-words-mcp/java-server](https://github.com/aspose-words-mcp/java-server) for a deployment with pinned public engine and plugin revisions. Follow its [setup](https://github.com/aspose-words-mcp/java-server/blob/main/docs/setup.md) and [ingestion guide](https://github.com/aspose-words-mcp/java-server/blob/main/docs/ingestion.md). Its catalog already registers `aspose.words.java`; no change to the shared engine's default catalog is required.

The server helpers use `engine/` as the ingestion workspace and `plugins/words-java/` for the plugin and Gist cache. The standalone instructions below use this plugin checkout as the workspace instead.

## Optional: register with an existing engine

> **Using `aspose-words-mcp/java-server`?** Registration is already configured. Skip these steps.

Create a deployment-specific catalog, preserving any existing registrations:

```json
{
  "plugins": ["/absolute/path/to/java-plugin/plugin.json"],
  "compositions": []
}
```

Source paths are relative to the ingestion workspace, not the catalog file. Prepare the sources and Gist cache using [source preparation](source-preparation.md), then run from the activated engine environment:

```sh
adcs-platform-ingest aspose.words.java \
  --catalog /absolute/path/to/catalog.json \
  --workspace /absolute/path/to/java-plugin \
  --python /absolute/path/to/java-plugin/.venv/bin/python
```

This validates extraction and may write operation metadata. Registration does not clone sources, install dependencies, or publish indexes. After configuring runtime stores and embeddings, add `--publish` to publish content explicitly.

## Retrieval and serving

`plugin.json` names `retrieval-profile.json`. Point both `ADCS_PRODUCT_PLUGIN_CATALOG` and `ADCS_RETRIEVAL_PLUGIN_CATALOG` at the deployment catalog and restart the API to load profile changes. Installing the plugin does not dynamically create HTTP routes.

Extractor or source changes require re-extraction and publication of affected content. Restarting a server alone does not update indexed symbols or excerpts.

## Connect an MCP client

Follow the [Words/Java server client guide](https://github.com/aspose-words-mcp/java-server/blob/main/docs/clients.md) and configure your client with your deployed `/words/java/mcp/v1/streamable-http` endpoint. The server is self-hosted; no hosted endpoint is supplied.
