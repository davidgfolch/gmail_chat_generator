# Installation Guide

## Prerequisites

### 1. Install Python 3.11+

**Option A: Using winget (Recommended for Windows)**

```bash
winget install Python.Python.3.12
```

**Option B: Manual Installation**

- Download from [python.org/downloads](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

**Verify installation:**

```bash
python --version
```

### 2. Install Poetry

**Windows (PowerShell):**

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**Alternative (via pip):**

```bash
pip install poetry
```

**Add Poetry to PATH:**
Poetry is typically installed to `C:\Users\<USERNAME>\AppData\Roaming\Python\Scripts`

If `poetry` command doesn't work after installation, restart your terminal or add to PATH manually.

**Verify installation:**

```bash
poetry --version
```

## Project Setup

### 3. Clone or Navigate to Project

### 4. Configure Poetry to Use Python 3.11+

```bash
poetry env use python3.12
```

Or specify full path:

```bash
poetry env use C:\Users\<YOUR_USERNAME>\AppData\Local\Programs\Python\Python312\python.exe
```

### 5. Install Dependencies

```bash
poetry install
```

If you get a lock file error:

```bash
poetry lock
poetry install
```

## Gmail API Setup

### 6. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
   - **Direct Links:**
     - [Enable Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com?organizationId=0&supportedpurview=project)
     - [API Metrics](https://console.cloud.google.com/apis/api/gmail.googleapis.com/metrics?project=infra-analyzer-481511-b0&supportedpurview=project)
     - [Credentials Page](https://console.cloud.google.com/auth/clients?project=infra-analyzer-481511-b0&supportedpurview=project)
2. Create a new project
3. Enable Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 7. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure consent screen if prompted
4. Application type: "Desktop app"
5. Download the credentials JSON file
6. Rename it to `gmail-api-credentials.json`
7. Place it in the `credentials/` directory (create the folder if it doesn't exist)

**File structure should be:**

```
gmail_processor/
└── credentials
    └── gmail-api-credentials.json  ← Place here
```

## Running the Script

### First Run (Authentication)

```bash
poetry run python main.py --start-date 2024-01-01 --end-date 2024-12-31 --label INBOX
```

- A browser window will open for authentication
- Grant permissions to access Gmail (read-only)
- A `token.json` file will be created automatically in `credentials/`

### Subsequent Runs

```bash
poetry run python main.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD --label INBOX
```

**Parameters:**

- `--start-date`: Start date in YYYY-MM-DD format
- `--end-date`: End date in YYYY-MM-DD format
- `--label`: Gmail label to filter (e.g., INBOX, SENT, custom labels)

## Troubleshooting

### Poetry not found after installation

- Restart your terminal
- Or add to PATH: `C:\Users\<USERNAME>\AppData\Roaming\Python\Scripts`

### Python version mismatch

```bash
poetry env use <path-to-python-3.11+>
poetry install
```

### FutureWarning about Python version

- Install Python 3.11 or newer
- Reconfigure Poetry environment
- Reinstall dependencies

### credentials.json not found

- Ensure the file is in `credentials/`
- Check filename is exactly `gmail-api-credentials.json`

### OAuth authentication fails

- Delete `credentials/token.json` and try again
- Check OAuth consent screen configuration
- Verify redirect URIs in Google Cloud Console
