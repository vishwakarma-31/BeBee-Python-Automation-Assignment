# BeBee Python Automation

A command-line tool built in Python that handles automated account signups, logins, and parallel batch processing for BeBee using `requests` and `ThreadPoolExecutor`.

## Features
- **Single Account Login**: Authenticates an account and verifies the session.
- **Account Signup**: Supports automated account creation and handles email verification via a prompt token.
- **Parallel Batch Processing**: Reads accounts from an input CSV, processes multiple logins concurrently, and writes the results to an output CSV safely using thread locks.
- **Proxy Support**: Connect through proxies for single and batch operations.

## Requirements
- Python 3.7+
- `requests` library

```bash
pip install requests
```

## Usage

This project uses `argparse` to handle different execution modes via `main.py`.

### 1. Single Login
Logs into a single account and confirms session creation.
```bash
python main.py login --email your_email@example.com --password "YourPassword123!"
```
*(Optional: Add `--proxy http://user:pass@host:port` to route through a proxy).*

### 2. Single Signup
Creates a new account. Since email verification is required, you can pass the `--prompt-token` flag to pause execution and manually input the verification link from your inbox.
```bash
python main.py signup --email your_email@example.com --password "YourPassword123!" --prompt-token
```
*(Note: If the live API endpoint for email signup is disabled, this command will output the server's rejection status code).*

### 3. Batch Login (Parallel Processing)
Reads accounts from a CSV file, attempts to log them in concurrently, and logs the success/failure status to an output CSV.

**Input CSV Format (`accounts.csv`)**:
```csv
email,password
test1@example.com,Pass1!
test2@example.com,Pass2!
```

**Run Command**:
```bash
python main.py batch --input accounts.csv --output results.csv --workers 3
```
- `--workers 3` configures the script to process 3 accounts concurrently. 
- You can also pass `--proxy-file proxies.txt` to round-robin through a list of proxies.

## Documentation
For deeper technical insights into how this tool operates, please refer to:
- `WORKFLOW.md`: Detailed breakdown of the HTTP sequences, cookies, and tokens.
- `ARCHITECTURE.md`: Overview of the core folder structure and concurrency design.
- `NOTES.md`: Known limitations, assumptions, and future improvements.