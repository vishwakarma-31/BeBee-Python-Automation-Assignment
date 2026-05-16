# Workflow Analysis (Task 1)

Hi, this is my workflow analysis for the BeBee automation assignment. Before starting the code, I used the Chrome DevTools network tab to figure out how the login works, and I used the assignment URLs to guess the signup flow since the email signup isn't fully active right now on the real site.

## The Full Login Sequence

Here are the steps my script follows to log in a user.

| Step | Method | URL | Why I used it (Purpose) |
|------|--------|-----|--------------------------|
| 1 | GET | `https://bebee.com/auth/login?callbackUrl=%2Fin` | To open the login page and get the first cookies. |
| 2 | GET | `https://bebee.com/api/auth/providers` | It fetches the auth providers. The site needs this before generating the CSRF token. |
| 3 | GET | `https://bebee.com/api/auth/csrf` | To get the CSRF token. We can't submit the password without it. |
| 4 | POST | `https://bebee.com/api/auth/callback/credentials` | Here is where we actually send the email and password. |
| 5 | GET | `https://bebee.com/api/auth/session` | Finally, I check this URL to see if we really logged in or not. |

**Important Note for Step 4:**
I found out that the POST request sends form data, not JSON. This is what the payload looks like:
```
email=user@example.com
password=secret
redirect=false
csrfToken=<token from step 3>
callbackUrl=https://bebee.com/auth/login?callbackUrl=%2Fin
json=true
```

## The Full Signup Sequence

Since I couldn't test this with live traffic, I mapped it out based on the target URLs from the assignment.

| Step | Method | URL | Why I used it (Purpose) |
|------|--------|-----|--------------------------|
| 1 | GET | `https://bebee.com/` (or `https://bebee.com/br`) | To start the session. I noticed `/br` is for the Brazil region, so we can use either one to get our first cookies. |
| 2 | GET | `https://bebee.com/api/auth/session` | To start an empty guest session. |
| 3 | GET | `https://bebee.com/api/search/locations?q=<city>` | To search for a city and get its location ID. |
| 4 | POST | `https://bebee.com/api/users` | To create the actual account. This triggers the email to be sent to the user. |
| 5 | — | (User's Email Inbox) | This is where we wait for the email and grab the verification link. |
| 6 | POST | `https://bebee.com/api/auth/verify-email` | We submit the token from the email here to confirm the account. |
| 7 | POST | `https://bebee.com/api/upload/photo` | Optional step to upload a profile pic. |
| 8 | GET | `https://bebee.com/api/auth/session` | Check if the signup worked by seeing if our email is in the session now. |

## Important Tokens
There are two really important tokens I had to handle:
1. **CSRF Token (`csrfToken`)**: I get this from `/api/auth/csrf`. The site uses NextAuth, so it blocks the login POST request if I don't include this token in the body.
2. **Email Verification Token**: When we create an account, BeBee sends an email with a link like `https://bebee.com/api/auth/verify-email?token=<TOKEN>`. We need this token to finish signing up.

## Important Cookies
While testing in the Network tab, I noticed the site needs standard cookies or it blocks the bot. The most important one is:
* `__Host-next-auth.csrf-token`: This gets set during Step 1 and Step 3. It's needed for security so the server knows the CSRF token in the body matches the cookie.
* Also `_ga` and `_geo` for analytics, which just get set automatically on the home page.

## Where Email Verification Happens
Email verification happens exactly at **Step 5 and Step 6** of the signup flow. 
First, we have to extract the token from the email (Step 5), and then we send a POST request with that token to the `/api/auth/verify-email` URL (Step 6) to actually verify the account.

## Which Step Determines Success?
I figured out that we **cannot** just look at the status code of the login POST request (Step 4). Sometimes the site returns a 401 but says "MAGIC_LINK_SENT" if the account was made with Google. 
Because of this, **the step that determines success is always the final `GET /api/auth/session` step.** 
If the response contains `{"user": {"email": "our_email@example.com"}}`, then we know 100% that the login or signup was successful.
