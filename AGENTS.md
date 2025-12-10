# Repository Guidelines

## Project Structure & Module Organization
- `main.py` orchestrates the ENEX parsing pipeline, calling helpers in `gdrive.py` for OAuth and Drive uploads and `pdf_utils.py` for PDF/text handling.
- Place Evernote exports in `input_data/`; outputs are written under `output/<NotebookName>`, mirroring the Drive folder structure the script creates.
- Auth artifacts (`credentials.json`, generated `token.json`) live in the repo root but must never be committed; `extraction_log.json` records processing issues during runs.
## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` — create an isolated environment.
- `pip install -r requirements.txt` — install Google API clients, PDF tooling, and XML dependencies.
- `python main.py --dry-run --output-directory output/Medical.Viresh.Current` — parse `.enex` files without uploading; use this before every PR to verify structure.
- `python main.py --output-directory <DriveFolder> --input-dir input_data` — full migration run; ensure OAuth has been authorized.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4‑space indentation and snake_case for functions (`process_enex_file`), PascalCase reserved for classes (currently none).
- Use `pathlib.Path` for filesystem work and keep notebook/note names filesystem-safe (see `safe_title` logic); extend that helper instead of embedding custom replacements.
- Keep any new modules flat at repo root so `main.py` imports stay simple.

## Testing Guidelines
- No automated test suite exists; rely on dry-run executions plus manual inspection of `output/` artifacts and `extraction_log.json`.
- When adding logic, run lightweight smoke commands (e.g., `python main.py --dry-run --input-dir fixtures/health`) and keep fixtures under `input_data/fixtures/`.
- Name future tests `test_<module>.py` and keep them independent of live Google credentials by mocking Drive calls in `gdrive`.

## Commit & Pull Request Guidelines
- Git history favors Conventional Commit prefixes with emojis (`feat: ✨`, `fix: 🩹`, `refactor: 🔨`); follow the same pattern so changelog reads consistently.
- Keep commits scoped: parsing changes separate from Drive auth or PDF tweaks.
- PRs should describe the migration scenario validated (input notebook, dry-run vs upload), list new commands or flags, and mention any changes to credential handling; attach relevant console output or screenshots of Drive results when applicable.

## Security & Configuration Tips
- Store `credentials.json` and generated `token.json` securely; rotate them if the Google project or scopes change.
- Never commit PHI/PII produced under `output/`; treat that directory as ephemeral and add new ignore rules if additional formats appear.
- Use `--dry-run` plus a temporary `output/preview` directory when reviewing community contributions to avoid polluting personal Drive accounts.
