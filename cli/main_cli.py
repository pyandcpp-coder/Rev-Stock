# file: cli/main_cli.py
import argparse
from datetime import datetime
import sys
import os

# This line allows the script to import modules from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_orchestrator import Orchestrator

def main():
    parser = argparse.ArgumentParser(description="Stock Analysis and Prediction Tool")
    parser.add_argument('--ticker', type=str, default='NVDA', help='Stock ticker symbol')
    parser.add_argument('--start', type=str, default='2022-01-01', help='Start date YYYY-MM-DD')
    parser.add_argument('--end', type=str, default=datetime.now().strftime('%Y-%m-%d'), help='End date YYYY-MM-DD')
    args = parser.parse_args()

    orchestrator = Orchestrator(
        ticker=args.ticker,
        start_date=args.start,
        end_date=args.end
    )
    orchestrator.execute()

if __name__ == "__main__":
    main()