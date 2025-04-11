# automated-daily-url-request

## Usage

### Build the Docker image

```bash
docker build -t automated-daily-url-request .
```
### Run the Docker container

```bash
docker run -e TARGET_URL="https://your_url.fr" \
           -e COOKIES='{"cookie1": "value1", "cookie2": "value2", "session": "abc123"}' \
           -e TIME_WINDOW_START="8" \
           -e TIME_WINDOW_END="22" \
           -e USER_AGENT="Mozilla/5.0 ..." \
           -e EXECUTE_IN_5_SECONDS="true" \
           -t \
           automated-daily-url-request
```

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