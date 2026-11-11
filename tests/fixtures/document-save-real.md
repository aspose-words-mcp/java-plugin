---
title: Document
linktitle: Document
second_title: Aspose.Words for Java
description: Represents a Word document in Java.
type: docs
weight: 162
url: /java/com.aspose.words/document/
---

**Inheritance:**
java.lang.Object, [com.aspose.words.Node](../../com.aspose.words/node/), [com.aspose.words.CompositeNode](../../com.aspose.words/compositenode/), [com.aspose.words.DocumentBase](../../com.aspose.words/documentbase/)
```
public class Document extends DocumentBase
```

Represents a Word document.

## Methods

| Method | Description |
| --- | --- |
| [save(OutputStream stream, SaveOptions saveOptions)](#save-java.io.OutputStream-com.aspose.words.SaveOptions) |  |
| [save(OutputStream stream, int saveFormat)](#save-java.io.OutputStream-int) |  |
| [save(String fileName)](#save-java.lang.String) | Saves the document. |
| [save(String fileName, SaveOptions saveOptions)](#save-java.lang.String-com.aspose.words.SaveOptions) | Saves the document to a file using the specified save options. |
| [save(String fileName, int saveFormat)](#save-java.lang.String-int) |  |
### save(OutputStream stream, SaveOptions saveOptions) {#save-java.io.OutputStream-com.aspose.words.SaveOptions}
```
public SaveOutputParameters save(OutputStream stream, SaveOptions saveOptions)
```




**Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| stream | java.io.OutputStream |  |
| saveOptions | [SaveOptions](../../com.aspose.words/saveoptions/) |  |

**Returns:**
[SaveOutputParameters](../../com.aspose.words/saveoutputparameters/)
### save(OutputStream stream, int saveFormat) {#save-java.io.OutputStream-int}
```
public SaveOutputParameters save(OutputStream stream, int saveFormat)
```




**Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| stream | java.io.OutputStream |  |
| saveFormat | int |  |

**Returns:**
[SaveOutputParameters](../../com.aspose.words/saveoutputparameters/)
### save(String fileName) {#save-java.lang.String}
```
public SaveOutputParameters save(String fileName)
```


Saves the document.  Saves the document to a file. Automatically determines the save format from the extension.

 **Examples:** 

Shows how to open a document and convert it to .PDF.

```

 Document doc = new Document(getMyDir() + "Document.docx");

 doc.save(getArtifactsDir() + "Document.ConvertToPdf.pdf");
 
```

**Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| fileName | java.lang.String | The name for the document. If a document with the specified file name already exists, the existing document is overwritten. |

**Returns:**
[SaveOutputParameters](../../com.aspose.words/saveoutputparameters/) - Additional information that you can optionally use.
### save(String fileName, SaveOptions saveOptions) {#save-java.lang.String-com.aspose.words.SaveOptions}
```
public SaveOutputParameters save(String fileName, SaveOptions saveOptions)
```


Saves the document to a file using the specified save options.

 **Examples:** 

Shows how to improve the quality of a rendered document with SaveOptions.

```

 Document doc = new Document(getMyDir() + "Rendering.docx");
 DocumentBuilder builder = new DocumentBuilder(doc);

 builder.getFont().setSize(60.0);
 builder.writeln("Some text.");

 SaveOptions options = new ImageSaveOptions(SaveFormat.JPEG);
 doc.save(getArtifactsDir() + "Document.ImageSaveOptions.Default.jpg", options);

 options.setUseAntiAliasing(true);
 options.setUseHighQualityRendering(true);

 doc.save(getArtifactsDir() + "Document.ImageSaveOptions.HighQuality.jpg", options);
 
```

Shows how to render one page from a document to a JPEG image.

```

 Document doc = new Document();
 DocumentBuilder builder = new DocumentBuilder(doc);

 builder.writeln("Page 1.");
 builder.insertBreak(BreakType.PAGE_BREAK);
 builder.writeln("Page 2.");
 builder.insertImage(getImageDir() + "Logo.jpg");
 builder.insertBreak(BreakType.PAGE_BREAK);
 builder.writeln("Page 3.");

 // Create an "ImageSaveOptions" object which we can pass to the document's "Save" method
 // to modify the way in which that method renders the document into an image.
 ImageSaveOptions options = new ImageSaveOptions(SaveFormat.JPEG);
 // Set the "PageSet" to "1" to select the second page via
 // the zero-based index to start rendering the document from.
 options.setPageSet(new PageSet(1));

 // When we save the document to the JPEG format, Aspose.Words only renders one page.
 // This image will contain one page starting from page two,
 // which will just be the second page of the original document.
 doc.save(getArtifactsDir() + "ImageSaveOptions.OnePage.jpg", options);
 
```

Shows how to render every page of a document to a separate TIFF image.

```

 Document doc = new Document();
 DocumentBuilder builder = new DocumentBuilder(doc);

 builder.writeln("Page 1.");
 builder.insertBreak(BreakType.PAGE_BREAK);
 builder.writeln("Page 2.");
 builder.insertImage(getImageDir() + "Logo.jpg");
 builder.insertBreak(BreakType.PAGE_BREAK);
 builder.writeln("Page 3.");

 // Create an "ImageSaveOptions" object which we can pass to the document's "Save" method
 // to modify the way in which that method renders the document into an image.
 ImageSaveOptions options = new ImageSaveOptions(SaveFormat.TIFF);

 for (int i = 0; i < doc.getPageCount(); i++) {
     // Set the "PageSet" property to the number of the first page from
     // which to start rendering the document from.
     options.setPageSet(new PageSet(i));
     // Export page at 2325x5325 pixels and 600 dpi.
     options.setResolution(600f);
     options.setImageSize(new Dimension(2325, 5325));

     doc.save(getArtifactsDir() + MessageFormat.format("ImageSaveOptions.PageByPage.{0}.tiff", i + 1), options);
 }
 
```

Shows how to configure compression while saving a document as a JPEG.

```

 Document doc = new Document();
 DocumentBuilder builder = new DocumentBuilder(doc);
 builder.insertImage(getImageDir() + "Logo.jpg");

 // Create an "ImageSaveOptions" object which we can pass to the document's "Save" method
 // to modify the way in which that method renders the document into an image.
 ImageSaveOptions imageOptions = new ImageSaveOptions(SaveFormat.JPEG);

 // Set the "JpegQuality" property to "10" to use stronger compression when rendering the document.
 // This will reduce the file size of the document, but the image will display more prominent compression artifacts.
 imageOptions.setJpegQuality(10);

 doc.save(getArtifactsDir() + "ImageSaveOptions.JpegQuality.HighCompression.jpg", imageOptions);

 Assert.assertTrue(new File(getArtifactsDir() + "ImageSaveOptions.JpegQuality.HighCompression.jpg").length() <= 20000);

 // Set the "JpegQuality" property to "100" to use weaker compression when rending the document.
 // This will improve the quality of the image at the cost of an increased file size.
 imageOptions.setJpegQuality(100);

 doc.save(getArtifactsDir() + "ImageSaveOptions.JpegQuality.HighQuality.jpg", imageOptions);

 Assert.assertTrue(new File(getArtifactsDir() + "ImageSaveOptions.JpegQuality.HighQuality.jpg").length() < 60000);
 
```

Shows how to convert a whole document to PDF with three levels in the document outline.

```

 Document doc = new Document();
 DocumentBuilder builder = new DocumentBuilder(doc);

 // Insert headings of levels 1 to 5.
 builder.getParagraphFormat().setStyleIdentifier(StyleIdentifier.HEADING_1);

 Assert.assertTrue(builder.getParagraphFormat().isHeading());

 builder.writeln("Heading 1");

 builder.getParagraphFormat().setStyleIdentifier(StyleIdentifier.HEADING_2);

 builder.writeln("Heading 1.1");
 builder.writeln("Heading 1.2");

 builder.getParagraphFormat().setStyleIdentifier(StyleIdentifier.HEADING_3);

 builder.writeln("Heading 1.2.1");
 builder.writeln("Heading 1.2.2");

 builder.getParagraphFormat().setStyleIdentifier(StyleIdentifier.HEADING_4);

 builder.writeln("Heading 1.2.2.1");
 builder.writeln("Heading 1.2.2.2");

 builder.getParagraphFormat().setStyleIdentifier(StyleIdentifier.HEADING_5);

 builder.writeln("Heading 1.2.2.2.1");
 builder.writeln("Heading 1.2.2.2.2");

 // Create a "PdfSaveOptions" object that we can pass to the document's "Save" method
 // to modify how that method converts the document to .PDF.
 PdfSaveOptions options = new PdfSaveOptions();

 // The output PDF document will contain an outline, which is a table of contents that lists headings in the document body.
 // Clicking on an entry in this outline will take us to the location of its respective heading.
 // Set the "HeadingsOutlineLevels" property to "4" to exclude all headings whose levels are above 4 from the outline.
 options.getOutlineOptions().setHeadingsOutlineLevels(4);

 // If an outline entry has subsequent entries of a higher level inbetween itself and the next entry of the same or lower level,
 // an arrow will appear to the left of the entry. This entry is the "owner" of several such "sub-entries".
 // In our document, the outline entries from the 5th heading level are sub-entries of the second 4th level outline entry,
 // the 4th and 5th heading level entries are sub-entries of the second 3rd level entry, and so on.
 // In the outline, we can click on the arrow of the "owner" entry to collapse/expand all its sub-entries.
 // Set the "ExpandedOutlineLevels" property to "2" to automatically expand all heading level 2 and lower outline entries
 // and collapse all level and 3 and higher entries when we open the document.
 options.getOutlineOptions().setExpandedOutlineLevels(2);

 doc.save(getArtifactsDir() + "PdfSaveOptions.ExpandedOutlineLevels.pdf", options);
 
```

**Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| fileName | java.lang.String | The name for the document. If a document with the specified file name already exists, the existing document is overwritten. |
| saveOptions | [SaveOptions](../../com.aspose.words/saveoptions/) | Specifies the options that control how the document is saved. Can be  null . |

**Returns:**
[SaveOutputParameters](../../com.aspose.words/saveoutputparameters/) - Additional information that you can optionally use.
### save(String fileName, int saveFormat) {#save-java.lang.String-int}
```
public SaveOutputParameters save(String fileName, int saveFormat)
```




**Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| fileName | java.lang.String |  |
| saveFormat | int |  |

**Returns:**
[SaveOutputParameters](../../com.aspose.words/saveoutputparameters/)
