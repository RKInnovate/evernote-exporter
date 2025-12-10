# Reference Guide

Complete technical reference for the Evernote to Google Drive migration tool.

---

## CLI Flags

### Command Syntax

```bash
uv run python main.py [OPTIONS]
```

### Options Table

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--output-directory` | `-o` | Path | `./EverNote Notes` | Directory where converted notes are saved (also becomes Drive folder name) |
| `--dry-run` | `-d` | Boolean | `False` | Extract and convert files without uploading to Google Drive |
| `--no-serial` | `-ns` | Boolean | `False` | Preserve original filenames without 6-digit ID prefix |
| `--verbose` | `-v` | Boolean | `False` | Enable verbose logging (DEBUG level) with detailed progress |
| `--quiet` | `-q` | Boolean | `False` | Enable quiet mode (ERROR level only, no warnings or info) |
| `--help` | `-h` | - | - | Show help message and exit |

### Flag Details

#### `--output-directory` / `-o`

Specifies where extracted notes are saved locally and what the root folder will be named in Google Drive.

**Examples:**
```bash
# Default location
uv run python main.py
# Output: ./EverNote Notes/

# Custom location
uv run python main.py -o ./my-notes
# Output: ./my-notes/
```

**Behavior:**
- Directory is created if it doesn't exist
- Existing files are not overwritten (collision detection applies)
- Notebook structure is preserved under this root

#### `--dry-run` / `-d`

Runs the full extraction and conversion process without uploading to Google Drive.

**Use Cases:**
- Testing ENEX parsing before uploading
- Inspecting converted files locally
- Debugging conversion issues
- Previewing output structure

**Examples:**
```bash
# Extract and convert only
uv run python main.py --dry-run

# Combine with custom output
uv run python main.py -d -o ./test-output
```

**Behavior:**
- All files are created locally
- OAuth authentication is skipped
- `extraction_log.json` is still created
- No Drive API calls are made

#### `--no-serial` / `-ns`

Preserves original note filenames without adding the 6-digit alphanumeric ID prefix.

**Default Behavior (with serial):**
```
A3B9K2-Meeting Notes.pdf
X7Y1Z4-Vacation Photo.jpg
M2N5P8-Recipe-MultiItem.pdf
```

**With `--no-serial`:**
```
Meeting Notes.pdf
Vacation Photo.jpg
Recipe-MultiItem.pdf
```

**⚠️ Collision Warning:**

When multiple notes in the same notebook have identical titles, the tool automatically adds `_1`, `_2`, `_3` suffixes to prevent data loss:

```
First note:   Shopping List.pdf
Second note:  Shopping List_1.pdf
Third note:   Shopping List_2.pdf
```

**Collision Behavior:**
- Warning printed to console: `⚠️ WARNING: File collision: 'Shopping List.pdf' already exists, using 'Shopping List_1.pdf'`
- Logged to `extraction_log.json` with type `"filename-collision"`
- No data is lost or silently skipped

**Examples:**
```bash
# Preserve original filenames
uv run python main.py --no-serial

# Short form
uv run python main.py -ns

# With dry-run
uv run python main.py -ns -d
```

**When to Use:**
- You have unique note titles within each notebook
- You prefer readable filenames without IDs
- You're migrating from a system with meaningful filenames

**When NOT to Use:**
- You frequently have duplicate note titles
- You want guaranteed unique filenames
- You need to trace files back to source ENEX by ID

#### `--verbose` / `-v`

Enable detailed logging with DEBUG level output.

**Use Cases:**
- Debugging issues during conversion
- Understanding what the tool is doing
- Seeing detailed progress for each note
- Investigating warnings or errors

**Examples:**
```bash
# Enable verbose logging
uv run python main.py --verbose

# Short form
uv run python main.py -v

# Combine with dry-run
uv run python main.py -v -d
```

**Output Example:**
```
2025-12-10 14:30:45 [INFO] Starting Evernote to Google Drive migration
2025-12-10 14:30:45 [DEBUG] Log level: DEBUG
2025-12-10 14:30:45 [INFO] Processing notes into: ./EverNote Notes
2025-12-10 14:30:45 [INFO] Found 3 ENEX file(s) to process
2025-12-10 14:30:45 [INFO] Processing: Work.enex
2025-12-10 14:30:46 [INFO] ✓ Created multi-item PDF: A3B9K2-Meeting Notes-MultiItem.pdf
2025-12-10 14:30:46 [DEBUG]   → Saved separately: video.mp4
2025-12-10 14:30:46 [WARNING] ⚠️  File collision: 'Recipe.pdf' already exists, using 'Recipe_1.pdf'
```

**When to Use:**
- First time running the tool
- Troubleshooting conversion issues
- Large ENEX files (see progress per note)
- Understanding warnings and errors

#### `--quiet` / `-q`

Suppress all output except errors (ERROR level only).

**Use Cases:**
- Automated scripts or CI/CD pipelines
- Cron jobs
- Batch processing where you only care about failures
- Reducing log noise

**Examples:**
```bash
# Enable quiet mode
uv run python main.py --quiet

# Short form
uv run python main.py -q

# Quiet with dry-run
uv run python main.py -q -d
```

**Output Example:**
```
2025-12-10 14:30:50 [ERROR] ✗ Error creating multi-item PDF for 'Broken Note': XML parse error (notebook: Work, file: Work.enex)
2025-12-10 14:30:51 [ERROR] Failed to decode resource in note 'Bad Resource' (notebook: Personal, file: Personal.enex): Invalid base64
```

**When to Use:**
- Automated workflows
- When you only need to know about failures
- Scripts that parse output
- Reducing terminal clutter

**Note:** The summary report is still printed at INFO level, so it will not appear in quiet mode.

#### Logging Levels

| Mode | Level | Shows |
|------|-------|-------|
| **Default** | INFO | Success messages, progress, warnings, errors |
| **Verbose** (`-v`) | DEBUG | All messages including detailed debug info |
| **Quiet** (`-q`) | ERROR | Only errors and failures |

**Priority:** If both `--verbose` and `--quiet` are specified, `--quiet` takes precedence.

---

## Directory Structure

### Input Layout

```
project-root/
├── input_data/
│   ├── Notebook1.enex
│   ├── Notebook2.enex
│   └── Notebook3.enex
├── credentials.json          # Google OAuth credentials
├── token.pickle              # Cached auth token (auto-generated)
└── main.py
```

**Requirements:**
- All `.enex` files must be placed in `./input_data/`
- Files must have `.enex` extension (case-insensitive)
- `credentials.json` must be in project root

### Output Layout

**With Serial IDs (default):**
```
EverNote Notes/                # Root output directory
├── Notebook1/
│   ├── A3B9K2-Note Title.pdf
│   ├── X7Y1Z4-Photo Note.jpg
│   └── M2N5P8-Multi-Note-MultiItem.pdf
├── Notebook2/
│   ├── Q8W3E1-Meeting.pdf
│   └── R5T6Y7-Report.pdf
└── extraction_log.json        # Processing log
```

**With `--no-serial`:**
```
EverNote Notes/
├── Notebook1/
│   ├── Note Title.pdf
│   ├── Photo Note.jpg
│   ├── Multi-Note-MultiItem.pdf
│   └── Duplicate Title_1.pdf   # Collision handled
├── Notebook2/
│   ├── Meeting.pdf
│   └── Report.pdf
└── extraction_log.json
```

**Flat Structure:**
- All files are placed directly in the notebook directory
- No nested subdirectories for multi-item notes
- `-MultiItem.pdf` suffix indicates merged content

### Google Drive Layout

The Drive structure mirrors the local output directory exactly:

```
Google Drive (root)/
└── EverNote Notes/            # Folder created in Drive
    ├── Notebook1/             # Subfolder for each notebook
    │   ├── A3B9K2-Note Title.pdf
    │   └── X7Y1Z4-Photo Note.jpg
    └── Notebook2/
        └── Q8W3E1-Meeting.pdf
```

---

## Filename Conventions

### Safe Title Transformation

Note titles are made filesystem-safe using these rules:

| Original Character | Replacement | Reason |
|--------------------|-------------|--------|
| `/` | `-` | Slash creates subdirectories |
| `--` | `-` | Avoid double dashes |
| Leading/trailing spaces | Trimmed | Avoid hidden characters |

**Examples:**
```
"Meeting Notes / Jan 2024"  →  "Meeting Notes - Jan 2024"
"Q&A  --  Part 1"          →  "Q&A - Part 1"
"  Spaced Title  "         →  "Spaced Title"
```

### ID Generation

6-digit alphanumeric IDs use characters: `ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`

**Properties:**
- Always 6 characters long
- Random generation (not sequential)
- Collision probability: ~1 in 2 billion
- Used to guarantee unique filenames

**Format Patterns:**

| File Type | With Serial | Without Serial |
|-----------|-------------|----------------|
| Single resource | `{ID} - {Title}.{ext}` | `{Title}.{ext}` |
| Text-only PDF | `{ID}-{Title}.pdf` | `{Title}.pdf` |
| Multi-item PDF | `{ID} - {Title}-MultiItem.pdf` | `{Title}-MultiItem.pdf` |
| Unsupported file | `{ID} - {Title}-{filename}.{ext}` | `{Title}-{filename}.{ext}` |

**Note:** Text-only PDFs use `{ID}-{Title}` (no space) while others use `{ID} - {Title}` (with space). This is intentional for historical compatibility.

---

## File Type Handling

### Supported Types (Merged into PDFs)

These file types can be included in multi-item PDFs:

| Category | Extensions | Conversion Method |
|----------|-----------|-------------------|
| **Text** | (note content) | ReportLab PDF generation |
| **Images** | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp` | Pillow → PDF pages |
| **PDFs** | `.pdf` | pypdf merging |

### Unsupported Types (Saved Separately)

These file types cannot be merged and are saved as individual files:

| Category | Extensions | Saved As |
|----------|-----------|----------|
| **Archives** | `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2` | Original file |
| **Videos** | `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.flv`, `.wmv` | Original file |
| **Audio** | `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a`, `.aac` | Original file |
| **HTML** | `.html`, `.htm`, `.mhtml` | Original file |
| **Office Docs** | `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx` | Original file |

**Behavior When Unsupported Files Are Present:**

1. Supported files (text, images, PDFs) are merged into `-MultiItem.pdf`
2. Unsupported files are saved separately with naming: `{ID} - {Title}-{original_filename}.{ext}`
3. Warning logged: `"type": "unsupported-separate-file"`

---

## Multi-Item PDF Logic

### When Multi-Item PDFs Are Created

A note becomes a multi-item PDF when **either** condition is true:

1. **Multiple resources** (2 or more attachments), OR
2. **Text + at least one resource**

### Decision Table

| Text Content | Number of Resources | Result |
|--------------|---------------------|--------|
| Yes | 0 | Text-only PDF |
| Yes | 1+ | Multi-item PDF |
| No | 0 | Skipped (nothing to export) |
| No | 1 | Single resource file |
| No | 2+ | Multi-item PDF |

### Merging Order

Content is merged in this order:

1. **Text content** (if present) → First pages of PDF
2. **Images** → Converted to PDF pages (scaled to fit letter size)
3. **PDFs** → Merged as-is
4. **Unsupported files** → Saved separately (not in PDF)

---

## Logging Schema

### `extraction_log.json` Format

The log file is created in the output directory root and contains processing results for every note.

#### Structure

```json
{
  "Notebook Name": [
    {
      "file": "Notebook.enex",
      "note": "Note Title",
      "note_id": "A3B9K2",
      "success": true,
      "file_path": "/path/to/EverNote Notes/Notebook/A3B9K2-Note Title.pdf",
      "type": "text-only-pdf"
    }
  ],
  "warnings": [
    {
      "type": "filename-collision",
      "original": "Shopping List.pdf",
      "deduped": "Shopping List_1.pdf",
      "message": "File collision: 'Shopping List.pdf' already exists, using 'Shopping List_1.pdf'"
    }
  ]
}
```

#### Log Entry Fields

| Field | Type | Description |
|-------|------|-------------|
| `file` | String | Source `.enex` filename |
| `note` | String | Safe note title |
| `note_id` | String | 6-digit ID (empty if `--no-serial`) |
| `success` | Boolean | Whether note was processed successfully |
| `file_path` | String | Absolute path to created file |
| `type` | String | Entry type (see below) |

#### Log Entry Types

| Type | Description |
|------|-------------|
| `single-resource` | Note with one attachment, saved as original file type |
| `text-only-pdf` | Note with only text content, converted to PDF |
| `multi-item-pdf` | Note with text + resources or multiple resources, merged into PDF |
| `unsupported-separate-file` | Unsupported file saved separately from multi-item PDF |
| `error` | Processing failed (includes `error` field with details) |

#### Warning Types

| Type | Description |
|------|-------------|
| `filename-collision` | Duplicate filename detected and resolved with `_N` suffix |
| `missing-mime-type` | Resource has no MIME type metadata |
| `decode-error` | Base64 decoding failed for resource |

### Example Log Entries

**Text-only note:**
```json
{
  "file": "Work Notes.enex",
  "note": "Meeting Notes",
  "note_id": "A3B9K2",
  "success": true,
  "file_path": "/path/to/output/Work Notes/A3B9K2-Meeting Notes.pdf",
  "type": "text-only-pdf"
}
```

**Multi-item note:**
```json
{
  "file": "Personal.enex",
  "note": "Vacation Photos",
  "note_id": "X7Y1Z4",
  "success": true,
  "file_path": "/path/to/output/Personal/X7Y1Z4-Vacation Photos-MultiItem.pdf",
  "type": "multi-item-pdf"
}
```

**Unsupported file:**
```json
{
  "file": "Work Notes.enex",
  "note": "Project Files",
  "note_id": "M2N5P8",
  "success": true,
  "file_path": "/path/to/output/Work Notes/M2N5P8-Project Files-data.zip",
  "type": "unsupported-separate-file",
  "message": "Saved separately: data.zip (unsupported format)"
}
```

**Error:**
```json
{
  "file": "Notes.enex",
  "note": "Corrupted Note",
  "note_id": "Q8W3E1",
  "success": false,
  "error": "Failed to decode base64 data",
  "type": "error"
}
```

**Collision warning:**
```json
{
  "type": "filename-collision",
  "original": "Recipe.pdf",
  "deduped": "Recipe_1.pdf",
  "message": "File collision: 'Recipe.pdf' already exists, using 'Recipe_1.pdf'"
}
```

---

## OAuth 2.0 Flow

### Required Files

1. **`credentials.json`** - Download from Google Cloud Console
   - Application type: Desktop App
   - Contains `client_id` and `client_secret`
   - Must be in project root

2. **`token.pickle`** - Auto-generated on first run
   - Stores OAuth access and refresh tokens
   - Reused for subsequent runs
   - Automatically refreshed when expired

### Authentication Flow

```
First Run:
1. Script reads credentials.json
2. Browser opens with Google consent screen
3. User signs in and grants Drive permissions
4. Script receives OAuth token
5. Token saved to token.pickle
6. Upload proceeds

Subsequent Runs:
1. Script reads token.pickle
2. If token expired, automatically refreshes
3. Upload proceeds without browser interaction
```

### Required Scopes

```python
SCOPES = ['https://www.googleapis.com/auth/drive.file']
```

**Permissions:**
- Create folders in Drive
- Upload files to Drive
- Only accesses files created by this app (not your entire Drive)

### Troubleshooting Auth Issues

**Error: `credentials.json not found`**
- Download from Google Cloud Console → APIs & Services → Credentials
- Place in project root directory

**Error: `invalid_grant`**
- Delete `token.pickle`
- Run script again to re-authenticate

**Error: `insufficient_permission`**
- Check that Drive API is enabled in Google Cloud Console
- Verify scopes include `drive.file`

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all notes processed |
| 1 | Error - see console output or log file |

---

## Performance Characteristics

### File Size Limits

| Operation | Limit | Notes |
|-----------|-------|-------|
| ENEX file size | No hard limit | Large files (>1GB) may be slow |
| Single note | No hard limit | Memory usage scales with note size |
| Image resolution | Preserved | Scaled to fit letter-size PDF pages |
| PDF pages | No hard limit | Multi-item PDFs can have many pages |

### Processing Speed

Approximate throughput (varies by hardware and note complexity):

- **Text-only notes:** ~50-100 notes/second
- **Notes with images:** ~10-20 notes/second (conversion overhead)
- **Multi-item PDFs:** ~5-10 notes/second (merging overhead)
- **Upload to Drive:** ~2-5 files/second (network dependent)

### Memory Usage

- **Typical:** 100-200 MB for moderate notebooks
- **Peak:** Scales with largest single note (images held in memory during conversion)
- **Large notebooks:** Consider splitting ENEX files if memory issues occur

---

## Limitations & Known Issues

### Current Limitations

1. **HTML content:** Note content is extracted as plain text; formatting is lost
2. **Tables:** Markdown tables in notes are rendered as plain text
3. **Attachments:** Cannot preview or embed Office docs, videos, archives in PDFs
4. **Links:** External and internal links preserved as text but not clickable in PDFs
5. **Tags:** Evernote tags are not preserved (ENEX metadata not extracted)
6. **Notebooks:** One ENEX file = one notebook (no nested notebook support)

### Workarounds

- **HTML formatting:** Export individual notes as HTML from Evernote before migration
- **Office docs:** Will be saved as separate files; open manually after migration
- **Tags:** Use Evernote's search and export features to group notes by tag before export

---

## API Rate Limits

Google Drive API quotas (default free tier):

- **Queries per day:** 1,000,000,000 (effectively unlimited for personal use)
- **Queries per 100 seconds:** 1,000 (automatically throttled by SDK)
- **Upload bandwidth:** No explicit limit, but timeouts may occur with very large files

**Recommendation:** For extremely large migrations (>10,000 files), consider:
- Running in smaller batches
- Using `--dry-run` first to verify conversion
- Uploading during off-peak hours

---

## Environment Variables

Currently, the tool does not use environment variables. All configuration is via CLI flags.

**Future consideration:** Support for `.env` file to configure:
- Default output directory
- OAuth credentials path
- Logging verbosity

---

## File Encoding

- **ENEX files:** UTF-8 XML
- **Note content:** UTF-8 text
- **Filenames:** UTF-8 (supports international characters)
- **PDFs:** UTF-8 encoded with standard fonts

---

## Additional Resources

- [Usage Guide](usage.md) - Step-by-step instructions
- [Developer Guide](dev.md) - Contributing and development setup
- [Roadmap](roadmap.md) - Planned features
- [Changelog](../CHANGELOG.md) - Version history
- [Main README](../README.md) - Project overview
