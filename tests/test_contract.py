"""Run with stdlib unittest; no engine installation needed."""

import json
import unittest

from helpers import FIXTURES, MANIFEST, extract_api, request, run_worker

BASE = "https://reference.aspose.com/words/java/com.aspose.words"


def by_fqn(symbols, fqn):
    return [s for s in symbols if s["member_fqn"] == fqn]


class JavaTypePageTest(unittest.TestCase):
    def test_type_row_uses_java_identity_and_declaration(self):
        output = extract_api("watermark-real.md", "watermark")
        document = output["normalized_document"]["document"]
        self.assertEqual(document["symbol_fqn"], "com.aspose.words.Watermark")
        self.assertEqual(document["symbol_kind"], "class")
        self.assertEqual(document["canonical_url"], BASE + "/watermark/")
        (type_row,) = by_fqn(output["symbols"], "com.aspose.words.Watermark")
        self.assertEqual(type_row["kind"], "class")
        self.assertEqual(type_row["parent_fqn"], "com.aspose.words")
        self.assertEqual(type_row["signature"], "public class Watermark")
        self.assertEqual(type_row["payload"]["section_anchor"], "#")
        self.assertEqual(type_row["language"], "java")

    def test_member_overloads_keep_anchor_signature_and_parent(self):
        output = extract_api("watermark-real.md", "watermark")
        rows = by_fqn(output["symbols"], "com.aspose.words.Watermark.setText")
        self.assertEqual(
            sorted(r["signature"] for r in rows),
            [
                "public void setText(String text)",
                "public void setText(String text, TextWatermarkOptions options)",
            ],
        )
        anchors = {r["payload"]["section_anchor"] for r in rows}
        self.assertEqual(
            anchors,
            {"#setText-java.lang.String",
             "#setText-java.lang.String-com.aspose.words.TextWatermarkOptions"},
        )
        for row in rows:
            self.assertEqual(row["kind"], "method")
            self.assertEqual(row["name"], "setText")
            self.assertEqual(row["parent_fqn"], "com.aspose.words.Watermark")
            self.assertEqual(row["canonical_url"], BASE + "/watermark/")
            self.assertIn("Parameter", row["payload"]["parameters"])

    def test_document_save_overloads_examples_and_facets(self):
        output = extract_api("document-save-real.md", "document")
        rows = by_fqn(output["symbols"], "com.aspose.words.Document.save")
        self.assertEqual(len(rows), 5)
        self.assertEqual(len({r["signature"] for r in rows}), 5)
        one = next(r for r in rows if r["signature"].endswith("save(String fileName)"))
        self.assertEqual(one["signature"], "public SaveOutputParameters save(String fileName)")
        self.assertEqual(one["payload"]["section_anchor"], "#save-java.lang.String")
        self.assertEqual(one["summary"], "Saves the document.")
        self.assertIn("SaveOutputParameters", one["payload"]["returns"])
        self.assertNotIn("](", one["payload"]["returns"])  # link markup reduced to text
        (example,) = one["payload"]["examples"]
        self.assertIn('doc.save(getArtifactsDir() + "Document.ConvertToPdf.pdf");', example)
        self.assertEqual(one["payload"]["example_snippets"][0]["language"], "java")
        for row in rows:
            for code in row["payload"]["examples"]:
                self.assertNotIn("public SaveOutputParameters", code)  # never the declaration
                self.assertNotIn("**Parameters:**", code)

    def test_fields_and_interfaces(self):
        fields = extract_api("saveformat-real.md", "saveformat")["symbols"]
        (docx,) = by_fqn(fields, "com.aspose.words.SaveFormat.DOCX")
        self.assertEqual(docx["kind"], "field")
        self.assertEqual(docx["signature"], "public static int DOCX")
        self.assertEqual(docx["payload"]["section_anchor"], "#DOCX")
        self.assertTrue(docx["summary"].startswith("Saves the document as an Office Open XML"))
        callback = extract_api("iwarningcallback-real.md", "iwarningcallback")
        self.assertEqual(
            callback["normalized_document"]["document"]["symbol_kind"], "interface"
        )
        (warning,) = by_fqn(callback["symbols"], "com.aspose.words.IWarningCallback.warning")
        self.assertEqual(warning["signature"], "public abstract void warning(WarningInfo info)")
        self.assertTrue(warning["payload"]["examples"])

    def test_broken_upstream_fence_is_recovered_at_member_heading(self):
        output = extract_api("htmlversion-real.md", "htmlversion")
        codes = {w["code"] for w in output["normalized_document"]["warnings"]}
        self.assertIn("CODE_FENCE_RECOVERED_AT_MEMBER_HEADING", codes)
        names = {s["name"] for s in output["symbols"] if s["kind"] == "field"}
        self.assertEqual(names, {"HTML_5", "XHTML", "length"})
        methods = {s["name"] for s in output["symbols"] if s["kind"] == "method"}
        self.assertEqual(methods, {"fromName", "getName", "getValues", "toString"})
        for row in output["symbols"]:
            self.assertTrue(row["signature"].startswith("public "))


class JavaChunkTest(unittest.TestCase):
    def test_chunks_cite_their_member_and_never_span_two(self):
        output = extract_api("document-save-real.md", "document")
        chunks = output["chunk_records"]
        anchors = [c["section_anchor"] for c in chunks]
        self.assertIn("#save-java.lang.String", anchors)
        self.assertEqual(anchors[0], "#")
        for chunk in chunks:
            self.assertEqual(chunk["symbol_fqn"], "com.aspose.words.Document")
            self.assertLessEqual(len(chunk["section_path"]), 3)
            if chunk["section_anchor"] != "#":
                label = chunk["section_path"][1]
                self.assertTrue(label.startswith("save("), label)
                # One member per chunk: no other overload heading inside it.
                headings = [line for line in chunk["text"].splitlines()
                            if line.startswith("save(") and "{#" not in line]
                self.assertLessEqual(len(headings), 1, chunk["text"][:200])

    def test_declarations_are_signatures_not_executable_snippets(self):
        output = extract_api("document-save-real.md", "document")
        snippets = [s for c in output["chunk_records"] for s in c["executable_snippets"]]
        self.assertTrue(snippets)
        for snippet in snippets:
            self.assertFalse(snippet["code"].startswith("public "), snippet["code"])
            self.assertEqual(snippet["language"], "java")
        self.assertTrue(
            any(c["chunk_type"] == "api_signature" for c in output["chunk_records"])
        )
        # Member summary tables are not parameter facets.
        for chunk in output["chunk_records"]:
            if chunk["chunk_type"] == "api_parameters":
                self.assertIn("| Parameter |", chunk["text"])
        self.assertTrue(any("| Method | Description |" in c["text"]
                            for c in output["chunk_records"]))


class ScopeAndUrlTest(unittest.TestCase):
    def test_package_and_root_pages_are_namespaces_without_symbols(self):
        for relative, raw in (
            ("english/java/_index.md", "---\ntitle: Aspose.Words for Java\nurl: /java/\n---\n"
             "## Packages\n| Package | Description |\n| --- | --- |\n"),
            ("english/java/com.aspose.words/_index.md",
             "---\ntitle: com.aspose.words\nurl: /java/com.aspose.words/\n---\n## Classes\n"),
        ):
            with self.subTest(relative=relative):
                result = run_worker(request("apiref", raw, relative))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                output = json.loads(result.stdout)["result"]
                document = output["normalized_document"]["document"]
                self.assertEqual(document["doc_type"], "api_reference_namespace")
                self.assertEqual(output["symbols"], [])

    def test_mixed_case_package_directory_is_preserved(self):
        raw = ("---\ntitle: DataTable\nurl: /java/com.aspose.words.net.system.data/datatable/\n"
               "---\n```\n"
               "public class DataTable implements System.Data.DataTableEventListener\n```\n"
               "\nRepresents one table of in-memory data.\n")
        relative = "english/java/com.aspose.words.net.System.Data/datatable/_index.md"
        result = run_worker(request("apiref", raw, relative))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = json.loads(result.stdout)["result"]
        self.assertEqual(
            output["symbols"][0]["member_fqn"], "com.aspose.words.net.System.Data.DataTable"
        )
        self.assertEqual(
            output["normalized_document"]["document"]["canonical_url"],
            "https://reference.aspose.com/words/java/com.aspose.words.net.system.data/datatable/",
        )

    def test_other_platforms_and_products_are_rejected(self):
        relative = "english/java/com.aspose.words/watermark/_index.md"
        raw = (FIXTURES / "watermark-real.md").read_text(encoding="utf-8")
        for override in ({"language": "net"}, {"product_id": "aspose.cells"},
                         {"plugin_id": "aspose.words.net"}):
            with self.subTest(override=override):
                result = run_worker(request("apiref", raw, relative, **override))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("error", json.loads(result.stdout))
        net_layout = "english/net/aspose.words/watermark/_index.md"
        result = run_worker(request("apiref", raw, net_layout))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("did not identify Java content", result.stdout)

    def test_canonical_urls(self):
        for kind in ("docs", "apiref"):
            source = MANIFEST["sources"][kind]
            base = source["canonical_base_url"]
            origin = base.removesuffix("/words/java")
            cases = [
                ("_index.md", None, base + "/"),
                ("_index.md", "/java/", base + "/"),
                ("_index.md", "/java", base + "/"),
                ("guide/_index.md", "/java/guide/", base + "/guide/"),
                ("guide/_index.md", "/java/guide/?view=x#example", base + "/guide/?view=x#example"),
                ("guide/_index.md", "/javascript/guide/", origin + "/javascript/guide/"),
                ("guide/details.md", None, base + "/guide/details/"),
                ("guide/_index.md", "/words/java/guide/", base + "/guide/"),
                ("guide/_index.md", "guide/#example", base + "/guide/#example"),
                ("guide/_index.md", "https://example.com/x/", "https://example.com/x/"),
                ("guide/_index.md", "//example.com/guide/", None),
                ("guide/_index.md", "javascript:alert(1)", None),
            ]
            for path, override, expected in cases:
                with self.subTest(kind=kind, path=path, override=override):
                    relative = source["prefix"] + "/" + path
                    frontmatter = "title: Guide\n"
                    if override is not None:
                        frontmatter += "url: " + json.dumps(override) + "\n"
                    raw = "---\n" + frontmatter + "---\n# Guide\nUseful content.\n"
                    result = run_worker(request(kind, raw, relative))
                    if expected is None:
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("Canonical URL overrides", result.stdout)
                        continue
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    response = json.loads(result.stdout)["result"]
                    self.assertEqual(
                        response["normalized_document"]["document"]["canonical_url"], expected
                    )
                    for chunk in response["chunk_records"]:
                        self.assertEqual(chunk["canonical_url"], expected)

    def test_minimal_docs_fixture_used_by_deployment_check(self):
        raw = (FIXTURES / "docs.md").read_text(encoding="utf-8")
        result = run_worker(request("docs", raw, MANIFEST["sources"]["docs"]["prefix"] + "/_index.md"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = json.loads(result.stdout)["result"]
        self.assertEqual(
            output["normalized_document"]["document"]["canonical_url"],
            "https://docs.aspose.com/words/java/guide/",
        )
        self.assertEqual([b["language"] for b in output["page"]["code_blocks"]], ["java"])
        self.assertTrue(output["chunk_records"])


if __name__ == "__main__":
    unittest.main()
