# Notes, Assumptions, and Future Work

## Assumptions
- I assumed the format for `accounts.csv` just needs a header with `email,password`.
- I assumed that hitting `/api/auth/session` is the best way to verify if we are actually logged in, because the login POST request sometimes returned a 401 when it sent a magic link.
- I assumed `ThreadPoolExecutor` is okay to use for the parallel processing requirement.
- For signup, since I couldn't test the email part directly with an API without setting up a fake mail server, I made it so the script pauses and asks the user to paste the verification link from their email.

## Known Risks / Issues
- **Cloudflare/CAPTCHA:** BeBee seems to use CloudFront, but if they ever turn on Cloudflare bot protection, this `requests`-based script will probably get blocked pretty fast. We'd have to switch to something like Selenium or Playwright.
- **Proxy rotation:** Right now, I'm just cycling through the proxy list sequentially. If one proxy is completely dead, any account that gets assigned that proxy will just fail.
- **Email Verification:** The signup process isn't fully 100% automated right now because it requires you to manually copy/paste the email link.

## Future Improvements
- **Automate Email Verification:** I would love to use an IMAP library or a temporary email service API (like Mailosaur or 1secmail) so the script could create an inbox, sign up, wait for the email, grab the token, and verify it all automatically.
- **AsyncIO:** If we needed to run thousands of accounts at the same time, using `asyncio` and `aiohttp` would be a lot faster and use less memory than `ThreadPoolExecutor`.
- **Better Retry Logic:** Right now, if a request fails it just fails. It would be cool to add some logic that automatically retries the request 2 or 3 times if there's a timeout.