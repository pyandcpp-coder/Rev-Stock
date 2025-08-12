# file: core/data_provider.py
import pandas as pd
import yfinance as yf

class DataProvider:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.df = None

    def fetch_data(self):
        print(f"Fetching data for {self.ticker}...")
        self.df = yf.download(self.ticker, start=self.start_date, end=self.end_date)
        
        if self.df.empty:
            print(f"No data found for {self.ticker}, please check the ticker symbol.")
            return False
        
        if len(self.df.columns.levels) > 1:
            self.df.columns = self.df.columns.droplevel(1)
        self.df = self.df.reset_index()
        print("Data fetched successfully.")
        return True

    def get_data(self):
        return self.df.copy()