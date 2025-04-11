# Use a Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and requirements.txt into the container
COPY . /app/

# Install the required Python dependencies
RUN pip install --no-cache-dir -r src/requirements.txt

# Set the default command to run the script
CMD ["python", "src/main.py"]