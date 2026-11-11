# Real-source regression fixtures

API Reference fixtures come from `aspose-words/Aspose.Words-API-References`
`main` at `8db4485b53d2f6ef08894a005d251db4bd1bebc9`, under
`english/java/com.aspose.words/`:

- `watermark-real.md`: whole `watermark/_index.md` page (type, constructor-less
  class with overloaded `setText` and other methods).
- `saveformat-real.md`: whole `saveformat/_index.md` page (`public static int` fields).
- `iwarningcallback-real.md`: whole `iwarningcallback/_index.md` page (interface).
- `htmlversion-real.md`: whole `htmlversion/_index.md` page. Its upstream example
  lost HTML during generation and leaves an unbalanced fence; the parser must
  recover at the next member heading.
- `document-save-real.md`: excerpt of `document/_index.md` with the front matter,
  type declaration, the `save` rows of the member table and all five `save`
  overload sections. The full page is ~390 KB and contains non-UTF-8 bytes.

`hello-world-docs-real.md` is `en/java/developer-guide/linq-reporting-engine/
introduction-to-linq-reporting-engine/hello-world-example/_index.md` from
`sabir-aspose/words-docs-com` branch `master` at
`7c88ea9416d62d910b93a08cd9cc5722dafc872b`, including its two Gist shortcodes.
The page is byte-identical in `aspose-words-mcp/aspose-words-docs` `master` at
`e469743995bcf03f2f9011e86bb4e6c31adb8304`.

`docs.md` is a minimal synthetic documentation page without Gist shortcodes. The
deployment repository's registration check extracts it through the real worker.

These revisions are also in the current source repositories
`aspose-words-mcp/reference` and `aspose-words-mcp/docs`.
