FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY . .

COPY .env .env

RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Copy and setup the cronjob file
COPY cronjob /etc/cron.d/reddit-bot-cron
RUN chmod 0644 /etc/cron.d/reddit-bot-cron
RUN chmod +x /app/generate_report.sh

# Create the log file
RUN touch /var/log/cron.log && chmod 0666 /var/log/cron.log

# Install the crontab
RUN crontab /etc/cron.d/reddit-bot-cron

# Start both cron and the main application
CMD ["sh", "-c", "cron && python3 main.py"]
