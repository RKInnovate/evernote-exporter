# Evernote to Google Drive Migrator

A bulletproof tool to migrate your notes from **Evernote** (via `.enex` export files) to **Google Drive**, preserving notebook hierarchy and note content.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## 🚀 Quick Start

### 1. Install uv (Recommended)

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

### 2. Clone and Setup

```bash
git clone https://github.com/RKInnovate/evernote-exporter.git
cd evernote-exporter
uv sync
```

### 3. Get Google Drive Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable **Google Drive API**
3. Create **OAuth 2.0 Client ID** (Desktop App)
4. Download `credentials.json` to project root

### 4. Run Migration

```bash
# Place .enex files in ./input_data/
mkdir -p input_data
cp ~/Downloads/*.enex ./input_data/

# Dry run (test without upload)
uv run python main.py --dry-run

# Upload to Google Drive
uv run python main.py
```

---

## 📋 Features

- ✅ Converts Evernote notes to PDFs (with images, attachments)
- ✅ Preserves notebook structure as Drive folders
- ✅ Handles multiple file types (images, PDFs, documents)
- ✅ Optional filename preservation (`--no-serial`)
- ✅ Automatic collision detection (prevents data loss)
- ✅ Dry-run mode for testing
- ✅ OAuth 2.0 secure authentication

---

## ⚡ Common Usage

```bash
# Basic usage with default options
uv run python main.py

# Custom output directory
uv run python main.py -o ./my-notes

# Dry run (no upload)
uv run python main.py --dry-run

# Preserve original filenames (no ID prefix)
uv run python main.py --no-serial

# Combine options
uv run python main.py -ns -d -o ./test-output

# Show all options
uv run python main.py --help
```

### Command-Line Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--output-directory` | `-o` | Output directory (default: `./EverNote Notes`) |
| `--dry-run` | `-d` | Extract without uploading to Drive |
| `--no-serial` | `-ns` | Preserve original filenames (no 6-digit ID prefix) |
| `--help` | `-h` | Show help message |

**⚠️ Collision Warning:** When using `--no-serial` with duplicate note titles, files are automatically renamed with `_1`, `_2` suffixes to prevent data loss.

---

## 📁 How It Works

1. **Export** notebooks from Evernote as `.enex` files
2. **Place** `.enex` files in `./input_data/` directory
3. **Run** the tool and sign in with Google account
4. **Done** - Notebooks recreated in Google Drive

### Directory Structure

```
input_data/
├── Work Notes.enex          # Each .enex = one notebook
├── Personal.enex
└── Recipes.enex

↓ Converts to ↓

EverNote Notes/              # Output directory
├── Work Notes/
│   ├── A3B9K2-Meeting.pdf
│   └── X7Y1Z4-Report.pdf
├── Personal/
│   └── M2N5P8-Photo-MultiItem.pdf
└── Recipes/
    └── Q8W3E1-Pasta.pdf
```

**File Types:**
- **Text-only notes** → PDF
- **Notes with images** → PDF (images embedded)
- **Multiple attachments** → Combined into single `-MultiItem.pdf`
- **Unsupported files** (videos, ZIPs, etc.) → Saved separately

---

## 📚 Documentation

Complete documentation available in [`docs/`](docs/) directory:

| Document | Description |
|----------|-------------|
| **[Usage Guide](docs/usage.md)** | Step-by-step setup and usage instructions |
| **[CLI Reference](docs/reference.md)** | Complete CLI flag reference, file formats, logging |
| **[Developer Guide](docs/dev.md)** | Contributing, code style, testing, debugging |
| **[Release Process](docs/release.md)** | Versioning policy, release checklist |
| **[Roadmap](docs/roadmap.md)** | Planned features and future development |
| **[Changelog](CHANGELOG.md)** | Version history and release notes |

---

## 🛠️ Traditional Setup (pip)

If you prefer pip over uv:

```bash
# Clone repository
git clone https://github.com/RKInnovate/evernote-exporter.git
cd evernote-exporter

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tool
python main.py --help
```

---

## 🔐 Security & Privacy

- **OAuth 2.0:** No passwords stored - uses Google's secure authentication
- **Local Processing:** All conversion happens on your machine
- **Minimal Permissions:** Only accesses files created by this app in Drive
- **Open Source:** Audit the code yourself

---

## 🐛 Troubleshooting

### Common Issues

**`credentials.json not found`**
```bash
# Download from Google Cloud Console
# Place in project root (not input_data/)
```

**`ModuleNotFoundError`**
```bash
# Reinstall dependencies
uv sync
# Or: pip install -r requirements.txt
```

**Duplicate Filenames (with `--no-serial`)**
```bash
# Automatic: Files renamed to "Title_1.pdf", "Title_2.pdf"
# Check console warnings and extraction_log.json
```

**OAuth Errors**
```bash
# Delete token and re-authenticate
rm token.pickle
uv run python main.py
```

See [Usage Guide](docs/usage.md#troubleshooting) for detailed solutions.

---

## 🤝 Contributing

Contributions welcome! See [Developer Guide](docs/dev.md) for:

- Development setup
- Code style guidelines
- Testing procedures
- PR process

### Quick Contribution Steps

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes and test
4. Commit with [Conventional Commits](https://www.conventionalcommits.org/)
5. Push and create Pull Request

---

## 📊 Project Status

**Current Version:** v1.0.0
**Next Release:** v1.1.0 (Q1 2026) - Production Hardening
**Python Support:** 3.9, 3.10, 3.11, 3.12

See [Roadmap](docs/roadmap.md) for upcoming features.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/RKInnovate/evernote-exporter/issues)
- **Questions:** [Support Question Template](https://github.com/RKInnovate/evernote-exporter/issues/new?template=support_question.yml)
- **Bugs:** [Bug Report Template](https://github.com/RKInnovate/evernote-exporter/issues/new?template=bug_report.yml)
- **Security:** See [Security Policy](https://github.com/RKInnovate/.github/blob/main/SECURITY.md)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙌 Why This Exists

Evernote doesn't provide a clean way to migrate content into Google Drive. This tool is a lightweight bridge — ideal for individuals or teams moving away from Evernote.

**Built with:**
- [ReportLab](https://www.reportlab.com/) - PDF generation
- [Pillow](https://pillow.readthedocs.io/) - Image processing
- [pypdf](https://pypdf.readthedocs.io/) - PDF merging
- [Google Drive API](https://developers.google.com/drive) - Upload automation

---

## ⭐ Star History

If this tool helped you, consider starring the repository!

---

**For Maintainers:** See [CLAUDE.md](CLAUDE.md) for AI agent development cheat sheet.
