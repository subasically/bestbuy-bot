# Use an official Python image as a base
FROM python:3.9-slim

# Install Firefox and required libraries
RUN apt-get update && \
    apt-get install -y firefox-esr wget libgtk-3-0 libdbus-glib-1-2 libxt6 libnss3 libasound2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . /app

# Set environment variable to ensure headless execution
ENV DISPLAY=:99

# Run your bot
CMD ["python", "bestbuy.py"]