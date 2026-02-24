---
name: file-conversion
description: Convert files between formats including PDF↔text, images (PNG↔JPG↔WebP), DOCX↔text, CSV↔JSON, and Markdown↔HTML. Use when the user needs to transform file formats or extract/convert content.
---

# File Conversion

Transform files between different formats.

## Quick Start

PDF to text:
```bash
python3 scripts/pdf_to_text.py --input document.pdf --output document.txt
```

Image conversion:
```bash
python3 scripts/convert_image.py --input photo.png --output photo.jpg --quality 90
```

CSV to JSON:
```bash
python3 scripts/csv_to_json.py --input data.csv --output data.json
```

## Scripts

- `scripts/pdf_to_text.py` - Extract text from PDF
- `scripts/text_to_pdf.py` - Create PDF from text
- `scripts/convert_image.py` - Convert between image formats
- `scripts/docx_to_text.py` - Extract text from DOCX
- `scripts/text_to_docx.py` - Create DOCX from text
- `scripts/csv_to_json.py` - CSV to JSON conversion
- `scripts/json_to_csv.py` - JSON to CSV conversion
- `scripts/md_to_html.py` - Markdown to HTML
- `scripts/html_to_md.py` - HTML to Markdown

## Supported Formats

### Documents
- PDF ↔ Text (via pdfplumber/pypdf)
- DOCX ↔ Text (via python-docx)
- Markdown ↔ HTML (via markdown/markdownify)

### Images
- PNG ↔ JPG ↔ WebP ↔ GIF (via Pillow)
- Resize, rotate, quality adjustment

### Data
- CSV ↔ JSON (pandas/nativ)
- JSONL support

## Usage Examples

### PDF with page range
```bash
python3 scripts/pdf_to_text.py --input doc.pdf --output pages.txt --pages 1-5,10
```

### Batch image conversion
```bash
python3 scripts/convert_image.py --input "*.png" --output ./converted/ --format jpg --quality 85
```

### CSV with options
```bash
python3 scripts/csv_to_json.py --input data.csv --output data.json --delimiter ";" --headers id,name,value
```

### DOCX with formatting
```bash
python3 scripts/text_to_docx.py --input report.md --output report.docx --style headings
```

## References

See [references/format_options.md](references/format_options.md) for detailed format-specific options.
