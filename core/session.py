import requests
import logging

def build_session(proxy=None, timeout=30):
    # Just setup a basic session with headers so we don't look like a bot
    session = requests.Session()
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty"
    })

    if proxy:
        session.proxies = {"http": proxy, "https": proxy}
        logging.info(f"Using proxy: {proxy}")

    session.default_timeout = timeout
    return session

def warm_up_session(session):
    # Make a first request to get the initial tracking cookies
    try:
        resp = session.get("https://bebee.com/", timeout=session.default_timeout)
        resp.raise_for_status()
        logging.debug(f"Warm up worked. Cookies: {session.cookies.keys()}")
        return True
    except Exception as e:
        logging.error(f"Could not warm up session: {e}")
        return False
