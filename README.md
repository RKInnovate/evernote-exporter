# Evernote to Google Drive Migrator

A super simple and bulletproof script to migrate your notes from **Evernote** (via `.enex` export files) to **Google Drive**, preserving notebook hierarchy and note content.

---

## 🚀 Features

- 🗂️ Recreates Evernote notebook structure as Drive folders
- 📝 Uploads notes as individual Google Docs
- 📦 Supports multiple `.enex` exports
- 🔐 Uses OAuth 2.0 to authorize your personal Google Drive
- 🧪 Minimal setup, runs locally

---

## 📁 How It Works

1. Export notebooks from Evernote as `.enex` files.
2. Run the script, and sign in with your Google account.
3. The tool will parse the `.enex` files and replicate your notebooks in Google Drive.

---

## 🛠️ Requirements

- Python 3.9+
- Google Cloud Project with **Drive API** enabled
- OAuth 2.0 credentials (`credentials.json`)
- **uv** package manager (recommended) or pip

### Installing uv (Recommended)

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew on macOS
brew install uv
```

### Installing Dependencies

**With uv (recommended):**
```bash
# Install dependencies in a virtual environment
uv sync

# Or run directly without installing
uv run python main.py
```

**With pip (traditional):**
```bash
pip install -r requirements.txt
```

---

## ⚙️ Usage

**With uv:**
```bash
# Run with default options
uv run python main.py

# Run with custom output directory
uv run python main.py --output-directory ./my-notes

# Dry run (extract files but don't upload)
uv run python main.py --dry-run

# Show help
uv run python main.py --help
```

**With pip/traditional Python:**
```bash
python main.py -h -d --output-directory {{OutputDirectory}}
```

### Command-line Options

- `-o` OR `--output-directory`: Specify the directory where the output will be saved and the same directory name will be used in Google Drive.
- `-d` OR `--dry-run`: Run the script without uploading any files.
- `-h` OR `--help`: Display this help message.

---

## 🔐 OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or use an existing one.
3. Enable the **Google Drive API**.
4. Under "APIs & Services" → "Credentials":
    - Create **OAuth 2.0 Client ID**
    - Application type: **Desktop App**
    - Download the `credentials.json` file

5. When you run the script, a browser will open to request access.
6. On first run, a `token.json` file will be generated and reused for future authentication.

> ✅ Make sure you authenticate with the same Google account where you want the notes to go!

---

## 📌 Notes

- Each `.enex` file maps to one notebook.
- Notes are converted into Google Docs.
- Notebook structure is recreated using Drive folders.

---

## 🙌 Contributing

This is a focused utility tool, but PRs and bug reports are welcome!

---

## 🧠 Why This Exists

Evernote doesn’t provide a clean way to migrate content into Google Drive. This tool is a lightweight bridge — ideal for individuals or teams moving away from Evernote.
