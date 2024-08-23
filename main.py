import praw
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import pandas as pd
import os
from openai import OpenAI
import threading
import markdown2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API configuration
reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    user_agent=os.environ.get("REDDIT_USER_AGENT"),
)

# Email configuration
smtp_server = "smtp.gmail.com"
smtp_port = 587
email_user = os.environ.get("USER_EMAIL")
email_password = os.environ.get("USER_PASSWORD")
recipient = os.environ.get("USER_RECIPIENT_EMAIL")

# File configuration
csv_file = 'results.csv'
tracking_file = 'tracking.csv'

# OpenAI API configuration
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Keywords to search for
keywords = ["airbnb", "solve this problem", "I need help for", "how to solve", "how can I do", "where I find", "what can I do", "I have a problem", "help me"]

def create_csv_if_not_exists(file_name, columns):
    """Create a CSV file with the specified columns if it does not exist."""
    if not os.path.exists(file_name):
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_name, index=False)
        print(f"Created {file_name} with columns: {columns}")

def send_email(subject, html_body):
    """Send an email with the specified subject and HTML body."""
    message = MIMEMultipart("alternative")
    message["From"] = email_user
    message["To"] = recipient
    message["Subject"] = subject
    html_part = MIMEText(html_body, "html")
    message.attach(html_part)
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.sendmail(email_user, recipient, message.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

def search_on_reddit():
    """Search for posts and comments on Reddit based on keywords and save results to CSV."""
    results = []

    for comment in reddit.subreddit('all').comments(limit=1000):
        for keyword in keywords:
            if keyword.lower() in comment.body.lower():
                results.append({
                    "date": datetime.fromtimestamp(comment.created_utc),
                    "type": "comment",
                    "subreddit": comment.subreddit.display_name,
                    "content": comment.body,
                    "url": f"https://www.reddit.com{comment.permalink}"
                })

    for submission in reddit.subreddit('all').new(limit=1000):
        for keyword in keywords:
            if keyword.lower() in submission.title.lower() or keyword.lower() in submission.selftext.lower():
                results.append({
                    "date": datetime.fromtimestamp(submission.created_utc),
                    "type": "post",
                    "subreddit": submission.subreddit.display_name,
                    "content": submission.title,
                    "url": f"https://www.reddit.com{submission.permalink}"
                })

    if results:
        df = pd.DataFrame(results)
        create_csv_if_not_exists(csv_file, df.columns)
        df.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False)
        print(f"{len(results)} new results saved.")
    else:
        print("No new results found.")

def check_and_send():
    """Check for new results and send email notifications."""
    try:
        create_csv_if_not_exists(csv_file, ["date", "type", "subreddit", "content", "url"])
        create_csv_if_not_exists(tracking_file, ["date", "type", "subreddit", "content", "url"])

        if os.path.getsize(csv_file) > 0:
            df = pd.read_csv(csv_file)
            now = datetime.now()
            last_hour = now - timedelta(hours=1)
            df['date'] = pd.to_datetime(df['date'])
            recent = df[(df['date'] >= last_hour) & (df['date'] <= now)]

            if os.path.getsize(tracking_file) > 0:
                df_tracking = pd.read_csv(tracking_file)
            else:
                df_tracking = pd.DataFrame(columns=["date", "type", "subreddit", "content", "url"])

            new_recent = recent[~recent['url'].isin(df_tracking['url'])]

            if not new_recent.empty:
                for keyword in keywords:
                    group = new_recent[new_recent['content'].str.contains(keyword, case=False)]
                    if not group.empty:
                        html_body = f"""
                        <html>
                        <body>
                            <h2>Reddit Automation found something!</h2>
                            <p><strong>Keyword:</strong> "{keyword}"</p>
                        """
                        for _, row in group.iterrows():
                            html_body += f"""
                            <p><strong>{row['type'].capitalize()}:</strong> (/r/{row['subreddit']}) (<a href="{row['url']}">Link to Reddit</a>)</p>
                            <blockquote>{row['content']}</blockquote>
                            <hr>
                            """
                        html_body += """
                            <p>Do you have comments or suggestions about Reddit Automation? Please hit reply and let me know what you think!</p>
                            <p>Want to advertise your company or product on Reddit Automation? Hit reply to get in touch.</p>
                            <p>You are receiving this email because you signed up for alerts from Reddit Automation. If you no longer wish to receive these emails, please log into your account or click to disable all future emails.</p>
                        </body>
                        </html>
                        """
                        send_email(f"Reddit Automation found something: {keyword}", html_body)

                new_recent.to_csv(tracking_file, mode='a', header=not os.path.exists(tracking_file), index=False)
                print("Data sent and saved in the tracking file.")

                df = df[~df['url'].isin(new_recent['url'])]
                df.to_csv(csv_file, mode='w', header=True, index=False)
                print("Data removed from the main CSV.")
            else:
                print("No new recent data to send.")
        else:
            print("The CSV file has no data or does not exist.")
    except Exception as e:
        print(f"Error reading or sending emails: {e}")

def create_report(data: str):
    """Create a report from the data using OpenAI."""
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert assistant in creating data reports to identify real needs of people and then come up with ideas to solve those needs for a software project. You should choose the best data that contains a real problem and use it to create the report to identify pain points, features to solve them, and ideas derived from them that may be viable. Ignore data that is not relevant or does not contain a problem or need."},
            {"role": "user", "content": f"Create a report from this data in Markdown format:\n\n{data}"}
        ],
    )
    return completion.choices[0].message['content']

def generate_daily_report():
    """Generate and send a daily report."""
    try:
        create_csv_if_not_exists(tracking_file, ["date", "type", "subreddit", "content", "url"])

        if os.path.getsize(tracking_file) > 0:
            df = pd.read_csv(tracking_file)
            df['date'] = pd.to_datetime(df['date'])
            today = datetime.now().date()
            df_today = df[df['date'].dt.date == today]

            if not df_today.empty:
                print("DF_TODAY LENGTH: ", len(df_today))
                data = df_today.to_json(orient='records', date_format='iso')
                report_md = create_report(data)

                report_html = markdown2.markdown(report_md)

                subject = f"Daily Reddit Report - {today}"
                send_email(subject, report_html)
                print(f"Report for {today} generated and sent successfully.")
            else:
                print("No data to generate the daily report.")
        else:
            print("The CSV file has no data or does not exist.")
    except Exception as e:
        print(f"Error generating the daily report: {e}")

def schedule_daily_report():
    """Schedule the daily report to be generated and sent at midnight."""
    now = datetime.now()
    midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
    seconds_until_midnight = (midnight - now).total_seconds()

    def run_and_reschedule():
        generate_daily_report()
        schedule_daily_report()

    threading.Timer(seconds_until_midnight, run_and_reschedule).start()

def main():
    """Main function to run the bot."""
    create_csv_if_not_exists(csv_file, ["date", "type", "subreddit", "content", "url"])
    create_csv_if_not_exists(tracking_file, ["date", "type", "subreddit", "content", "url"])
    
    schedule_daily_report()
    while True:
        search_on_reddit()
        check_and_send()
        print("Waiting 5 minutes before the next search...")
        time.sleep(300)

if __name__ == "__main__":
    main()
