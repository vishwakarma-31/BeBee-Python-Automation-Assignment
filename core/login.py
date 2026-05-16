import logging
import requests

def run_login(session, email, password):
    # This is the main function to log in
    result = {
        "email": email,
        "password": password,
        "success": False,
        "status": "unknown_error",
        "error": None
    }

    try:
        logging.info("Trying to login %s", email)

        # Step 1: visit login page
        try:
            session.get("https://bebee.com/auth/login?callbackUrl=%2Fin", timeout=30)
        except Exception as e:
            result["status"] = "network_error"
            result["error"] = str(e)
            return result

        # Step 2: fetch providers
        try:
            session.get("https://bebee.com/api/auth/providers", timeout=30)
        except Exception as e:
            result["status"] = "network_error"
            result["error"] = "Failed to fetch providers: %s" % e
            return result

        # Step 3: fetch csrf token
        csrf_token = None
        try:
            resp = session.get("https://bebee.com/api/auth/csrf", timeout=30)
            data = resp.json()
            csrf_token = data.get("csrfToken")
        except Exception as e:
            result["status"] = "network_error"
            result["error"] = "Could not get CSRF token"
            return result

        if not csrf_token:
            result["status"] = "parse_error"
            result["error"] = "No CSRF token in response"
            return result

        # Step 4: submit credentials
        payload = {
            "email": email,
            "password": password,
            "redirect": "false",
            "csrfToken": csrf_token,
            "callbackUrl": "https://bebee.com/auth/login?callbackUrl=%2Fin",
            "json": "true"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://bebee.com",
            "Referer": "https://bebee.com/auth/login?callbackUrl=%2Fin"
        }

        try:
            post_resp = session.post(
                "https://bebee.com/api/auth/callback/credentials",
                data=payload,
                headers=headers,
                timeout=30
            )
            body_text = post_resp.text
        except Exception as e:
            result["status"] = "network_error"
            result["error"] = str(e)
            return result

        # Sometimes BeBee sends a magic link if the account is Google OAuth
        if post_resp.status_code == 401 and "MAGIC_LINK_SENT" in body_text:
            result["status"] = "magic_link_sent"
            result["error"] = "Account uses Google Auth, sent a magic link instead."
            return result

        # Step 5: Check if it actually worked
        try:
            check_resp = session.get("https://bebee.com/api/auth/session", timeout=30)
            user_data = check_resp.json().get("user", {})
            if user_data.get("email", "").lower() == email.lower():
                result["success"] = True
                result["status"] = "success"
                logging.info("Successfully logged in %s", email)
            else:
                result["status"] = "invalid_credentials"
                result["error"] = "Session check failed. Wrong password."
        except Exception as e:
            result["status"] = "network_error"
            result["error"] = "Failed to verify session."

    except Exception as e:
        result["status"] = "unknown_error"
        result["error"] = str(e)

    return result
