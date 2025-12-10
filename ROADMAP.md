# Evernote Exporter Roadmap

This document outlines the strategic direction and planned features for the Evernote Exporter project.

## Project Vision

Create a bulletproof, production-ready tool for migrating Evernote notes to Google Drive with zero data loss and maximum flexibility.

---

## Existing Infrastructure ✅

This project already has **excellent development practices** in place:

### GitHub Organization & Automation
- ✅ **Issue Templates**: Bug reports, feature requests, security reports, support questions
- ✅ **PR Templates**: Structured PR format with validation
- ✅ **GitHub Actions**: Automated PR checks and commit message validation
- ✅ **Conventional Commits**: Enforced via workflows
- ✅ **Security Policy**: Integrated with RKInnovate organization

### Development Standards
- ✅ **Semantic Versioning**: MAJOR.MINOR.PATCH format
- ✅ **Modern Tooling**: uv package manager, pyproject.toml
- ✅ **Code Quality**: Black formatter, Ruff linter, MyPy type checking configured
- ✅ **Documentation**: ROADMAP.md, CHANGELOG.md, comprehensive README, HOWTO, CLAUDE.md

---

## Version History

### v1.0.0 - Initial Release ✅ (Completed: December 2025)

**Major Achievement**: Successfully converted to uv package manager with modern Python packaging standards.

**Key Features**:
- Parse ENEX files and extract notes with attachments
- Convert text to PDF with unique 6-digit alphanumeric IDs
- Multi-item PDF generation (merge text + images + PDFs)
- Google Drive upload with folder structure preservation
- Dry-run mode for testing without upload
- Comprehensive documentation (README, HOWTO, CLAUDE.md)

**Successfully Tested**:
- ✅ Converted Medical.Viresh notebooks on Cadile 2 (Viresh)
- ✅ Full workflow validation with real data

---

## v1.1.0 - Production Hardening 🚧 (Target: Q1 2026)

**Theme**: Make the tool bulletproof for production use across multiple Evernote accounts

### High Priority Features

#### 1. Optional Serial Number Prefix (Feature #1)
**Status**: Planned
**Priority**: High
**Description**: Add command-line flag `--preserve-filenames` or `--no-serial` to disable the automatic 6-digit ID prefix on filenames.

**Use Case**: When migrating certain notebooks, users may want to preserve original filenames without the serial number prefix.

**Implementation**:
```bash
# With serial numbers (current default)
uv run python main.py

# Preserve original filenames
uv run python main.py --preserve-filenames
```

#### 2. Enhanced Error Handling & Logging (Feature #2)
**Status**: Planned
**Priority**: High
**Description**: Improve warning and error messages during ENEX conversion.

**Tasks**:
- [ ] Document all warnings from Medical.Viresh ENEX conversion
- [ ] Add detailed error messages with actionable information
- [ ] Implement verbose logging mode (`--verbose` flag)
- [ ] Create error summary report at end of conversion
- [ ] Add progress indicators for large ENEX files
- [ ] Handle edge cases gracefully (malformed XML, missing data, etc.)

#### 3. Robust Error Recovery (Feature #3)
**Status**: Planned
**Priority**: High
**Description**: Ensure the tool handles all edge cases without crashing.

**Tasks**:
- [ ] Add comprehensive error handling for all file types
- [ ] Implement retry logic for transient failures
- [ ] Create detailed test suite for edge cases
- [ ] Add validation checks before conversion starts
- [ ] Generate error reports for problematic notes

### Medium Priority

#### 4. Development Process Formalization (Process #1)
**Status**: Mostly Complete ✅
**Priority**: Medium
**Description**: Establish standardized development workflow.

**Components**:
- [x] ROADMAP.md (this file)
- [x] CHANGELOG.md for version history
- [x] GitHub Issues for feature tracking
- [x] GitHub Milestones for release planning
- [x] Semantic versioning (MAJOR.MINOR.PATCH)
- [x] Issue templates (bug report, feature request, security report, support question)
- [x] PR templates
- [x] GitHub Actions workflows (PR checks, commit message validation)
- [x] Conventional commits enforcement
- [ ] CONTRIBUTING.md guidelines
- [ ] Release notes template

#### 5. Comprehensive Test Suite (Feature #4)
**Status**: Planned
**Priority**: Medium

**Tasks**:
- [ ] Unit tests for PDF utilities
- [ ] Integration tests for ENEX parsing
- [ ] End-to-end tests with sample ENEX files
- [ ] Test coverage reporting
- [ ] CI/CD pipeline setup

---

## v1.2.0 - Advanced Features 📋 (Target: Q2 2026)

### Planned Features

#### 6. Selective Export (Feature #5)
- Filter by date range
- Filter by tags
- Export specific notebooks only

#### 7. Performance Optimization (Feature #6)
- Parallel processing for large ENEX files
- Streaming mode for memory efficiency
- Progress bars and ETA

#### 8. Enhanced PDF Generation (Feature #7)
- Custom PDF templates
- Better text formatting
- Table of contents for multi-item PDFs
- Hyperlink preservation

---

## v2.0.0 - Multi-Platform Support 🌍 (Future)

### Vision: Universal Note Migration Tool

**Potential Features**:
- Support for other note-taking apps (OneNote, Notion, etc.)
- Export to multiple destinations (Dropbox, OneDrive, etc.)
- Cloud-native deployment options
- Web UI for non-technical users
- Batch processing across multiple accounts

---

## Development Workflow

### Issue Labels (GitHub Defaults)
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `duplicate` - This issue already exists
- `invalid` - This doesn't seem right
- `question` - Further information requested
- `wontfix` - This will not be worked on

### Milestones
- **v1.1.0 - Production Hardening** (Q1 2026) - Current
- **v1.2.0 - Advanced Features** (Q2 2026)
- **v2.0.0 - Multi-Platform Support** (Future)

### Commit Format (Enforced by GitHub Actions)
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Valid Types**: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

**Examples**:
- `feat(pdf): add optional serial number flag`
- `fix(parser): handle malformed XML gracefully`
- `docs(readme): update installation instructions`

### Branching Strategy
- `main` - Production-ready code
- `feature/<name>` - New features
- `bugfix/<name>` - Bug fixes
- `release/<version>` - Release preparation

### Release Process
1. Create milestone for version
2. Create issues for features/bugs
3. Develop in feature branches
4. Create PRs (templates + validation enforced)
5. Review and merge
6. Update CHANGELOG.md
7. Bump version in pyproject.toml and __version__.py
8. Create GitHub release with tag
9. Publish release notes

---

## Contributing

This is currently a focused utility tool. Feature requests and bug reports are welcome via GitHub Issues.

For major changes, please open an issue first to discuss what you would like to change.

---

## Feedback & Support

- **Issues**: https://github.com/RKInnovate/evernote-exporter/issues
- **Discussions**: Open an issue for questions or feedback

---

## Around the Sun Development Model ☀️

This project follows an "around the sun" collaborative development approach:
- Work is handed off between team members across time zones
- Each developer works for ~12 hours, then hands off
- Continuous progress without burnout
- Clear handoff notes in commits and issues

**Current Handoff**: From Viresh (Cadile 2) → Ravindra → Back to team

---

*Last Updated: December 10, 2025*
*Next Review: After v1.1.0 release*
