import csv
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle
import os

from core.session import build_session, warm_up_session
from core.login import run_login

# keep threads from writing over each other
csv_lock = threading.Lock()

def write_result(path, email, password, status):
    with csv_lock:
        file_exists = os.path.exists(path)
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["email", "password", "success_status"])
            writer.writerow([email, password, status])

def run_single_job(account, proxy, output_csv):
    email = account["email"]
    password = account["password"]
    logging.info("Starting job for %s", email)

    try:
        session = build_session(proxy)
        if not warm_up_session(session):
            write_result(output_csv, email, password, "network_error")
            logging.info("Finished job for %s", email)
            logging.warning("Job failed for %s -> network_error", email)
            return "network_error"
        
        result = run_login(session, email, password)
        status = result["status"] if not result["success"] else "success"
        
        write_result(output_csv, email, password, status)
        
        logging.info("Finished job for %s", email)
        if status == "success":
            logging.info("Job succeeded for %s", email)
        else:
            logging.warning("Job failed for %s -> %s", email, status)
            
        return status

    except Exception as e:
        logging.error("Error on %s: %s", email, e)
        write_result(output_csv, email, password, "unknown_error")
        logging.info("Finished job for %s", email)
        logging.warning("Job failed for %s -> unknown_error", email)
        return "unknown_error"

def run_batch_login(input_csv, output_csv, workers=1, proxies=None):
    logging.info("Starting batch login from %s with %s workers", input_csv, workers)

    accounts = []
    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("email") and row.get("password"):
                accounts.append({
                    "email": row["email"].strip(),
                    "password": row["password"].strip()
                })

    summary = {
        "total": len(accounts),
        "succeeded": 0,
        "failed": 0,
        "magic_link": 0
    }

    proxy_iter = cycle(proxies) if proxies else None

    if workers == 1:
        for acc in accounts:
            p = next(proxy_iter) if proxy_iter else None
            status = run_single_job(acc, p, output_csv)
            if status == "success":
                summary["succeeded"] += 1
            elif status == "magic_link_sent":
                summary["magic_link"] += 1
            else:
                summary["failed"] += 1
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for acc in accounts:
                p = next(proxy_iter) if proxy_iter else None
                future = executor.submit(run_single_job, acc, p, output_csv)
                futures.append(future)

            for future in futures:
                status = future.result()
                if status == "success":
                    summary["succeeded"] += 1
                elif status == "magic_link_sent":
                    summary["magic_link"] += 1
                else:
                    summary["failed"] += 1

    return summary
