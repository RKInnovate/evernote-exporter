# Release Process

Guide for creating and publishing new releases of the Evernote to Google Drive migration tool.

---

## Versioning Policy

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH

Example: v1.2.3
```

### Version Number Meaning

| Component | When to Increment | Example |
|-----------|-------------------|---------|
| **MAJOR** | Incompatible API changes, breaking changes | `1.x.x` → `2.0.0` |
| **MINOR** | New features (backward compatible) | `1.1.x` → `1.2.0` |
| **PATCH** | Bug fixes (backward compatible) | `1.1.1` → `1.1.2` |

### Examples

**MAJOR version bump (2.0.0):**
- Changed output directory structure
- Removed support for Python 3.8
- Changed CLI flag names (breaking change)

**MINOR version bump (1.1.0):**
- Added `--no-serial` flag (new feature)
- Added collision detection (enhancement)
- Added new log entry types

**PATCH version bump (1.0.1):**
- Fixed crash with malformed ENEX
- Fixed MIME type detection bug
- Fixed typo in help text

---

## Release Cadence

- **MAJOR:** When necessary (rare)
- **MINOR:** Quarterly or when milestone complete
- **PATCH:** As needed for critical bugs

**Current schedule:**
- **v1.1.0:** Q1 2026 (Production Hardening)
- **v1.2.0:** Q2 2026 (Advanced Features)
- **v2.0.0:** TBD (Multi-Platform Support)

---

## Pre-Release Checklist

Before starting the release process, ensure:

### Code Quality

- [ ] All tests pass (manual testing with sample data)
- [ ] `uv run ruff check` passes without errors
- [ ] `uv run black --check .` passes
- [ ] `uv run mypy .` passes (or acceptable warnings documented)
- [ ] No TODOs or FIXMEs in code (or tracked in issues)

### Documentation

- [ ] CHANGELOG.md updated with all changes
- [ ] README.md reflects current features
- [ ] docs/reference.md updated with new flags/behavior
- [ ] docs/usage.md updated with new workflows
- [ ] CLAUDE.md updated with architectural changes
- [ ] All code comments accurate and up-to-date

### Functionality

- [ ] Smoke test completed successfully
- [ ] Tested with real Evernote exports
- [ ] Tested both `uv` and `pip` installation methods
- [ ] Tested on target Python versions (3.9, 3.10, 3.11, 3.12)
- [ ] Google Drive upload tested end-to-end
- [ ] Dry-run mode tested

### Milestone & Issues

- [ ] All issues in milestone closed or moved
- [ ] GitHub Actions workflows passing
- [ ] No open security issues
- [ ] All PRs for this release merged

---

## Release Steps

### 1. Update Version Numbers

Update version in **two** files:

**`pyproject.toml`:**
```toml
[project]
name = "evernote-exporter"
version = "1.1.0"  # <-- Update this
```

**`__version__.py`:**
```python
__version__ = "1.1.0"  # <-- Update this
__build_id__ = "xxx"
__author__ = "BadRat-in"
```

**Verify:**
```bash
uv run python -c "from __version__ import __version__; print(__version__)"
# Should print: 1.1.0
```

### 2. Update CHANGELOG.md

Move unreleased changes to new version section:

```markdown
## [Unreleased]

(empty or new work in progress)

## [1.1.0] - 2026-01-15

### Added
- Optional filename preservation flag (`-ns` or `--no-serial`)
- Automatic filename collision handling
- Collision warning logging

### Fixed
- Critical bug: Files no longer silently skipped with duplicate titles
- Dual package manager support (pip and uv)

### Changed
- (any breaking changes or behavior modifications)

## [1.0.0] - 2025-12-10
...
```

**Update links at bottom:**
```markdown
## Links

- [1.1.0]: https://github.com/RKInnovate/evernote-exporter/releases/tag/v1.1.0
- [1.0.0]: https://github.com/RKInnovate/evernote-exporter/releases/tag/v1.0.0
- [Unreleased]: https://github.com/RKInnovate/evernote-exporter/compare/v1.1.0...HEAD
```

### 3. Update requirements.txt (if dependencies changed)

```bash
# Generate requirements.txt from pyproject.toml
uv pip compile pyproject.toml -o requirements.txt
```

### 4. Run Final Quality Checks

```bash
# Lint and format
uv run ruff check --fix
uv run black .

# Type check
uv run mypy .

# Verify help text shows correct version (if displayed)
uv run python main.py --help

# Run smoke test
uv run python main.py --dry-run -o ./test-release
rm -rf ./test-release
```

### 5. Commit Version Bump

```bash
git add pyproject.toml __version__.py CHANGELOG.md requirements.txt
git commit -m "chore(release): bump version to v1.1.0

- Updated version in pyproject.toml and __version__.py
- Moved unreleased changes to v1.1.0 in CHANGELOG.md
- Regenerated requirements.txt with updated dependencies
"
```

### 6. Create Release Branch (Optional for Major/Minor)

```bash
# For major/minor releases, create a release branch
git checkout -b release/v1.1.0

# Push to GitHub
git push origin release/v1.1.0
```

### 7. Create Pull Request

**Title:** `Release v1.1.0`

**Description:**
```markdown
## Release v1.1.0 - Production Hardening

### Summary
This release focuses on robustness and dual package manager support.

### Key Changes
- ✨ Added `--no-serial` flag to preserve original filenames
- 🐛 Fixed critical bug: duplicate titles no longer silently skip files
- 📦 Added pip compatibility alongside uv

### Breaking Changes
None

### Migration Guide
No migration needed. All changes are backward compatible.

### Checklist
- [x] Version updated in pyproject.toml and __version__.py
- [x] CHANGELOG.md updated
- [x] Documentation updated
- [x] All tests pass
- [x] Code quality checks pass

### Related Issues
Closes #1, Closes #5, Closes #6
```

### 8. Review and Merge

1. Request review from maintainers
2. Wait for GitHub Actions to pass
3. Address any feedback
4. Merge to `main` (use "Squash and merge" or "Merge commit")

### 9. Tag the Release

```bash
# Pull latest main
git checkout main
git pull origin main

# Create annotated tag
git tag -a v1.1.0 -m "Release v1.1.0 - Production Hardening

Key changes:
- Added --no-serial flag for filename preservation
- Fixed critical collision bug
- Added pip/uv dual compatibility

See CHANGELOG.md for full details."

# Push tag to GitHub
git push origin v1.1.0
```

### 10. Create GitHub Release

1. Go to https://github.com/RKInnovate/evernote-exporter/releases
2. Click "Draft a new release"
3. Select tag `v1.1.0`
4. Release title: `v1.1.0 - Production Hardening`
5. Description:

```markdown
## 🎉 v1.1.0 - Production Hardening

This release focuses on robustness, collision handling, and dual package manager support.

### ✨ New Features

- **Filename Preservation Flag** (`-ns`, `--no-serial`)
  - Preserve original note filenames without 6-digit ID prefix
  - Automatic collision detection adds `_1`, `_2` suffixes when needed

- **Collision Warning System**
  - Console warnings for duplicate filenames
  - Logged to `extraction_log.json` for auditing

- **Dual Package Manager Support**
  - Works with both `uv` (modern) and `pip` (traditional)
  - Added `[project.optional-dependencies]` for pip compatibility

### 🐛 Bug Fixes

- **Critical:** Files with duplicate titles are no longer silently skipped
  - Previously, second note with same title would be lost
  - Now automatically renamed with suffix

- **Linter Configuration:** Updated ruff config to new format

### 📚 Documentation

- New organized docs structure under `docs/`
- Added comprehensive CLI reference
- Added developer guide for contributors
- Added release process documentation

### 🔧 Technical Changes

- Minimum Python version: 3.9+ (required by Pillow 12.0)
- Added `get_unique_filepath()` helper for collision detection
- Improved error handling and logging

### 📦 Installation

**With uv (recommended):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/RKInnovate/evernote-exporter.git
cd evernote-exporter
uv sync
uv run python main.py --help
```

**With pip:**
```bash
git clone https://github.com/RKInnovate/evernote-exporter.git
cd evernote-exporter
pip install -r requirements.txt
python main.py --help
```

### 🔗 Links

- [Documentation](docs/)
- [Usage Guide](docs/usage.md)
- [CLI Reference](docs/reference.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](docs/roadmap.md)

### 🙏 Contributors

Thank you to everyone who contributed to this release!

---

**Full Changelog**: https://github.com/RKInnovate/evernote-exporter/compare/v1.0.0...v1.1.0
```

6. Click "Publish release"

### 11. Announce Release

- Update README.md if installation instructions changed
- Post in GitHub Discussions (if enabled)
- Share on relevant forums/communities (optional)

---

## Post-Release

### Create Next Milestone

1. Go to GitHub Milestones
2. Create `v1.2.0` milestone
3. Add planned issues from roadmap
4. Set due date (target Q2 2026)

### Update Roadmap

Move completed features from "Unreleased" to the released version section in `docs/roadmap.md`.

### Monitor Issues

Watch for bug reports related to new release:
- Check GitHub Issues
- Monitor email for error reports
- Review any user feedback

### Hotfix Process (if needed)

If critical bug discovered:

1. Create hotfix branch: `git checkout -b hotfix/v1.1.1`
2. Fix bug
3. Update CHANGELOG.md (add `## [1.1.1]` section)
4. Bump version to `1.1.1` in `pyproject.toml` and `__version__.py`
5. Commit: `fix: critical bug description`
6. PR and merge
7. Tag: `git tag v1.1.1`
8. Create GitHub Release

---

## Version Branches

### Branch Strategy

- **`main`** - Latest stable release
- **`feature/*`** - New features
- **`bugfix/*`** - Bug fixes
- **`hotfix/*`** - Emergency patches
- **`release/*`** - Release preparation (optional for major/minor)

### Branch Naming

```
feature/add-verbose-logging
bugfix/fix-mime-detection
hotfix/critical-crash
release/v1.2.0
```

---

## Rollback Procedure

If a release has critical issues:

### Option 1: Hotfix Release (Preferred)

1. Fix bug in hotfix branch
2. Release v1.1.1 with fix
3. Keep v1.1.0 tag (mark as deprecated in release notes)

### Option 2: Revert Tag (Last Resort)

```bash
# Delete tag locally
git tag -d v1.1.0

# Delete tag on GitHub
git push origin :refs/tags/v1.1.0

# Mark GitHub Release as "Pre-release" or delete it
# (Go to GitHub → Releases → Edit)

# Create new release with fix
```

**Warning:** Only do this if release was very recent and no one has downloaded it.

---

## Release Artifacts

### Files to Include (Future)

Currently, releases are source-only. Future enhancements:

- [ ] Pre-built Python wheels (`.whl` files)
- [ ] Standalone executables (PyInstaller)
- [ ] Docker images
- [ ] Homebrew formula
- [ ] pip-installable package (PyPI)

### Publishing to PyPI (Future)

```bash
# Build distribution
uv build

# Upload to PyPI
uv publish

# Or with twine
python -m twine upload dist/*
```

---

## Versioning Anti-Patterns

### ❌ Don't:

- Bump version without updating CHANGELOG
- Create tags without testing
- Release with failing CI/CD
- Skip documentation updates
- Forget to push tags (`git push` without `--tags` or explicit tag name)
- Use generic commit messages for version bumps

### ✅ Do:

- Test thoroughly before tagging
- Update all version references
- Write clear release notes
- Document breaking changes
- Keep CHANGELOG accurate
- Communicate changes to users

---

## Emergency Release Checklist

For critical security or data-loss bugs:

1. **Immediate actions:**
   - [ ] Create private branch for fix
   - [ ] Verify fix resolves issue
   - [ ] Add regression test (if applicable)

2. **Fast-track release:**
   - [ ] Bump PATCH version
   - [ ] Update CHANGELOG with security note
   - [ ] Skip normal review process (maintainer approval only)
   - [ ] Tag and release immediately

3. **Communication:**
   - [ ] Mark previous version as vulnerable (GitHub Security Advisory)
   - [ ] Post notice in README if critical
   - [ ] Email known users (if contact list exists)

---

## Version Archive

All releases are preserved in GitHub:

- **Tags:** `git tag -l`
- **Releases:** https://github.com/RKInnovate/evernote-exporter/releases
- **CHANGELOG:** [CHANGELOG.md](../CHANGELOG.md)

---

## Additional Resources

- [Semantic Versioning Specification](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## Questions?

If you have questions about the release process:

- Check [Developer Guide](dev.md)
- Open a [Support Question issue](https://github.com/RKInnovate/evernote-exporter/issues/new?template=support_question.yml)
- Contact maintainers directly
