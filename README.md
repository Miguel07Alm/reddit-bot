# Reddit Niche Bot

This repository contains a Reddit Niche Bot that searches Reddit for specific keywords in posts and comments. It then sends email notifications and generates daily reports using OpenAI's API. The bot is designed to run continuously, checking for new content on Reddit and sending alerts.

## Features

- **Keyword Monitoring**: Monitors Reddit for posts and comments containing specific keywords.
- **Email Alerts**: Sends email notifications when new relevant content is found.
- **Daily Reports**: Generates and sends a daily report summarizing the findings.
- **Automated Scheduling**: Automatically schedules daily reports.

## Prerequisites

- Docker installed on your system. You can download and install Docker from the official [Docker website](https://www.docker.com/get-started).
- A Reddit API account to generate your `client_id`, `client_secret`, and `user_agent`.
- Gmail credentials for sending email notifications.
- OpenAI API key for generating reports.
- Python packages and environment variables stored in a `.env` file.

## Environment Variables

Before deploying, ensure you have a `.env` file in the project directory with the following variables:

```env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_reddit_user_agent
USER_EMAIL=your_email_address
USER_PASSWORD=your_email_password
USER_RECIPIENT_EMAIL=recipient_email_address
OPENAI_API_KEY=your_openai_api_key
```

## Steps to Deploy with Docker

### 1. Build the Docker Image

First, you need to build the Docker image using the `Dockerfile` in the project directory. This command will create a Docker image with the tag `reddit-niche-bot`.

```bash
docker build -t reddit-niche-bot .
```

This command does the following:
- `docker build`: Initiates the process of building a Docker image.
- `-t reddit-niche-bot`: Tags the image with the name `reddit-niche-bot`.
- `.`: Refers to the current directory, which contains the `Dockerfile`.

### 2. Run the Docker Container

After the image is built, you can run the Docker container using the following command:

```bash
docker run -d --name reddit-bot reddit-niche-bot
```

Explanation:
- `docker run`: Starts a new Docker container.
- `-d`: Runs the container in detached mode (in the background).
- `--name reddit-bot`: Assigns the name `reddit-bot` to the running container.
- `reddit-niche-bot`: The name of the Docker image that was built in the previous step.

Once the container is running, the bot will start monitoring Reddit, sending email notifications, and generating daily reports.

## Managing the Docker Container

Here are a few additional Docker commands you may find useful:

- **Check container logs**:
  ```bash
  docker logs reddit-bot
  ```

- **Stop the container**:
  ```bash
  docker stop reddit-bot
  ```

- **Remove the container**:
  ```bash
  docker rm reddit-bot
  ```

## Explanation of Key Functions

### `search_on_reddit()`
Searches Reddit comments and posts for the specified keywords and saves the results to a CSV file.

### `check_and_send()`
Checks the CSV file for new results, sends email notifications for relevant content, and tracks the content sent.

### `create_report()`
Uses OpenAI to generate a Markdown report from the collected data.

### `generate_daily_report()`
Generates and sends the daily report based on the collected data and scheduled tasks.

## Example of email
[![example-reddit-bot.png](https://i.postimg.cc/fL6zJ6xg/example-reddit-bot.png)](https://postimg.cc/1nrhd77p)
