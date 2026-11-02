# TOSS — Usage Guide

## Requirements

- Python 3
- Ubuntu Linux or another supported Python environment
- SQLite (included with Python)

## Installation

```bash
git clone https://github.com/DRA3V50/Technical-Operations-Support-System.git
cd Technical-Operations-Support-System
python3 -m venv .venv
source .venv/bin/activate
python3 src/main.py
```

The application initializes its local SQLite database when launched.

## Available Operations

| Option | Function |
|---|---|
| 1 | Create a support request |
| 2 | List saved requests |
| 3 | Search by request ID |
| 4 | Update status or assignment |
| 5 | Close a request with resolution notes |
| 6 | View request history |
| 7 | Review records for missing information |
| 8 | Correct resolution documentation |
| 9 | View operational report |
| 10 | Export report as a text file |

## Testing

```bash
python3 -m unittest discover -s tests -v
```

## Notes

All sample requests are fictional. Local databases, generated reports, and backup files are excluded from version control.

## Web Dashboard

The project also includes a Streamlit dashboard for managing support requests.

Launch it with:

```bash
streamlit run src/dashboard.py
```
Open the local URL displayed in the terminal.

The dashboard supports:
- Creating and searching support requests
- Assigning requests to technicians
- Updating request status and priority
- Recording resolution notes
- Reviewing request history
- Viewing operational reports and charts
