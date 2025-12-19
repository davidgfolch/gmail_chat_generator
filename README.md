# Gmail chat generator

This script uses the Gmail API to fetch messages in data range and from a specific gmail label (folder) & generate markdown files containing chronological chat like conversations for each date range & label.

## Setup

Please refer to [INSTALL.md](INSTALL.md) for detailed installation, prerequisites, and configuration instructions.

## Filter parameters

To see the available parameters execute:

```shell
poetry run python main.py --help
```

Examples:

```shell
poetry run python main.py --start-date 2025-12-16 --label "INBOX/your-gmail-label"
# or
poetry run python main.py --start-date 2025-12-16 --end-date 2025-12-17 --label "INBOX/your-gmail-label"

# Automation mode
# To run tasks defined in data/*.txt files:
poetry run python main.py
```

## Project Structure

```
gmail_processor/
├── main.py                  # Main script
├── credentials/
│   ├── gmail-api-credentials.json # OAuth credentials (not tracked)
│   └── token.json           # Generated token (not tracked)
├── data/                    # Data files to automate INBOX/label date ranges
├── api-response/            # Gmail API response cache
├── md/                      # Generated markdown reports
├── pyproject.toml           # Poetry configuration
├── poetry.lock              # Locked dependencies
└── INSTALL.md               # This file
```

## Automation mode

To run tasks defined in data/\*.txt files:

```shell
poetry run python main.py
```

The content of the data/\*.txt files should be in the following format:

```shell
INBOX/your-gmail-label
2025-12-16 2025-12-17 Comment (optional) that will be added to the markdown file name & report
```

Note: you can use spaces in comment.
