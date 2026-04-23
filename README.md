# PII Anonymizor

> **Offline Windows 11 PII Anonymizer — no cloud, no OCR, text-based files only.**

PII Anonymizor is a Windows desktop utility that detects and anonymizes personally identifiable information (PII) in Word and text-based files. The app is designed to work fully offline after launch, and the current project supports a browser-based GitHub build flow so non-technical users can create the Windows `.exe` without installing Python locally. GitHub documents repository creation, browser uploads, Actions workflow runs, and artifact downloads through its web interface.

## What the app does

- Upload a supported file and scan it for common PII categories.
- Review each finding before export.
- Replace approved findings with tags like `[EMAIL]`, `[PHONE]`, and `[NAME]`.
- Save a **new anonymized copy** so the original file stays untouched.
- Optionally export a JSON audit report for traceability.

## Main features

- Drag-and-drop or browse to select a file.
- Built-in PII categories enabled by default.
- Review-first workflow to reduce accidental over-redaction.
- Up to 5 custom regex patterns for one-time use.
- DOCX formatting-preserving export support.
- Offline processing after the app is opened.
- Windows executable build support through GitHub Actions artifacts. GitHub’s artifact system is the mechanism used to download build outputs from completed workflow runs.

## Supported file types

| Format | Extensions |
|---|---|
| Word | `.docx`, `.doc` |
| Plain text | `.txt`, `.log`, `.csv` |
| Markdown | `.md`, `.markdown` |
| Config and markup | `.json`, `.xml`, `.ini`, `.cfg`, `.yaml`, `.yml`, `.toml` |
| Rich text | `.rtf` |

> **Not supported in this version:** PDF, scanned documents, image-based files, OCR workflows.

## Built-in PII categories

| Category | Replacement tag |
|---|---|
| Full names (high-precision, label/salutation-based) | `[NAME]` |
| Email addresses | `[EMAIL]` |
| Phone numbers | `[PHONE]` |
| SSN / National ID | `[SSN]` |
| Credit / debit card numbers | `[CARD_NUMBER]` |
| Dates of birth | `[DATE_OF_BIRTH]` |
| Bank / account numbers | `[BANK_ACCOUNT]` |
| IP addresses | `[IP_ADDRESS]` |
| ZIP / postal codes | `[ZIP_CODE]` |
| Street addresses | `[ADDRESS]` |
| URLs | `[URL]` |

## Easiest way to get the EXE

The easiest path for a non-technical user is to let **GitHub Actions** build the Windows executable remotely, then download the finished artifact from the repository’s **Actions** page. GitHub’s documentation explains how to upload files in the browser and download workflow artifacts after the run completes.

### Step 1: Create a GitHub repository

1. Sign in to GitHub.
2. Click the **+** icon in the top-right corner.
3. Choose **New repository**.
4. Enter a repository name such as `pii-shield`.
5. Choose **Private** or **Public**.
6. Click **Create repository**. GitHub’s repository quickstart covers this browser flow.

### Step 2: Upload the project files in your browser

1. Open the new repository.
2. Click **Add file**.
3. Choose **Upload files**.
4. Drag the unzipped project files and folders into the page.
5. Click **Commit changes**. GitHub supports uploading project files directly through the web interface.

### Step 3: Add the GitHub Actions workflow file

Create this file in your repository:

`.github/workflows/build-windows.yml`

Paste this content into that file:

```yaml
name: Build Windows EXE

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest

    steps:
      - name: Download repository
        uses: actions/checkout@v4

      - name: Install Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install app packages
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Build EXE
        run: |
          pyinstaller --noconfirm --clean --onefile --windowed --name "PII-Shield" src/main.py

      - name: Show dist folder
        run: dir dist

      - name: Upload built app
        uses: actions/upload-artifact@v4
        with:
          name: PII-Shield-Windows
          path: dist/PII-Shield.exe
```

GitHub Actions supports manually triggered workflows with `workflow_dispatch`, and uploaded artifacts can be downloaded from the finished run page.

### Step 4: Run the workflow

1. Click the **Actions** tab in the repository.
2. Click **Build Windows EXE**.
3. Click **Run workflow**.
4. Wait for the build to finish. GitHub’s Actions interface provides the run summary and step-by-step logs for troubleshooting.

### Step 5: Download the built EXE

1. Open the completed workflow run.
2. Scroll to the **Artifacts** section.
3. Click **PII-Shield-Windows** to download it.
4. Unzip the downloaded artifact.
5. Run `PII-Shield.exe`. GitHub documents artifact download from the workflow run summary page.

## Important build note

You do **not** need Python installed on your own laptop if GitHub Actions builds the app for you, because the Windows runner installs what it needs during the workflow and the downloadable artifact is the build output. This is why the GitHub Actions method is the recommended path for non-technical users who only need the final EXE.

## Local developer build

If someone wants to run or modify the project locally, Python is still required on the build machine.

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/pii-shield.git
cd pii-shield

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python src/main.py
```

## Local Windows EXE build

If building locally on Windows:

```bash
build.bat
```

The generated executable will appear in `dist/`, and PyInstaller’s one-file mode is intended to create a standalone application bundle for distribution.

## Known fixes

A previous GitHub Actions build failure was caused by a syntax error in `src/main.py` inside the `orig_lbl = make_label(...)` block. If that older code is still present in a fork, replace it with the corrected `short_text` version before rebuilding.

Correct version:

```python
        short_text = self.finding.original[:40]
        if len(self.finding.original) > 40:
            short_text += "…"

        orig_lbl = make_label(
            f'"{short_text}"',
            "muted"
        )
```

## Project structure

```text
pii-shield/
├── .github/
│   └── workflows/
│       └── build-windows.yml
├── src/
│   ├── main.py
│   ├── engine.py
│   ├── patterns.py
│   ├── file_handler.py
│   └── audit.py
├── tests/
│   └── test_engine.py
├── build.bat
├── pii_shield.spec
├── requirements.txt
├── README.md
└── LICENSE
```

## Contributing

Good beginner contribution areas include regex improvement, file-format support, UI polish, and Windows packaging improvements. If contributing through GitHub, browser-based editing and direct file upload are supported through the repository interface.

## License

MIT — see `LICENSE`.
