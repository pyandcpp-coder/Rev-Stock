import pandas as pd 
import numpy as np 
import yfinance as yf
import matplotlib.pyplot as plt
import plotly as pl   
def get_data(ticker,start_date,end_date):
    data = yf.download(ticker,start_date,end_date)
    data = data.reset_index()
    print(f"Data for {ticker} from {start_date} to {end_date}")
    return data

if __name__ == "__main__":
    ticker = "AAPL"
    start = "2023-01-01"
    end = "2023-12-31"
    
    data = get_data(ticker,start,end)
    
    print("Data for AAPL from 2023-01-01 to 2023-12-31")
    print(data.head())
    data.to_csv(f"{ticker}_data.csv", index=False)
    print(f"Data saved to {ticker}_data.csv")
    
    