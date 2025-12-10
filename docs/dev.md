# Developer Guide

Guide for contributors and maintainers of the Evernote to Google Drive migration tool.

---

## Development Setup

### Prerequisites

- **Python 3.9+** (required by Pillow 12.0)
- **Git** for version control
- **uv** package manager (recommended) or pip
- **Google Cloud Project** with Drive API enabled (for testing uploads)

### Initial Setup

#### Option 1: Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or: brew install uv

# Clone repository
git clone https://github.com/RKInnovate/evernote-exporter.git
cd evernote-exporter

# Install dependencies (including dev tools)
uv sync

# Verify installation
uv run python main.py --help
```

#### Option 2: Using pip

```bash
# Clone repository
git clone https://github.com/RKInnovate/evernote-exporter.git
cd evernote-exporter

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Mac/Linux
# .venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install .[dev]

# Verify installation
python main.py --help
```

---

## Project Structure

```
evernote-exporter/
├── main.py                    # Entry point and orchestration
├── gdrive.py                  # Google Drive API integration
├── pdf_utils.py               # PDF generation and merging
├── __version__.py             # Version tracking
├── pyproject.toml             # Package metadata and dependencies
├── requirements.txt           # pip-compatible requirements (generated)
├── .python-version            # Python version for uv
├── uv.lock                    # uv lockfile
├── .gitignore                 # Git exclusions
├── .github/                   # GitHub workflows and templates
│   ├── workflows/
│   │   ├── pr_checks.yml      # PR validation
│   │   └── commit_msg_check.yml  # Commit message validation
│   ├── ISSUE_TEMPLATE/        # Bug report, feature request, etc.
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/                      # Documentation
│   ├── usage.md               # User guide
│   ├── reference.md           # CLI reference
│   ├── dev.md                 # This file
│   ├── release.md             # Release process
│   └── roadmap.md             # Future plans
├── README.md                  # Project overview
├── CHANGELOG.md               # Version history
├── CLAUDE.md                  # AI agent cheat sheet
└── input_data/                # Place .enex files here (not in git)
```

---

## Development Workflow

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # Or: bugfix/issue-description
   ```

2. **Make your changes** to `main.py`, `gdrive.py`, or `pdf_utils.py`

3. **Run linters and formatters** (see below)

4. **Test your changes** with sample ENEX files

5. **Commit with conventional commit format** (enforced by hooks)

6. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   # Open PR on GitHub
   ```

### Conventional Commits

All commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Valid Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Code style (formatting, no logic change)
- `refactor` - Code restructuring (no functional change)
- `perf` - Performance improvement
- `test` - Adding or updating tests
- `build` - Build system or dependencies
- `ci` - CI/CD changes
- `chore` - Maintenance tasks
- `revert` - Revert previous commit

**Examples:**
```bash
feat(pdf): add collision detection for --no-serial mode

Automatically appends _1, _2 suffixes when duplicate filenames
are detected to prevent data loss.

Closes #42

---

fix(parser): handle missing MIME types gracefully

Some ENEX resources don't include MIME type metadata.
Now defaults to binary file with generic extension.

---

docs(readme): update installation instructions for uv
```

**Enforcement:**
- GitHub Actions validates commit messages on PRs
- Pre-commit hook validates locally (if configured)

---

## Code Quality Tools

### Linting with Ruff

Ruff is a fast Python linter that checks code style and potential bugs.

```bash
# Check for issues
uv run ruff check

# Auto-fix issues
uv run ruff check --fix

# Auto-fix including unsafe changes
uv run ruff check --fix --unsafe-fixes
```

**Configuration:** See `[tool.ruff]` in `pyproject.toml`

**Rules enabled:**
- `E` - pycodestyle errors
- `W` - pycodestyle warnings
- `F` - pyflakes
- `I` - isort (import sorting)
- `B` - flake8-bugbear
- `C4` - flake8-comprehensions
- `UP` - pyupgrade (modern Python patterns)

### Formatting with Black

Black is an opinionated code formatter that ensures consistent style.

```bash
# Format all files
uv run black .

# Check formatting without changes
uv run black --check .

# Format specific file
uv run black main.py
```

**Configuration:** See `[tool.black]` in `pyproject.toml`
- Line length: 100 characters
- Target: Python 3.9+

### Type Checking with MyPy

MyPy validates type hints to catch type errors before runtime.

```bash
# Type check all files
uv run mypy .

# Type check specific file
uv run mypy main.py
```

**Configuration:** See `[tool.mypy]` in `pyproject.toml`
- Python version: 3.9
- Allows untyped definitions (gradual typing)
- Ignores missing imports (third-party libraries)

### Running All Checks

```bash
# Run all quality checks
uv run ruff check && uv run black --check . && uv run mypy .

# Or with auto-fix
uv run ruff check --fix && uv run black . && uv run mypy .
```

---

## Testing

### Manual Testing

Currently, the project does not have automated tests. Manual testing workflow:

1. **Prepare test data:**
   ```bash
   # Place sample .enex files in input_data/
   cp ~/Downloads/TestNotebook.enex ./input_data/
   ```

2. **Test extraction (dry-run):**
   ```bash
   # Extract without uploading
   uv run python main.py --dry-run -o ./test-output

   # Verify files created correctly
   ls -R ./test-output
   ```

3. **Test specific features:**
   ```bash
   # Test --no-serial flag
   uv run python main.py -ns -d -o ./test-no-serial

   # Test with duplicate titles (verify collision handling)
   # Check console warnings
   # Check extraction_log.json for collision entries
   ```

4. **Test upload (optional):**
   ```bash
   # Upload to Drive (requires credentials.json)
   uv run python main.py -o ./test-upload

   # Check Google Drive for folders and files
   ```

5. **Verify logs:**
   ```bash
   # Check extraction_log.json
   cat ./test-output/extraction_log.json | python -m json.tool
   ```

### Smoke Test Recipe

Quick validation that core functionality works:

```bash
# 1. Lint and format
uv run ruff check --fix && uv run black .

# 2. Dry-run with sample data
uv run python main.py --dry-run -o ./smoke-test

# 3. Verify help works
uv run python main.py --help

# 4. Check version import
uv run python -c "from __version__ import __version__; print(__version__)"

# 5. Verify Google Auth (if credentials.json exists)
# uv run python -c "from gdrive import authenticate_drive; authenticate_drive()"

# 6. Clean up
rm -rf ./smoke-test
```

### Future: Automated Testing

**Planned test suite** (see [roadmap.md](roadmap.md)):

- **Unit tests:** `pytest` for individual functions
  - `test_generate_unique_id()` - ID generation
  - `test_categorize_file_type()` - MIME type classification
  - `test_get_unique_filepath()` - Collision detection
  - `test_safe_title()` - Title sanitization

- **Integration tests:** ENEX parsing with fixtures
  - Sample `.enex` files with known structure
  - Verify extraction produces expected files

- **End-to-end tests:** Full workflow with mocked Drive API
  - Mock Google Drive API responses
  - Verify upload calls made correctly

**Running tests (future):**
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_pdf_utils.py
```

---

## Code Style Guidelines

### General Principles

- **PEP 8:** Follow Python style guide
- **Clarity over cleverness:** Prefer readable code
- **Comments for "why":** Explain intent, not mechanics
- **Type hints:** Use for function signatures (gradual adoption)

### Python Standards

- **Python 3.9+:** Use modern syntax
- **Pathlib:** Use `Path` for file operations (not `os.path`)
- **Context managers:** Use `with` for file operations
- **List comprehensions:** Prefer over `map`/`filter` for clarity
- **f-strings:** Use for string formatting (not `%` or `.format()`)

### Examples

**Good:**
```python
def process_note(note: Path, output_dir: Path) -> bool:
    """Process a single note and return success status."""
    if not note.exists():
        return False

    output_path = output_dir / f"{note.stem}.pdf"
    with open(note, 'r') as f:
        content = f.read()

    return True
```

**Avoid:**
```python
def process_note(note, output_dir):  # No type hints
    if not os.path.exists(note):  # Use Path, not os.path
        return False

    output_path = os.path.join(output_dir, note.split('.')[0] + '.pdf')  # Use Path
    f = open(note, 'r')  # Use context manager
    content = f.read()
    f.close()

    return True
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Functions | `snake_case` | `process_enex_file()` |
| Variables | `snake_case` | `note_id`, `output_dir` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_OUTPUT_DIR` |
| Classes | `PascalCase` | `DriveUploader` |
| Private | Leading `_` | `_internal_helper()` |

### Comments

**Docstrings:** All functions should have docstrings (Google style):

```python
def create_text_pdf(text: str, output_path: Path) -> None:
    """
    Convert text content to a PDF file.

    Args:
        text: The text content to convert
        output_path: Where to save the generated PDF

    Raises:
        IOError: If output path is not writable

    Example:
        create_text_pdf("Hello World", Path("output.pdf"))
    ```
    ...
```

**Inline comments:** Explain "why", not "what":

```python
# Good: Explains intent
# Use empty string for note_id when preserving filenames to skip ID prefix
note_id = "" if preserve_filenames else generate_unique_id()

# Avoid: States the obvious
# Set note_id to empty string or generated ID
note_id = "" if preserve_filenames else generate_unique_id()
```

---

## Mocking Google Drive API

For future automated tests, mock the Drive API to avoid real uploads:

```python
from unittest.mock import MagicMock, patch

def test_upload_directory():
    """Test directory upload without hitting real Drive API."""

    # Mock the Drive service
    mock_service = MagicMock()
    mock_service.files().create().execute.return_value = {'id': 'mock-folder-id'}

    with patch('gdrive.authenticate_drive', return_value=mock_service):
        # Call upload function
        result = upload_directory(mock_service, Path('./test-data'))

        # Verify API calls made
        assert mock_service.files().create.called
        assert result is not None
```

**Benefits:**
- Tests run without `credentials.json`
- No network calls (fast tests)
- Can simulate API errors and edge cases

---

## Debugging

### Enable Verbose Logging

```python
# Add to top of main.py for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**Issue: `FileNotFoundError: credentials.json`**
- Download from Google Cloud Console
- Place in project root (not `input_data/`)

**Issue: `ImportError: No module named 'reportlab'`**
- Run `uv sync` or `pip install -r requirements.txt`
- Verify virtual environment is activated

**Issue: ENEX parsing fails**
- Check ENEX is valid XML: `xmllint --noout file.enex`
- Verify file encoding is UTF-8
- Check for special characters in note titles

**Issue: PDF generation fails**
- Verify Pillow supports image format: `python -c "from PIL import Image; print(Image.OPEN)"`
- Check disk space for temporary files
- Reduce image resolution if memory issues

### Interactive Debugging

```bash
# Use Python debugger
uv run python -m pdb main.py

# Or add breakpoint in code
import pdb; pdb.set_trace()
```

---

## Performance Optimization

### Current Performance

- **Bottlenecks:** Image conversion, PDF merging, Drive uploads
- **CPU-bound:** PDF generation
- **I/O-bound:** ENEX parsing, Drive uploads

### Optimization Ideas (Future)

1. **Parallel processing:**
   ```python
   from multiprocessing import Pool

   with Pool() as pool:
       pool.map(process_note, notes)
   ```

2. **Streaming ENEX parsing:**
   - Use `xml.etree.ElementTree.iterparse()` instead of loading full tree
   - Process notes one at a time (reduce memory)

3. **Batch Drive uploads:**
   - Use Drive API batch requests
   - Upload multiple files in one HTTP request

4. **Image optimization:**
   - Compress images before embedding in PDF
   - Reduce resolution for very large images

---

## Release Process

See [release.md](release.md) for detailed release procedures.

**Quick overview:**

1. Update version in `pyproject.toml` and `__version__.py`
2. Update `CHANGELOG.md`
3. Create PR for release
4. Merge to `main`
5. Tag release: `git tag v1.x.x`
6. Push tag: `git push origin v1.x.x`
7. Create GitHub Release with notes

---

## Contributing Guidelines

### Before Submitting a PR

- [ ] Code follows style guidelines (Black formatted)
- [ ] Code passes linting (Ruff clean)
- [ ] Manual testing completed with sample data
- [ ] Commit messages follow Conventional Commits
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (if user-facing change)

### PR Description Template

Use the provided `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
How did you test these changes?

## Checklist
- [ ] Code formatted with Black
- [ ] Linting passes
- [ ] Documentation updated
```

---

## Issue Tracking

### Creating Issues

Use GitHub issue templates:

- **Bug Report:** `.github/ISSUE_TEMPLATE/bug_report.yml`
- **Feature Request:** `.github/ISSUE_TEMPLATE/feature_request.yml`
- **Security Report:** `.github/ISSUE_TEMPLATE/security_report.yml`
- **Support Question:** `.github/ISSUE_TEMPLATE/support_question.yml`

### Labels

| Label | Usage |
|-------|-------|
| `bug` | Something isn't working |
| `enhancement` | New feature or improvement |
| `documentation` | Docs updates |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention needed |

### Milestones

- **v1.1.0 - Production Hardening** (Current)
- **v1.2.0 - Advanced Features**
- **v2.0.0 - Multi-Platform Support**

---

## Resources

- [Python Style Guide (PEP 8)](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Google Drive API Docs](https://developers.google.com/drive/api/guides/about-sdk)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [pypdf Documentation](https://pypdf.readthedocs.io/)

---

## Getting Help

- **Questions:** Open a [Support Question issue](https://github.com/RKInnovate/evernote-exporter/issues/new?template=support_question.yml)
- **Bugs:** Open a [Bug Report](https://github.com/RKInnovate/evernote-exporter/issues/new?template=bug_report.yml)
- **Discussions:** Check existing [GitHub Issues](https://github.com/RKInnovate/evernote-exporter/issues)
- **Security:** See [Security Policy](https://github.com/RKInnovate/.github/blob/main/SECURITY.md)

---

## License

This project is licensed under the MIT License. See root directory for LICENSE file.
