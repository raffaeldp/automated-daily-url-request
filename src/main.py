import os
import json
import time
import random
import datetime
import requests
from datetime import timedelta

# --- Configuration from Environment Variables ---
TARGET_URL = os.getenv("TARGET_URL", "https://default-url.com")

# The COOKIES environment variable should be a JSON string like:
# {"cookie1": "value1", "cookie2": "value2", "session": "abc123"}
cookies_env = os.getenv("COOKIES", "{}")
try:
    COOKIES = json.loads(cookies_env)
except json.JSONDecodeError as e:
    print(f"{datetime.datetime.now()} - Error decoding COOKIES environment variable: {e}")
    COOKIES = {}

# Optional: Configure your daily time window by setting these as environment variables.
TIME_WINDOW_START = int(os.getenv("TIME_WINDOW_START", 8))  # Default: 08:00 AM
TIME_WINDOW_END = int(os.getenv("TIME_WINDOW_END", 22))  # Default: 10:00 PM

# User-Agent string to mimic a regular browser.
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/105.0.0.0 Safari/537.36")

headers = {
    "User-Agent": USER_AGENT
}

# Check if debugging mode is enabled (execute in 5 seconds)
EXECUTE_IN_5_SECONDS = os.getenv("EXECUTE_IN_5_SECONDS", "").lower() == "true"
SHOW_RESULT = os.getenv("SHOW_RESULT", "").lower() == "true"


# --- Functions ---

def get_random_time_today():
    """
    Calculates a random time between the specified window (TIME_WINDOW_START to TIME_WINDOW_END) today.
    If the current time has passed the start time, adjust the start to now + 10 seconds.
    """
    now = datetime.datetime.now()

    # If debugging mode is enabled, set target time to now + 5 seconds
    if EXECUTE_IN_5_SECONDS:
        return now + timedelta(seconds=5)

    # Calculate today's start time
    start_dt = now.replace(hour=TIME_WINDOW_START, minute=0, second=0, microsecond=0)

    # Check if the current time has already passed the start time
    if now >= start_dt:
        start_dt = now + timedelta(seconds=10)  # Adjust the start time to now + 10 seconds

    # Calculate the end time for today's window
    end_dt = now.replace(hour=TIME_WINDOW_END, minute=0, second=0, microsecond=0)

    # If we are past today's end time, reset for the next day
    if now >= end_dt:
        start_dt += timedelta(days=1)
        end_dt += timedelta(days=1)

    # Randomly choose a time within the available window
    window_seconds = int((end_dt - start_dt).total_seconds())
    random_offset = random.randint(0, window_seconds)
    target_time = start_dt + timedelta(seconds=random_offset)

    return target_time


def wait_until(target_time):
    """
    Makes the program wait until the target time is reached.
    """
    now = datetime.datetime.now()
    sleep_seconds = (target_time - now).total_seconds()
    if sleep_seconds > 0:
        print(f"[{now}] Waiting until {target_time}. Sleeping for {int(sleep_seconds)} seconds.")
        time.sleep(sleep_seconds)
    else:
        print(f"[{now}] Target time {target_time} has already passed. Running action immediately.")


def connect_using_browser():
    """
    Makes a GET request to the TARGET_URL with the provided cookies and headers to mimic a browser connection.
    """
    try:
        response = requests.get(TARGET_URL, cookies=COOKIES, headers=headers)
        print(f"[{datetime.datetime.now()}] Connected to {TARGET_URL} - Status Code: {response.status_code}")
        if SHOW_RESULT:
            print(f"[{datetime.datetime.now()}] Response Content (first 10000 characters):")
            print(response.text[:10000])
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error connecting to {TARGET_URL}: {e}")


def daily_loop():
    """
    Runs the daily cycle: waits for a random time within the specified window, connects to the URL,
    then waits until the next day at midnight.
    """
    while True:
        now = datetime.datetime.now()
        print(f"\n[{now}] New cycle started.")

        # Get a random target time within today's window or 5 seconds for debugging
        target_time = get_random_time_today()
        print(f"[{now}] Target time today: {target_time}")

        # Wait until the target time
        wait_until(target_time)

        # Perform the connection action
        connect_using_browser()

        # Wait until tomorrow at 00:01
        tomorrow = now + timedelta(days=1)
        midnight = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 1)
        print(f"[{now}] Waiting until next cycle at {midnight}")
        wait_until(midnight)


# --- Main Execution ---
if __name__ == "__main__":
    daily_loop()
