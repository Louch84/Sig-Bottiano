# Format Options Reference

## Image Conversion

### Supported Formats
- PNG (lossless)
- JPEG (lossy, adjustable quality)
- WEBP (modern, efficient)
- GIF (animated supported)

### Options
- `--quality`: 1-100 (JPEG/WEBP)
- `--resize WxH`: Resize to dimensions

## PDF Conversion

### Text Extraction
- Extracts all text content
- Preserves page order
- Optional page range selection

### Page Selection
- `--pages 1,3,5` - Specific pages
- `--pages 1-10` - Range
- `--pages 1-5,10` - Mixed

## Data Formats

### CSV
- Auto-detects delimiter
- Optional header specification
- UTF-8 encoding

### JSON
- Pretty-printed output
- Preserves data types

## Document Formats

### DOCX
- Basic text extraction
- Heading style support
- Simple table support
