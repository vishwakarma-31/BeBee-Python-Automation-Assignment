# Architecture Note

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

I didn't want to overcomplicate things with too many extra files. The `requests` library handles the session cookies automatically, which is awesome. For the batch processing, `ThreadPoolExecutor` made it really easy to run things in parallel without having to write crazy manual threading code. I also made sure every thread gets its own `requests.Session()` because sharing a single session across threads usually causes weird bugs.

For error handling, instead of making big complicated custom error classes, I just used a `status` string in the dictionary returned by the functions (like `network_error` or `invalid_credentials`). This made it really easy to see why something failed and log it out directly to the console.
