# BeBee Automation — Architecture

## Project Structure

```
bebee/
├── main.py                    # CLI entrypoint (argparse subcommands)
├── requirements.txt
├── core/
│   ├── session.py             # HTTP session builder + warm-up
│   ├── login.py               # Login workflow — HAR verified
│   ├── signup.py              # Signup workflow — assumed (see NOTES.md)
│   └── batch.py               # Batch processor with parallel execution
├── utils/
│   ├── logging_config.py      # Console + rotating file logging
│   └── proxy_loader.py        # Proxy file loader
├── docs/
│   ├── ARCHITECTURE.md        # This file
│   ├── WORKFLOW.md            # URL-to-step mapping, payloads, responses
│   └── NOTES.md               # Assumptions, risks, improvements
├── logs/                      # Runtime logs (auto-created)
└── data/                      # Architecture Note
```

Here is a short note on how I built this project!

## Folder Structure

I decided to keep things simple but organized. I split the code into a `core` folder for the main logic and kept `main.py` at the root as the entry point.

- `main.py`
  This is the main file you run. It uses `argparse` to handle commands like `login`, `signup`, and `batch`. It also sets up some basic logging and reads the proxy files if needed.

- `core/session.py`
  This file creates the `requests.Session`. I made sure to add headers that look exactly like a real Chrome browser on Windows. I also added a `warm_up_session` function to hit the home page first and grab the initial cookies before trying to log in.

- `core/login.py`
  This has the `run_login` function. I broke the login down into the steps I saw in the Chrome DevTools Network tab. It visits the page, gets the CSRF token, sends the POST request, and then checks `/api/auth/session` to see if it actually worked.

- `core/signup.py`
  This handles creating a new account. It sends the user details to the `/api/users` endpoint. Since BeBee requires email verification, I added a way to pause and ask the user to paste the link they got in their email so the script can extract the token and finish the process.

- `core/batch.py`
  This is for running multiple logins from a CSV. It reads the CSV, and if you specify more than 1 worker, it uses `ThreadPoolExecutor` to run them in parallel. I added a `threading.Lock()` when writing to the output CSV so the threads don't write over each other and corrupt the file.

## Why I did it this way

I didn't want to overcomplicate things with too many extra files. The `requests` library handles the session cookies automatically, which is awesome. For the batch processing, `ThreadPoolExecutor` made it really easy to run things in parallel without having to write crazy manual threading code. I also made sure every thread gets its own `requests.Session()` because sharing a single session across threads usually causes weird bugs. would corrupt rows.

### Round-robin proxy assignment
When a proxy file is provided, proxies are assigned per job using `itertools.cycle()`.
BeBee's credentials endpoint returns HTTP 200 and HTTP 401 in ways that don't
reliably indicate auth success. The definitive check is always re-fetching
`/api/auth/session` and verifying `user.email` in the response.

### Magic link is its own outcome
`MAGIC_LINK_SENT` (HTTP 401 from BeBee when account is OAuth-only) is tracked
separately in output CSV and batch summary — it's not a failure.

## Failure Type Separation

| Failure | Exception / Detection | CSV Status |
|---------|----------------------|------------|
| Proxy failure | `requests.exceptions.ProxyError` | `proxy_error` |
| Network failure | `requests.exceptions.RequestException` | `network_error` |
| Email verification failure | `EmailVerificationError` | `email_verification_error` |
| Login failure | Session check returns False | `invalid_credentials` |
| Magic link sent | 401 + MAGIC_LINK_SENT in body | `magic_link_sent` |
| Response parse failure | `ValueError` on `.json()` | `parse_error` |
| Unexpected | Catch-all `Exception` | `unknown_error` |

## Data Flow — Batch Login

```
Input CSV (email, password)
        │
        ▼
  _load_input_csv()
        │
        ▼
  [max_workers=1]          [max_workers=N]
  for loop                 ThreadPoolExecutor
        │                          │
        ▼                          ▼
  _run_one(account, proxy)   _run_one() × N (parallel)
  build_session()
  warm_up_session()
  run_login()
        │
        ▼
  _write_row()  ← protected by _csv_lock
        │
        ▼
Output CSV (email, password, success_status)
```
