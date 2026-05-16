import logging
import random
import string
import re
from core.session import build_session

def random_name(length=7):
    letters = string.ascii_lowercase
    return random.choice(string.ascii_uppercase) + ''.join(random.choices(letters, k=length-1))

def extract_verification_token(email_body):
    # get the token from the email link
    match = re.search(r"token=([A-Za-z0-9\-_\.%]+)", email_body)
    if match:
        return match.group(1)
    return None

def run_signup(email, password, proxy=None, first_name=None, last_name=None, location_city="New York", verification_token=None, photo_path=None, prompt_token=False):
    result = {
        "email": email,
        "password": password,
        "success": False,
        "status": "failed",
        "error": None
    }

    try:
        logging.info("Starting signup for %s", email)
        
        session = build_session(proxy)

        # get the initial cookies
        try:
            session.get("https://bebee.com/br", timeout=30)
            session.get("https://bebee.com/api/auth/session", timeout=30)
        except Exception as e:
            result["error"] = "Could not get initial session: %s" % e
            return result

        location_id = None
        try:
            loc_resp = session.get("https://bebee.com/api/search/locations", params={"q": location_city}, timeout=30)
            data = loc_resp.json()
            if isinstance(data, list) and len(data) > 0:
                location_id = data[0].get("id") or data[0].get("locationId")
        except Exception as e:
            logging.warning("Could not get location ID for %s", location_city)

        payload = {
            "firstName": first_name or random_name(),
            "lastName": last_name or random_name(),
            "email": email,
            "password": password
        }
        if location_id:
            payload["locationId"] = str(location_id)

        try:
            user_resp = session.post("https://bebee.com/api/users", json=payload, timeout=30)
            logging.info("User creation API returned status: %s", user_resp.status_code)
            
            if user_resp.status_code == 409:
                result["status"] = "signup_error"
                result["error"] = "Email already registered"
                return result
            elif user_resp.status_code == 404 or user_resp.status_code == 405:
                # tell user if the endpoint is turned off
                logging.warning("BeBee's email signup endpoint appears to be disabled currently.")
                result["status"] = "signup_error"
                result["error"] = "Endpoint disabled by server."
                return result
            elif user_resp.status_code not in [200, 201]:
                # stop if the server rejects it
                result["status"] = "signup_error"
                result["error"] = "Failed to create user. Status: %s" % user_resp.status_code
                return result
                
        except Exception as e:
            result["status"] = "network_error"
            result["error"] = str(e)
            return result

        if not verification_token and prompt_token:
            print("\nUser creation request sent for %s." % email)
            print("Please check your email inbox and paste the full verification link below:")
            link = input("Link: ").strip()
            verification_token = extract_verification_token(link)
            if not verification_token:
                print("Could not find a valid token in that link.")
                result["status"] = "parse_error"
                result["error"] = "Invalid verification link provided."
                return result

        if not verification_token:
            result["status"] = "awaiting_verification"
            result["error"] = "We need the verification token to continue."
            return result

        try:
            ver_resp = session.post("https://bebee.com/api/auth/verify-email", json={"token": verification_token}, timeout=30)
            if ver_resp.status_code not in [200, 201, 204]:
                result["status"] = "email_verification_error"
                result["error"] = "Verification failed."
                return result
        except Exception as e:
            result["status"] = "network_error"
            result["error"] = str(e)
            return result

        if photo_path:
            try:
                with open(photo_path, "rb") as f:
                    files = {"photo": (photo_path.split("/")[-1], f, "image/jpeg")}
                    session.post("https://bebee.com/api/upload/photo", files=files, timeout=30)
            except Exception as e:
                logging.warning("Failed to upload photo: %s", e)

        # check if the signup worked
        try:
            check_resp = session.get("https://bebee.com/api/auth/session", timeout=30)
            user_data = check_resp.json().get("user", {})
            if user_data.get("email", "").lower() == email.lower():
                result["success"] = True
                result["status"] = "success"
                logging.info("Signup successful for %s", email)
            else:
                result["status"] = "failed"
                result["error"] = "Account created but session not active."
        except Exception as e:
            result["status"] = "network_error"
            result["error"] = str(e)

    except Exception as e:
        result["status"] = "unknown_error"
        result["error"] = str(e)

    return result
