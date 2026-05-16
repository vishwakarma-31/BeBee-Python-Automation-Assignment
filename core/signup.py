import logging
import random
import string
import re

def random_name(length=7):
    # just pick some random letters for the fake name
    letters = string.ascii_lowercase
    return random.choice(string.ascii_uppercase) + ''.join(random.choices(letters, k=length-1))

def extract_verification_token(email_body):
    # Try to find the token in the email link
    match = re.search(r"token=([A-Za-z0-9\-_\.%]+)", email_body)
    if match:
        return match.group(1)
    return None

def run_signup(session, email, password, first_name=None, last_name=None, location_city="New York", verification_token=None, photo_path=None, prompt_token=False):
    # Main function to sign up a new account
    result = {
        "email": email,
        "password": password,
        "success": False,
        "status": "failed",
        "error": None
    }

    try:
        logging.info(f"Starting signup for {email}")

        # Step 2: Get empty session
        try:
            session.get("https://bebee.com/api/auth/session", timeout=30)
        except Exception as e:
            result["error"] = f"Could not get initial session: {e}"
            return result

        # Step 3: Get location ID
        location_id = None
        try:
            loc_resp = session.get("https://bebee.com/api/search/locations", params={"q": location_city}, timeout=30)
            data = loc_resp.json()
            if isinstance(data, list) and len(data) > 0:
                location_id = data[0].get("id") or data[0].get("locationId")
        except Exception as e:
            logging.warning(f"Could not get location ID for {location_city}")

        # Step 4: Create user
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
            logging.info(f"User creation API returned status: {user_resp.status_code}")
            
            if user_resp.status_code == 409:
                result["status"] = "signup_error"
                result["error"] = "Email already registered"
                return result
            elif user_resp.status_code == 404 or user_resp.status_code == 405:
                # 404/405 means BeBee has disabled the endpoint
                logging.warning("BeBee's email signup endpoint appears to be disabled currently.")
                result["status"] = "signup_error"
                result["error"] = "Endpoint disabled by server."
                return result
            elif user_resp.status_code not in [200, 201]:
                # If it's 400 Bad Request or anything else, stop here.
                result["status"] = "signup_error"
                result["error"] = f"Failed to create user. Status: {user_resp.status_code}"
                return result
                
        except Exception as e:
            result["status"] = "network_error"
            result["error"] = str(e)
            return result

        # Step 5: Wait for verification token
        if not verification_token and prompt_token:
            print(f"\nUser creation request sent for {email}.")
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

        # Step 6: Verify email
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

        # Step 7: Upload photo
        if photo_path:
            try:
                with open(photo_path, "rb") as f:
                    files = {"photo": (photo_path.split("/")[-1], f, "image/jpeg")}
                    session.post("https://bebee.com/api/upload/photo", files=files, timeout=30)
            except Exception as e:
                logging.warning(f"Failed to upload photo: {e}")

        # Step 8: Confirm it worked
        try:
            check_resp = session.get("https://bebee.com/api/auth/session", timeout=30)
            user_data = check_resp.json().get("user", {})
            if user_data.get("email", "").lower() == email.lower():
                result["success"] = True
                result["status"] = "success"
                logging.info(f"Signup successful for {email}")
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
