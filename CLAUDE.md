# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Evernote to Google Drive migration tool** that converts Evernote `.enex` (export) files into a structured directory hierarchy and optionally uploads them to Google Drive. The tool is designed to be simple, bulletproof, and preserve notebook structure.

## Core Architecture

### Entry Point: `main.py`
- CLI entry point with argument parsing (`-o`/`--output-directory`, `-d`/`--dry-run`)
- Orchestrates the entire extraction and upload workflow
- Uses XML parsing (ElementTree) to parse `.enex` files
- Extracts notes with their text content and embedded resources (images, PDFs, etc.)
- Maintains a JSON extraction log (`extraction_log.json`) to track processed notes

### Google Drive Integration: `gdrive.py`
- Handles OAuth 2.0 authentication flow using `credentials.json`
- Stores authenticated credentials in `token.pickle` for reuse
- Recursively creates folder structures in Google Drive
- Uploads files using Google Drive API v3

### PDF Utilities: `pdf_utils.py`
- Generates unique 6-digit alphanumeric IDs for each note
- Converts text content to PDF using ReportLab
- Converts images (PNG, JPG, etc.) to PDF pages
- Merges multiple PDFs into a single document
- Handles multi-item notes by combining text and resources into one PDF

### Data Flow

1. **Input**: `.enex` files placed in `./input_data/` directory
2. **Processing**:
   - Each `.enex` file represents one Evernote notebook
   - Each note gets a unique 6-digit alphanumeric ID (e.g., `A3B7F2`)
   - Notes are processed based on content:
     - **Multi-item notes** (multiple resources OR text + resource): Merged into single PDF with `-MultiItem` suffix
     - **Single resource notes**: Saved as-is with ID prefix
     - **Text-only notes**: Converted to PDF
   - All files placed directly in notebook directory (flat structure, no nested folders)
3. **Output**: Flat directory structure in specified output directory (default: `./EverNote Notes/`)
   - Format: `{notebook_name}/{note_id}-{note_title}[-MultiItem].{ext}`
4. **Upload** (if not dry-run): Entire output directory is uploaded to Google Drive

## Running the Project

### Setup

**With uv (recommended):**
```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or: brew install uv

# Install dependencies (creates .venv automatically)
uv sync

# Ensure you have credentials.json from Google Cloud Console
# with Google Drive API enabled
```

**With pip (traditional):**
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Mac/Linux
# .venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Ensure you have credentials.json from Google Cloud Console
# with Google Drive API enabled
```

### Development Commands

**With uv:**
```bash
# Run with default output directory (./EverNote Notes/)
uv run python main.py

# Specify custom output directory
uv run python main.py -o ./output

# Dry run (extract files but don't upload to Drive)
uv run python main.py -d

# Preserve original filenames (no serial number prefix)
uv run python main.py --no-serial

# Combine options
uv run python main.py --output-directory ./my-notes --dry-run --no-serial

# Add development dependencies
uv add --dev pytest black ruff mypy

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run ruff check .
```

**With pip/traditional Python:**
```bash
# Activate virtual environment first
source .venv/bin/activate

# Run with default output directory (./EverNote Notes/)
python main.py

# Specify custom output directory
python main.py -o ./output

# Dry run (extract files but don't upload to Drive)
python main.py -d

# Preserve original filenames (no serial number prefix)
python main.py --no-serial

# Combine options
python main.py --output-directory ./my-notes --dry-run --no-serial
```

### Testing Without Upload
Always use `--dry-run` flag when testing extraction logic to avoid uploading test data to Google Drive.

## Important Implementation Details

### File Naming Convention
- Each note gets a unique 6-digit alphanumeric ID (e.g., `A3B7F2`)
- Note titles containing `/` are replaced with `-` to make them filesystem-safe
- File naming patterns:
  - **Multi-item PDF**: `{id}-{title}-MultiItem.pdf`
  - **Single resource**: `{id}-{title}.{ext}` (preserves original extension)
  - **Text-only**: `{id}-{title}.pdf`
- MIME types are used to determine file extensions

### Directory Structure Logic
- **Flat structure**: All files are placed directly in `notebook_name/` directory
- **No nested folders**: Previous nested directory logic has been removed
- Multi-item PDFs combine text and all resources into one file

### Multi-Item PDF Logic
A multi-item PDF is created when:
1. A note has multiple resources (2+), OR
2. A note has both text content AND at least one resource

The PDF contains (supported formats only):
- Text content (converted to formatted PDF pages)
- Images (converted to PDF pages, scaled to fit): PNG, JPG, JPEG, GIF, BMP, TIFF, WebP
- Existing PDFs (merged into the final document)

### Unsupported File Types
The following file types **cannot** be included in multi-item PDFs and are saved separately with the note ID prefix:

**Archive Files**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`
**Video Files**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.flv`, `.wmv`
**Audio Files**: `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a`, `.aac`
**HTML Files**: `.html`, `.htm`, `.mhtml`
**Office Docs**: `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`

When a note contains unsupported file types:
- Supported files (text, images, PDFs) are merged into the `-MultiItem.pdf`
- Unsupported files are saved as: `{id}-{title}-{filename}.{ext}`
- A warning is logged with type `"unsupported-separate-file"`

**TODO: Future enhancements for unsupported types require discussion:**
- Generate thumbnail previews for videos?
- Convert HTML to PDF with proper rendering (using headless browser)?
- Create info pages in PDF listing attached files with icons?
- Extract text content from Office documents?
- Create archive manifests showing ZIP file contents?

### Authentication & Credentials
- OAuth flow runs once and stores credentials in `token.pickle`
- Credentials are automatically refreshed if expired
- First run opens browser for Google account authorization

### Error Handling
- XML parsing errors are logged to `extraction_log.json`
- Missing MIME types or resource data are logged but don't stop processing
- Base64 decoding failures are caught and logged

## Project Dependencies

Key libraries:
- `google-api-python-client`: Google Drive API integration
- `google-auth-oauthlib`: OAuth 2.0 flow
- `reportlab`: PDF creation from text and layout
- `pypdf`: PDF reading and merging
- `Pillow` (PIL): Image processing and conversion
- Standard library: `xml.etree.ElementTree`, `pathlib`, `base64`, `mimetypes`, `random`, `string`

## Development Notes

- The project uses Python 3.9+ with type hints
- Virtual environment is in `.venv/` (excluded from git)
- Extraction logs (`extraction_log.json`) track all processed notes and errors
- Google Drive creates folders recursively, mirroring local structure exactly
- Linting: Ruff (fast Python linter) - `uv run ruff check`
- Formatting: Black (code formatter) - `uv run black .`
- Type checking: MyPy (optional) - `uv run mypy .`
- Test suite: Manual testing (automated tests planned for v1.2.0)
- Commit format: Conventional Commits (enforced by GitHub Actions)

## Documentation Structure

The project uses organized documentation under `docs/`:

- **README.md** - Landing page with quick start and overview
- **docs/usage.md** - Complete step-by-step user guide (former HOWTO.md)
- **docs/reference.md** - CLI flags, file formats, logging schema, conventions
- **docs/dev.md** - Developer setup, code style, testing, debugging
- **docs/release.md** - Release process, versioning, checklist
- **docs/roadmap.md** - Future plans and milestones (former ROADMAP.md)
- **CHANGELOG.md** - Version history (Keep a Changelog format)
- **CLAUDE.md** - This file (AI agent cheat sheet)

### When to Update Documentation

- **README.md:** New features, changed installation process
- **docs/usage.md:** New CLI flags, changed workflow
- **docs/reference.md:** New flags, new log types, new file behaviors
- **docs/dev.md:** Changed development tools, new testing procedures
- **CHANGELOG.md:** Every user-facing change (features, fixes, breaking changes)
- **CLAUDE.md:** Changed architecture, new files, modified data flow

### Documentation Principles

1. **One source of truth:** Don't duplicate information across files
2. **Cross-link:** Reference other docs instead of repeating content
3. **Code examples:** Use fenced code blocks with syntax highlighting
4. **Tables:** Use for structured data (flags, options, comparisons)
5. **Warnings:** Call out risks and edge cases clearly
