# How to Set Up and Run Evernote Exporter on Mac

This guide will walk you through setting up all dependencies and running the Evernote to Google Drive migrator on your Mac, even if you're completely new to Python.

---

## 📋 Table of Contents

1. [Prerequisites Check](#1-prerequisites-check)
2. [Installing Python (if needed)](#2-installing-python-if-needed)
3. [Installing uv Package Manager (Recommended)](#3-installing-uv-package-manager-recommended)
4. [Setting Up the Project](#4-setting-up-the-project)
5. [Installing Dependencies](#5-installing-dependencies)
6. [Setting Up Google Drive API](#6-setting-up-google-drive-api)
7. [Preparing Your ENEX Files](#7-preparing-your-enex-files)
8. [Running the Program](#8-running-the-program)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites Check

### Step 1.1: Check if Python is Installed

1. **Open Terminal**:
   - Press `Cmd + Space` to open Spotlight
   - Type "Terminal" and press Enter
   - Or go to Applications → Utilities → Terminal

2. **Check Python version**:
   Type this command and press Enter:
   ```bash
   python3 --version
   ```

3. **What you should see**:
   - ✅ **Good**: `Python 3.9.x` or higher (e.g., `Python 3.9.7`, `Python 3.11.5`, `Python 3.12.0`)
   - ❌ **Problem**: `command not found` or version lower than 3.9

### Step 1.2: Check if pip is Installed

1. **In Terminal, type**:
   ```bash
   pip3 --version
   ```

2. **What you should see**:
   - ✅ **Good**: `pip 20.x.x` or higher
   - ❌ **Problem**: `command not found`

**Note**: If you have Python 3.9+, pip3 is usually installed automatically. If not, we'll install it in the next section.

---

## 2. Installing Python (if needed)

### Option A: Install Python via Homebrew (Recommended)

**Homebrew** is a package manager for Mac that makes installing software easy.

1. **Install Homebrew** (if you don't have it):
   - Open Terminal
   - Copy and paste this command:
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```
   - Press Enter and follow the prompts
   - Enter your Mac password when asked (you won't see characters as you type - this is normal)
   - Wait for installation to complete (may take 5-10 minutes)

2. **Install Python**:
   ```bash
   brew install python3
   ```

3. **Verify installation**:
   ```bash
   python3 --version
   pip3 --version
   ```

### Option B: Install Python from Official Website

1. **Download Python**:
   - Visit: https://www.python.org/downloads/
   - Click the yellow "Download Python" button (it will detect your Mac)
   - The file will download (e.g., `python-3.12.x-macos11.pkg`)

2. **Install Python**:
   - Open the downloaded `.pkg` file
   - Follow the installation wizard
   - **Important**: Check the box "Add Python to PATH" if available
   - Complete the installation

3. **Verify installation**:
   - Open Terminal
   - Type: `python3 --version`
   - You should see a version number

---

## 3. Installing uv Package Manager (Recommended)

**uv** is a modern, fast Python package manager that simplifies dependency management. It's **highly recommended** as it's faster and more reliable than traditional pip.

### Step 3.1: Install uv

**Option A: Install with Homebrew (Easiest for Mac)**

If you already have Homebrew installed:
```bash
brew install uv
```

**Option B: Install with curl (Universal method)**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**What this does:**
- Downloads and installs the uv package manager
- Adds uv to your system PATH automatically
- Takes just a few seconds

### Step 3.2: Verify Installation

After installation, close and reopen Terminal, then type:
```bash
uv --version
```

You should see something like: `uv 0.9.12` or similar

### Step 3.3: Why Use uv?

- **10-100x faster** than pip for installing packages
- **Automatic virtual environment management** - no need to manually create/activate venvs
- **Lockfile support** - ensures everyone has the same dependency versions
- **Better error messages** when things go wrong
- **Compatible** with all existing Python projects

**Note:** If you prefer to use traditional pip instead, skip to the "With pip" instructions in each section below.

---

## 4. Setting Up the Project

### Step 4.1: Navigate to the Project Directory

1. **Open Terminal**

2. **Navigate to the project folder**:
   ```bash
   cd ~/Projects/evernote-exporter
   ```
   
   **Note**: If your project is in a different location, adjust the path accordingly. You can also:
   - Type `cd ` (with a space after cd)
   - Drag the project folder from Finder into Terminal
   - Press Enter

3. **Verify you're in the right place**:
   ```bash
   ls
   ```
   You should see files like `main.py`, `requirements.txt`, `README.md`, etc.

---

## 5. Installing Dependencies

Choose between **uv (recommended)** or **traditional pip**. Don't do both!

### Option A: Install with uv (Recommended - Faster and Simpler)

**uv handles everything automatically** - no need to create or activate virtual environments manually!

1. **Make sure you're in the project directory** (see Step 4.1)

2. **Install all dependencies with one command**:
   ```bash
   uv sync
   ```

3. **What happens**:
   - uv automatically creates a virtual environment (`.venv`) if it doesn't exist
   - Downloads and installs all required packages from `pyproject.toml`
   - Creates a lockfile (`uv.lock`) to ensure consistent versions
   - **Much faster** than pip - typically completes in 10-30 seconds
   - You'll see a progress bar and "Installed X packages" message

4. **That's it!** You don't need to manually activate the environment. When you run the program with `uv run`, it automatically uses the correct environment.

### Option B: Install with pip (Traditional Method)

If you prefer the traditional approach:

#### Step B.1: Create a Virtual Environment

A virtual environment keeps your project's dependencies separate from other Python projects.

1. **Create the virtual environment**:
   ```bash
   python3 -m venv .venv
   ```
   This creates a folder called `.venv` in your project directory.

2. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

   **You'll know it's activated when you see `(.venv)` at the start of your Terminal prompt**, like:
   ```
   (.venv) your-username@your-mac evernote-exporter %
   ```

3. **Keep Terminal open** - you'll need to activate the virtual environment each time you open a new Terminal window.

#### Step B.2: Upgrade pip

First, make sure pip is up to date:

```bash
pip3 install --upgrade pip
```

Wait for it to complete (you'll see "Successfully installed pip-x.x.x").

#### Step B.3: Install Project Dependencies

1. **Make sure your virtual environment is activated** (you should see `(.venv)` in your prompt)

2. **Install all required packages**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **What happens**:
   - This will download and install all packages listed in `requirements.txt`
   - It may take 2-5 minutes depending on your internet speed
   - You'll see lots of text scrolling by - this is normal
   - Wait until you see "Successfully installed" messages

4. **Verify installation**:
   ```bash
   pip3 list
   ```
   You should see packages like `google-api-python-client`, `reportlab`, `pypdf`, `Pillow`, etc.

### Install System Dependencies (if needed - Both Methods)

Some Python packages require system libraries. If you encounter errors during installation:

1. **Install Xcode Command Line Tools** (if not already installed):
   ```bash
   xcode-select --install
   ```
   - A popup will appear - click "Install"
   - Wait for installation to complete

2. **If you get errors about missing image libraries**, install via Homebrew:
   ```bash
   brew install libjpeg libpng
   ```

---

## 6. Setting Up Google Drive API

To upload files to Google Drive, you need to set up API credentials.

### Step 5.1: Create a Google Cloud Project

1. **Go to Google Cloud Console**:
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account (the one where you want notes uploaded)

2. **Create a new project**:
   - Click the project dropdown at the top
   - Click "New Project"
   - Enter a project name (e.g., "Evernote Exporter")
   - Click "Create"
   - Wait a few seconds, then select your new project from the dropdown

### Step 5.2: Enable Google Drive API

1. **Navigate to APIs & Services**:
   - In the left sidebar, click "APIs & Services" → "Library"
   - Or visit: https://console.cloud.google.com/apis/library

2. **Search for Drive API**:
   - Type "Google Drive API" in the search box
   - Click on "Google Drive API" from the results

3. **Enable the API**:
   - Click the blue "Enable" button
   - Wait for it to enable (may take 10-30 seconds)

### Step 5.3: Create OAuth 2.0 Credentials

1. **Go to Credentials**:
   - In the left sidebar, click "APIs & Services" → "Credentials"
   - Or visit: https://console.cloud.google.com/apis/credentials

2. **Create OAuth consent screen** (first time only):
   - Click "Configure Consent Screen" at the top
   - Select "External" (unless you have a Google Workspace account)
   - Click "Create"
   - Fill in:
     - **App name**: "Evernote Exporter" (or any name)
     - **User support email**: Your email
     - **Developer contact email**: Your email
   - Click "Save and Continue"
   - On "Scopes" page, click "Save and Continue"
   - On "Test users" page, click "Save and Continue"
   - Review and click "Back to Dashboard"

3. **Create OAuth 2.0 Client ID**:
   - Click "+ Create Credentials" → "OAuth client ID"
   - If prompted, select "Desktop app" as application type
   - **Application type**: Select "Desktop app"
   - **Name**: "Evernote Exporter Desktop" (or any name)
   - Click "Create"

4. **Download credentials**:
   - A popup will show your Client ID and Client Secret
   - Click "Download JSON" (or "OK" and download manually)
   - The file will be named something like `client_secret_xxxxx.json`

### Step 5.4: Place Credentials in Project

1. **Rename the downloaded file**:
   - Find the downloaded JSON file (usually in your Downloads folder)
   - Rename it to exactly: `credentials.json`
   - Make sure there are no extra spaces or characters

2. **Move to project directory**:
   - Open Finder
   - Navigate to your project folder: `~/Projects/evernote-exporter`
   - Drag `credentials.json` into this folder
   - Or use Terminal:
     ```bash
     mv ~/Downloads/client_secret_*.json ~/Projects/evernote-exporter/credentials.json
     ```
     (Adjust the path if your file has a different name or location)

3. **Verify the file is there**:
   ```bash
   ls credentials.json
   ```
   You should see: `credentials.json`

---

## 7. Preparing Your ENEX Files

### Step 6.1: Export Notes from Evernote

1. **Open Evernote** (desktop app or web)

2. **Export notebooks**:
   - Select a notebook
   - Go to File → Export Notes (or right-click notebook → Export)
   - Choose "ENEX Format"
   - Save the `.enex` file

3. **Repeat for each notebook** you want to migrate

### Step 6.2: Place ENEX Files in Input Directory

1. **Create input_data folder** (if it doesn't exist):
   ```bash
   mkdir -p input_data
   ```

2. **Copy ENEX files**:
   - Open Finder
   - Navigate to where you saved your `.enex` files
   - Copy all `.enex` files
   - Navigate to: `~/Projects/evernote-exporter/input_data/`
   - Paste the files here

3. **Verify files are there**:
   ```bash
   ls input_data/
   ```
   You should see your `.enex` files listed

---

## 8. Running the Program

### Running with uv (Recommended)

**No need to activate a virtual environment!** uv handles everything automatically.

#### Step 8.1: Test Run (Dry Run - No Upload)

First, test the program without uploading to Google Drive:

```bash
cd ~/Projects/evernote-exporter
uv run python main.py --dry-run
```

**What happens:**
- uv automatically uses the correct virtual environment
- The program extracts notes from `.enex` files to the output directory
- No files are uploaded to Google Drive (dry run mode)
- You can check the output in `./EverNote Notes/` directory

#### Step 8.2: Full Run (With Google Drive Upload)

Once you're satisfied with the dry run:

```bash
uv run python main.py
```

**What happens:**
- Extracts all notes from ENEX files
- Opens a browser window for Google OAuth authentication
- Uploads all notes to Google Drive
- Creates folder structure matching your notebooks

#### Step 8.3: Custom Output Directory

To specify a different output directory:

```bash
uv run python main.py --output-directory ./my-notes
```

#### Step 8.4: Preserve Original Filenames

By default, all files are prefixed with a 6-digit ID (e.g., `A3B7F2-MyNote.pdf`). To preserve original filenames:

```bash
uv run python main.py --no-serial
# Or use the short form: -ns
```

This creates files like `MyNote.pdf` instead of `A3B7F2-MyNote.pdf`.

⚠️ **Important**: If you have multiple notes with the same title in a notebook, the tool will automatically add `_1`, `_2` suffixes to prevent data loss (e.g., `MyNote.pdf`, `MyNote_1.pdf`, `MyNote_2.pdf`).

### Running with pip/Traditional Python

If you're using pip, you need to activate the virtual environment first.

#### Step 8.1: Activate Virtual Environment (if not already active)

If you closed Terminal or opened a new window:

```bash
cd ~/Projects/evernote-exporter
source .venv/bin/activate
```

You should see `(.venv)` in your prompt.

#### Step 8.2: Test Run (Dry Run - No Upload)

First, test the program without uploading to Google Drive:

```bash
python3 main.py --dry-run
```

**What happens**:
- The program will process all `.enex` files in `input_data/`
- Convert notes to PDFs
- Save them in `./EverNote Notes/` directory
- **No files will be uploaded to Google Drive**

**Check the output**:
- Look for messages like "✓ Created multi-item PDF" or "Saved single resource"
- Check the `./EverNote Notes/` folder to see your converted notes

#### Step 8.3: Full Run (With Google Drive Upload)

Once you're satisfied with the dry run:

```bash
python3 main.py
```

**What happens**:
1. Processes ENEX files (same as dry run)
2. Opens your web browser for Google authentication
3. Sign in with your Google account
4. Grant permissions to access Google Drive
5. Uploads all files to Google Drive
6. Creates a `token.pickle` file for future runs (you won't need to authenticate again)

#### Step 8.4: Custom Output Directory

To specify a different output directory:

```bash
python3 main.py --output-directory "./My Notes"
```

Or use the short form:

```bash
python3 main.py -o "./My Notes"
```

#### Step 8.5: Preserve Original Filenames

By default, all files are prefixed with a 6-digit ID (e.g., `A3B7F2-MyNote.pdf`). To preserve original filenames:

```bash
python3 main.py --no-serial
# Or use the short form: -ns
```

This creates files like `MyNote.pdf` instead of `A3B7F2-MyNote.pdf`.

⚠️ **Important**: If you have multiple notes with the same title in a notebook, the tool will automatically add `_1`, `_2` suffixes to prevent data loss (e.g., `MyNote.pdf`, `MyNote_1.pdf`, `MyNote_2.pdf`).

#### Step 8.6: View Help

To see all available options:

```bash
python3 main.py --help
```

---

## 9. Troubleshooting

### Using uv-specific Issues

#### Problem: "command not found: uv"

**Solution**:
1. uv is not installed or not in PATH
2. Install uv following Step 3
3. After installing, close and reopen Terminal
4. If still not working, try:
   ```bash
   source ~/.bashrc
   # or
   source ~/.zshrc
   ```

#### Problem: "No Python interpreter found"

**Solution**:
- uv needs Python installed
- Follow Step 2 to install Python 3.9+
- Verify with: `python3 --version`

### Using pip-specific Issues

### General Issues

#### Problem: "command not found: python3"

**Solution**:
- Python is not installed or not in PATH
- Follow Step 2 to install Python
- After installing, you may need to restart Terminal

#### Problem: "No module named 'gdrive'" or similar import errors

**Solution for uv users**:
```bash
cd ~/Projects/evernote-exporter
uv sync  # Reinstall dependencies
```

**Solution for pip users**:
1. Make sure you're in the project directory:
   ```bash
   cd ~/Projects/evernote-exporter
   ```

2. Make sure virtual environment is activated (you should see `(.venv)`):
   ```bash
   source .venv/bin/activate
   ```

3. Reinstall dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

### Problem: "credentials.json not found"

**Solution**:
1. Make sure the file is named exactly `credentials.json` (case-sensitive)
2. Make sure it's in the project root directory (same folder as `main.py`)
3. Verify with:
   ```bash
   ls -la credentials.json
   ```

### Problem: "Permission denied" errors

**Solution**:
1. Make sure you have write permissions in the project directory
2. Try:
   ```bash
   chmod -R 755 ~/Projects/evernote-exporter
   ```

### Problem: "No ENEX files found"

**Solution**:
1. Make sure `.enex` files are in the `input_data/` folder
2. Check with:
   ```bash
   ls input_data/*.enex
   ```
3. Make sure file extensions are `.enex` (not `.ENEX` or `.Enex`)

### Problem: Import errors for PIL/Pillow

**Solution**:
1. Install system dependencies:
   ```bash
   brew install libjpeg libpng
   ```

2. Reinstall Pillow:
   ```bash
   pip3 uninstall Pillow
   pip3 install Pillow
   ```

### Problem: Google Drive authentication fails

**Solution**:
1. Make sure `credentials.json` is valid (not corrupted)
2. Delete `token.pickle` and try again:
   ```bash
   rm token.pickle
   python3 main.py
   ```
3. Make sure you're using the correct Google account
4. Check that Google Drive API is enabled in Google Cloud Console

### Problem: "ModuleNotFoundError" for any package

**Solution**:
1. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Install the missing package:
   ```bash
   pip3 install <package-name>
   ```

3. Or reinstall all dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

### Problem: PDF creation fails

**Solution**:
1. Make sure you have write permissions in the output directory
2. Check available disk space:
   ```bash
   df -h
   ```
3. Try running with a different output directory:
   ```bash
   python3 main.py -o ~/Desktop/test_output
   ```

### Getting More Help

If you encounter other errors:

1. **Read the error message carefully** - it usually tells you what's wrong
2. **Check the extraction log**: Look at `extraction_log.json` for details
3. **Run with verbose output**: The program prints detailed messages as it runs
4. **Check file permissions**: Make sure you can read/write in the project directory

---

## ✅ Quick Start Checklist

Before running the program, make sure:

- [ ] Python 3.8+ is installed (`python3 --version`)
- [ ] Virtual environment is created and activated (`(venv)` in prompt)
- [ ] All dependencies are installed (`pip3 install -r requirements.txt`)
- [ ] `credentials.json` is in the project root directory
- [ ] `.enex` files are in the `input_data/` folder
- [ ] You're in the project directory when running commands

---

## 🎉 You're Ready!

Once all steps are complete, you can run:

```bash
python3 main.py --dry-run
```

Then when ready:

```bash
python3 main.py
```

Happy migrating! 🚀
