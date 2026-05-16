import requests
import logging

def build_session(proxy=None, timeout=30):
    # make sure we don't look like a bot
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
        logging.info("Using proxy: %s", proxy)

    session.default_timeout = timeout
    return session

def warm_up_session(session):
    # get the first cookies before doing anything else
    try:
        resp = session.get("https://bebee.com/", timeout=session.default_timeout)
        resp.raise_for_status()
        logging.debug("Warm up worked.")
        return True
    except requests.exceptions.ProxyError as e:
        logging.error("Proxy failure during warm up: %s", e)
        return False
    except Exception as e:
        logging.error("Network error during warm up: %s", e)
        return False
