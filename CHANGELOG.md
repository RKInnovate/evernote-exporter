# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v1.1.0
- Optional flag to disable serial number prefix on filenames
- Enhanced error handling and warning messages
- Verbose logging mode
- Comprehensive error reports

## [1.0.0] - 2025-12-10

### Added
- Modern package management with `uv` package manager
- `pyproject.toml` with complete project metadata and dependencies
- `__version__.py` for version tracking
- Comprehensive documentation updates (README.md, CLAUDE.md, HOWTO.md)
- Support for both `uv` and traditional `pip` workflows
- ROADMAP.md following industry standards
- CHANGELOG.md for version tracking
- Enhanced `.gitignore` for uv-specific files and build artifacts

### Changed
- **BREAKING**: Minimum Python version changed from 3.8 to 3.9 (required by Pillow 12.0)
- Updated all dependencies to latest versions:
  - google-api-python-client: 2.176.0 → 2.187.0
  - pillow: 11.0.0 → 12.0.0
  - pypdf: 5.1.0 → 6.4.1
  - reportlab: 4.2.5 → 4.4.5
  - And other dependency updates

### Documentation
- Added extensive beginner-friendly comments to all Python files (main.py, gdrive.py, pdf_utils.py)
- Created comprehensive HOWTO.md with Mac setup instructions (546 lines)
- Updated README.md with uv installation and usage instructions
- Updated CLAUDE.md with uv-specific development commands
- All documentation consistently updated to reflect Python 3.9+ requirement

### Tested
- Successfully tested conversion of Medical.Viresh notebooks on Cadile 2
- Verified `uv sync` installs all dependencies correctly
- Confirmed `uv run python main.py --help` works as expected

## [0.9.0] - 2025-12-04

### Added
- Multi-item PDF generation with unique 6-digit alphanumeric note IDs
- Flat directory structure (all files in notebook root)
- Check for credential file existence before running

### Fixed
- Handling of links in note titles and text with attachments
- Skip directory creation for notes with single attachment

## [0.8.0] - 2025-06-XX

### Added
- Initial release of Evernote to Google Drive migrator
- ENEX file parsing using XML ElementTree
- Text to PDF conversion using ReportLab
- Image to PDF conversion using Pillow
- PDF merging using pypdf
- Google Drive API integration with OAuth 2.0
- Dry-run mode for testing without upload
- Extraction logging to JSON file
- Command-line interface with argparse

### Features
- Parse Evernote ENEX export files
- Convert notes to PDFs with embedded resources
- Upload to Google Drive preserving folder structure
- Support for multiple file types (images, PDFs, documents)
- Unique ID generation for each note
- Filesystem-safe filename handling

---

## Version Schema

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for added functionality in a backward compatible manner
- **PATCH** version for backward compatible bug fixes

## Links

- [1.0.0]: https://github.com/RKInnovate/evernote-exporter/releases/tag/v1.0.0
- [Unreleased]: https://github.com/RKInnovate/evernote-exporter/compare/v1.0.0...HEAD
