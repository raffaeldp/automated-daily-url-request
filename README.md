# automated-daily-url-request

This repository contains a Python script that automates the process of sending a daily HTTP request to a specified URL. The script is designed to run in a Docker container, making it easy to deploy and manage.

The script run one time per day, at a random time within a specified time window during the day.

The script can be configured to include cookies in the request, and it can also log the response for debugging purposes.

## Usage

### Build the Docker image

```bash
docker build -t automated-daily-url-request .
```
### Run the Docker container

```bash
docker run -e TARGET_URL="https://your_url.fr/cappuccino_assassino" \
           -e COOKIES='{"cookie1": "value1", "cookie2": "value2", "session": "abc123"}' \
           -e TIME_WINDOW_START="8" \
           -e TIME_WINDOW_END="22" \
           -e EXECUTE_IN_5_SECONDS="true" \
           -e SHOW_RESULT="true" \
           -t \
           automated-daily-url-request
```

### Docker compose

```bash
services:
  automated-daily-url-request:
    image: 'ghcr.io/raffaeldp/automated-daily-url-request:latest'
    container_name: automated-daily-url-request
    environment:
      - 'TARGET_URL=https://your_url.fr/lirili-larila'
      - 'COOKIES={"cookie1": "value1", "cookie2": "value2", "coookie3": "value3"}'
      - 'TIME_WINDOW_START=8'
      - 'TIME_WINDOW_END=22'
      - 'EXECUTE_IN_5_SECONDS=true'
```

## Environment Variables
| Variable Name         | Description                                                                         |
|-----------------------|-------------------------------------------------------------------------------------|
| TARGET_URL            | The URL to be requested.                                                            |
| COOKIES               | Cookies to be sent with the request in JSON format.                                 |
| TIME_WINDOW_START     | The start of the time window (in 24 hours) during which the request should be made. |
| TIME_WINDOW_END       | The end of the time window (in 24 hours) during which the request should be made.   |
| EXECUTE_IN_5_SECONDS  | If set to "true", the script will execute the request after 5 seconds.              |
| SHOW_RESULT           | If set to "true", the script will logs the 10 000 first characters of the response. |
| TIMEZONE              | Set the timezone you want. (Europe/Paris etc...) default to UTC                     |
| USER_AGENT (optional) | The User-Agent string to be used in the request.                                    |

## Commands

```bash
# Create a new virtual environment
python3.11 -m venv .venv
```

```bash
# Activate the virtual environment
source .venv/bin/activate
```

```bash
# Install dependency
pip install package_name

pip install -r requirements.txt

pip uninstall package_name

pip list
```