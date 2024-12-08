#!/bin/bash
# Run the Python script to generate the daily report in midnight
/usr/local/bin/python3 -c "from main import generate_daily_report; generate_daily_report()"