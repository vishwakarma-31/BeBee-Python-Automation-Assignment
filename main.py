import argparse
import sys
import logging
import os
import csv

from core.session import build_session, warm_up_session
from core.login import run_login
from core.batch import run_batch_login
from core.signup import run_signup, extract_verification_token

def setup_logger(level="INFO"):
    # Just a simple logger setup
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def load_proxy_file(filepath):
    # simple function to read proxies from a text file
    proxies = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                p = line.strip()
                if p:
                    proxies.append(p)
    return proxies

def do_login(args):
    logger = logging.getLogger("bebee")
    logger.info("Starting single login for %s", args.email)

    try:
        session = build_session(args.proxy)
        is_warm = warm_up_session(session)
        if not is_warm:
            print("Error: Could not reach bebee.com. Check network.")
            return 1

        result = run_login(session, args.email, args.password)

        if result["success"]:
            print(f"Success! Logged in as {args.email}")
            return 0
        else:
            print(f"Failed! {args.email} - {result.get('status')}: {result.get('error')}")
            return 1

    except Exception as e:
        print(f"Got an error: {e}")
        return 1

def do_signup(args):
    logger = logging.getLogger("bebee")
    logger.info("Starting signup for %s", args.email)

    try:
        token = args.token

        result = run_signup(
            email=args.email,
            password=args.password,
            proxy=args.proxy,
            first_name=args.first_name,
            last_name=args.last_name,
            location_city=args.city,
            verification_token=token,
            photo_path=args.photo,
            prompt_token=args.prompt_token
        )

        if result["success"]:
            print(f"Success! Signed up {args.email}")
            
            # Save it to a csv file as required by the assignment
            file_exists = os.path.isfile(args.output)
            with open(args.output, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["email", "password", "success_status"])
                writer.writerow([args.email, args.password, "success"])
            print(f"Saved to {args.output}")
            return 0
        else:
            print(f"Failed: {result.get('status')} - {result.get('error')}")
            return 1

    except Exception as e:
        print(f"Got an error: {e}")
        return 1

def do_batch(args):
    logger = logging.getLogger("bebee")
    
    proxies = None
    if args.proxy_file:
        proxies = load_proxy_file(args.proxy_file)
    elif args.proxy:
        proxies = [args.proxy]

    workers = args.workers if args.workers > 0 else 1

    try:
        summary = run_batch_login(args.input, args.output, workers, proxies)
        print("\n--- Batch Run Finished ---")
        print(f"Total: {summary['total']}")
        print(f"Success: {summary['succeeded']}")
        print(f"Magic Link: {summary['magic_link']}")
        print(f"Failed: {summary['failed']}")
        return 0
    except Exception as e:
        print(f"Batch run failed: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="BeBee Automation Script for Assignment")
    parser.add_argument("--log-level", default="INFO", help="Set logging level (INFO, DEBUG)")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Login command setup
    lp = subparsers.add_parser("login", help="Login to a single account")
    lp.add_argument("--email", required=True)
    lp.add_argument("--password", required=True)
    lp.add_argument("--proxy", default=None)

    # Signup command setup
    sp = subparsers.add_parser("signup", help="Signup a single account")
    sp.add_argument("--email", required=True)
    sp.add_argument("--password", required=True)
    sp.add_argument("--first-name", default=None)
    sp.add_argument("--last-name", default=None)
    sp.add_argument("--city", default="New York")
    sp.add_argument("--token", default=None)
    sp.add_argument("--prompt-token", action="store_true")
    sp.add_argument("--photo", default=None)
    sp.add_argument("--proxy", default=None)
    sp.add_argument("--output", default="successful_signups.csv")

    # Batch command setup
    bp = subparsers.add_parser("batch", help="Run batch logins from CSV")
    bp.add_argument("--input", required=True)
    bp.add_argument("--output", required=True)
    bp.add_argument("--workers", type=int, default=1)
    bp.add_argument("--proxy", default=None)
    bp.add_argument("--proxy-file", default=None)

    args = parser.parse_args()
    setup_logger(args.log_level)

    if args.command == "login":
        sys.exit(do_login(args))
    elif args.command == "signup":
        sys.exit(do_signup(args))
    elif args.command == "batch":
        sys.exit(do_batch(args))

if __name__ == "__main__":
    main()
