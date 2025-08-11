import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_price(df, ticker):
    """ plots the closing price over time"""
    fig = go.Figure()
    
    # adding the closing price trace
    fig.add_trace(go.Scatter(x = df.index, y= df['Close'], mode = 'lines', name = 'Close Price'))
    # updating the layout
    fig.update_layout(title=f'{ticker} S Price Analysis', xaxis_title='Date', yaxis_title='Price (USD)',template='plotly_dark')
    
    fig.show()
    
if __name__ == '__main__':
    ticker = 'AAPL'
    try: 
        df = pd.read_csv(f'{ticker}_data.csv',index_col='Date', parse_dates=True)
        print(df.head())
        print("Successfully loaded data")
        
    except FileNotFoundError:
        print(f'{ticker} data not found')
        
    except Exception as e:
        print(e)    
    
        
    

