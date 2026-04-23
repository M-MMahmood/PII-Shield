# PII Shield

> **Offline Windows 11 PII Anonymizer — fork-friendly, open-source, zero cloud.**

PII Shield is a modern Windows desktop utility that detects and replaces
Personally Identifiable Information (PII) in Word and text-based documents.
All processing happens **100% locally** on your machine — no internet connection,
no cloud upload, no OCR.

---

## Features

- ✅ Drag-and-drop or browse to open a file
- ✅ Built-in detection for 10 PII categories, all enabled by default
- ✅ Conservative (high-precision) detection to minimise false positives
- ✅ Review every finding before saving — keep or ignore each one individually
- ✅ Add 1–5 custom regex patterns per run (not saved between sessions)
- ✅ Preserves Word document formatting on export
- ✅ Creates a **new anonymized copy** — original file is never modified
- ✅ Generates a JSON audit report
- ✅ Fully offline — files never leave your device

---

## Supported file types

| Format | Extension(s) |
|---|---|
| Word (format-preserving) | `.docx`, `.doc` |
| Plain text | `.txt`, `.log`, `.csv` |
| Markdown | `.md`, `.markdown` |
| Config / markup | `.json`, `.xml`, `.ini`, `.cfg`, `.yaml`, `.yml`, `.toml` |
| Rich Text | `.rtf` |

> ❌ **Not supported:** PDF, scanned documents, image-based files. No OCR.

---

## Built-in PII categories

| Category | Replacement tag |
|---|---|
| Full names (salutation-scoped) | `[NAME]` |
| Email addresses | `[EMAIL]` |
| Phone numbers | `[PHONE]` |
| SSN / National ID | `[SSN]` |
| Credit / debit card numbers | `[CARD_NUMBER]` |
| Dates of birth (labelled) | `[DATE_OF_BIRTH]` |
| Bank / account numbers | `[BANK_ACCOUNT]` |
| IP addresses | `[IP_ADDRESS]` |
| ZIP / postal codes (labelled) | `[ZIP_CODE]` |
| Street addresses | `[ADDRESS]` |
| URLs | `[URL]` |

---

## Getting started (from source)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/pii-shield.git
cd pii-shield

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python src/main.py
```

---

## Build a standalone Windows .exe

```bash
# From the repo root, with your venv active:
build.bat
```

The output `PII-Shield.exe` will be in `dist/`. It is self-contained —
no Python installation required on the target machine.

---

## Project structure

```
pii-shield/
├── src/
│   ├── main.py          # UI — PySide6 app, all 4 screens
│   ├── engine.py        # Detection + redaction logic
│   ├── patterns.py      # Built-in PII regex patterns
│   ├── file_handler.py  # DOCX + text read/write
│   └── audit.py         # JSON audit report generator
├── tests/
│   └── test_engine.py   # Unit tests for detection engine
├── build.bat            # One-click Windows build script
├── requirements.txt
└── README.md
```

---

## Contributing

Good first issues are labelled `good-first-issue` in GitHub Issues.

Key areas for contribution:
- **`patterns.py`** — add or improve PII regex patterns
- **`file_handler.py`** — add support for new file formats
- **`engine.py`** — improve deduplication or add NLP-based detection
- **`main.py`** — UI improvements, accessibility

Please open an issue before starting large changes so we can discuss approach.

---

## License

MIT — see `LICENSE`.
