# automated-daily-url-request

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
           -e USER_AGENT="Mozilla/5.0 ..." \
           -e EXECUTE_IN_5_SECONDS="true" \
           -e SHOW_RESULT="true" \
           -t \
           automated-daily-url-request
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