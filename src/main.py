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

# Parse the cookies provided as a JSON string.
cookies_env = os.getenv("COOKIES", "{}")
try:
    COOKIES = json.loads(cookies_env)
except json.JSONDecodeError as e:
    logging.error(f"Error decoding COOKIES environment variable: {e}")
    COOKIES = {}

# Daily time window (24-hour format)
TIME_WINDOW_START = int(os.getenv("TIME_WINDOW_START", 8))  # Default: 08:00 AM
TIME_WINDOW_END = int(os.getenv("TIME_WINDOW_END", 22))  # Default: 10:00 PM

# Optional timezone configuration; default is UTC.
TIMEZONE = os.getenv("TIMEZONE", "UTC")
tz = ZoneInfo(TIMEZONE)

USER_AGENT = os.getenv("USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")

headers = {"User-Agent": USER_AGENT}

# Debug flag to execute in 5 seconds
EXECUTE_IN_5_SECONDS = os.getenv("EXECUTE_IN_5_SECONDS", "").lower() == "true"
SHOW_RESULT = os.getenv("SHOW_RESULT", "").lower() == "true"

# Configure basic logging without timestamp (we add our own timestamp)
logging.basicConfig(level=logging.INFO, format="%(message)s")

# --- Custom Logging Functions ---
def get_now():
    """
    Returns the current time in the configured timezone.
    """
    return datetime.datetime.now(tz)

def log_info(message):
    """
    Logs an informational message prefixed by the current timestamp in the configured timezone.
    """
    now = get_now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    logging.info(f"{timestamp} - {message}")

def log_error(message):
    """
    Logs an error message prefixed by the current timestamp in the configured timezone.
    """
    now = get_now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    logging.error(f"{timestamp} - {message}")

# --- Setup a persistent session for HTTP requests ---
session = requests.Session()
session.headers.update(headers)

# --- Functions ---

def get_random_time_today():
    """
    Calculates a random target datetime between the start and end of the daily window (TIME_WINDOW_START to TIME_WINDOW_END)
    in the configured timezone. If the current time is outside today's window, computes for the next day.
    In debug mode (EXECUTE_IN_5_SECONDS), returns now + 5 seconds.
    """
    now = get_now()

    if EXECUTE_IN_5_SECONDS:
        return now + timedelta(seconds=5)

    # Build timezone-aware start and end times for today.
    start_dt = now.replace(hour=TIME_WINDOW_START, minute=0, second=0, microsecond=0)
    end_dt = now.replace(hour=TIME_WINDOW_END, minute=0, second=0, microsecond=0)

    # If it's already past today's end time, move the window to tomorrow.
    if now >= end_dt:
        start_dt += timedelta(days=1)
        end_dt += timedelta(days=1)
    # Otherwise, if we're within the window but past the start, delay the start time by 10 seconds.
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
        log_info(f"Waiting until {target_time.isoformat()}. Sleeping for {int(sleep_seconds)} seconds.")
        time.sleep(sleep_seconds)
    else:
        log_info(f"Target time {target_time.isoformat()} has already passed. Running action immediately.")

def connect_using_browser():
    """
    Makes a GET request to TARGET_URL using the persistent session with provided cookies.
    Logs the HTTP status code and, optionally, the beginning of the response content.
    """
    try:
        response = session.get(TARGET_URL, cookies=COOKIES, timeout=10)
        log_info(f"Connected to {TARGET_URL} - Status Code: {response.status_code}")
        if SHOW_RESULT:
            snippet = response.text[:10000]
            log_info("Response Content (first 10000 characters):")
            log_info(snippet)
    except Exception as e:
        log_error(f"Error connecting to {TARGET_URL}: {e}")

def daily_loop():
    """
    Runs the daily loop:
    - Logs the beginning of a cycle.
    - Schedules a connection based on a random time in the daily window.
    - Waits until the target time, then performs the HTTP request.
    - Waits until the next cycle (next day's 00:01 in the configured timezone) before repeating.
    """
    while True:
        now = get_now()
        log_info(f"New cycle started at {now.isoformat()}.")

        target_time = get_random_time_today()
        log_info(f"Scheduled target time: {target_time.isoformat()}.")
        wait_until(target_time)
        connect_using_browser()

        # Calculate the next cycle start: next day at 00:01 (timezone-aware)
        tomorrow = now + timedelta(days=1)
        midnight = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 1, tzinfo=tz)
        log_info(f"Waiting until next cycle at {midnight.isoformat()}.")
        wait_until(midnight)

# --- Main Execution ---
if __name__ == "__main__":
    try:
        daily_loop()
    except KeyboardInterrupt:
        log_info("Shutdown requested by user. Exiting gracefully.")
    except Exception as ex:
        log_error(f"An unexpected error occurred: {ex}")
