import os
import json
import time
import random
import datetime
import logging
import requests
from datetime import timedelta
from zoneinfo import ZoneInfo  # Python 3.9+

# --- Configuration from Environment Variables ---

TARGET_URL = os.getenv("TARGET_URL", "https://default-url.com")

cookies_env = os.getenv("COOKIES", "{}")
try:
    COOKIES = json.loads(cookies_env)
except json.JSONDecodeError as e:
    logging.error(f"Error decoding COOKIES environment variable: {e}")
    COOKIES = {}

TIME_WINDOW_START = int(os.getenv("TIME_WINDOW_START", 8))  # default: 08:00 AM
TIME_WINDOW_END = int(os.getenv("TIME_WINDOW_END", 22))  # default: 10:00 PM

# Optional timezone configuration; default to UTC if not provided.
TIMEZONE = os.getenv("TIMEZONE", "UTC")
tz = ZoneInfo(TIMEZONE)

USER_AGENT = os.getenv("USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")

headers = {"User-Agent": USER_AGENT}
EXECUTE_IN_5_SECONDS = os.getenv("EXECUTE_IN_5_SECONDS", "").lower() == "true"
SHOW_RESULT = os.getenv("SHOW_RESULT", "").lower() == "true"

# --- Custom Logging Formatter ---
class TZFormatter(logging.Formatter):
    """
    Custom logging formatter that formats the timestamp in the configured timezone.
    """
    def __init__(self, fmt=None, datefmt=None, tz=None):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.tz = tz

    def formatTime(self, record, datefmt=None):
        dt = datetime.datetime.fromtimestamp(record.created, self.tz)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.isoformat()
        return s

# Configure logging to use the custom formatter
log_format = "%(asctime)s - %(message)s"
log_datefmt = "%Y-%m-%d %H:%M:%S %Z"
handler = logging.StreamHandler()
handler.setFormatter(TZFormatter(fmt=log_format, datefmt=log_datefmt, tz=tz))
logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)

# --- Setup a persistent session for HTTP requests ---
session = requests.Session()
session.headers.update(headers)

# --- Functions ---

def get_now():
    """
    Returns the current time in the configured timezone.
    """
    return datetime.datetime.now(tz)

def get_random_time_today():
    """
    Calculates a random target datetime between the start and end of the daily window (TIME_WINDOW_START to TIME_WINDOW_END)
    in the configured timezone. If current time is outside today's window, computes for the next day.
    In debug mode (EXECUTE_IN_5_SECONDS), returns now + 5 seconds.
    """
    now = get_now()

    if EXECUTE_IN_5_SECONDS:
        return now + timedelta(seconds=5)

    start_dt = now.replace(hour=TIME_WINDOW_START, minute=0, second=0, microsecond=0)
    end_dt = now.replace(hour=TIME_WINDOW_END, minute=0, second=0, microsecond=0)

    if now >= end_dt:
        start_dt += timedelta(days=1)
        end_dt += timedelta(days=1)
    elif now > start_dt:
        start_dt = now + timedelta(seconds=10)

    window_seconds = int((end_dt - start_dt).total_seconds())
    if window_seconds <= 0:
        raise ValueError(f"Invalid time window computed: start_dt={start_dt} end_dt={end_dt}")

    random_offset = random.randint(0, window_seconds)
    target_time = start_dt + timedelta(seconds=random_offset)
    return target_time

def wait_until(target_time):
    """
    Sleeps until the target time is reached.
    """
    now = get_now()
    sleep_seconds = (target_time - now).total_seconds()
    if sleep_seconds > 0:
        logging.info(f"Waiting until {target_time.isoformat()}. Sleeping for {int(sleep_seconds)} seconds.")
        time.sleep(sleep_seconds)
    else:
        logging.info(f"Target time {target_time.isoformat()} has already passed. Running action immediately.")

def connect_using_browser():
    """
    Makes a GET request to TARGET_URL using the persistent session with provided cookies.
    Logs the HTTP status code and optionally the beginning of the response content.
    """
    try:
        response = session.get(TARGET_URL, cookies=COOKIES, timeout=10)
        logging.info(f"Connected to {TARGET_URL} - Status Code: {response.status_code}")
        if SHOW_RESULT:
            snippet = response.text[:10000]
            logging.info("Response Content (first 10000 characters):")
            logging.info(snippet)
    except Exception as e:
        logging.error(f"Error connecting to {TARGET_URL}: {e}")

def daily_loop():
    """
    Runs the daily loop:
    - Schedules a connection based on a random time within the daily window.
    - Waits for the target time and then performs the HTTP request.
    - Waits until the next cycle (next day's 00:01 in the configured timezone) before repeating.
    """
    while True:
        now = get_now()
        logging.info(f"New cycle started at {now.isoformat()}.")

        target_time = get_random_time_today()
        logging.info(f"Scheduled target time: {target_time.isoformat()}.")
        wait_until(target_time)
        connect_using_browser()

        tomorrow = now + timedelta(days=1)
        midnight = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 1, tzinfo=tz)
        logging.info(f"Waiting until next cycle at {midnight.isoformat()}.")
        wait_until(midnight)

# --- Main Execution ---
if __name__ == "__main__":
    try:
        daily_loop()
    except KeyboardInterrupt:
        logging.info("Shutdown requested by user. Exiting gracefully.")
    except Exception as ex:
        logging.error(f"An unexpected error occurred: {ex}")
