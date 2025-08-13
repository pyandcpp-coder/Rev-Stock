# file: api/main_api.py
from fastapi import FastAPI, HTTPException
import sys
import os
from pydantic import BaseModel
from typing import Dict,List,Optional
import logging
import pandas as pd
import numpy as np
from api.routers import users

## setting up the logger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add root directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main_orchestrator import Orchestrator


class TimeSeriesDataPoint(BaseModel):
    """ Defines the structure for a single row of chart data"""
    Date: str
    Open: float
    High : float
    Low : float
    Close : float
    SMA_50: Optional[float] = None
    SMA_200: Optional[float] = None
    MACD: Optional[float] = None
    MACD_Signal: Optional[float] = None
    RSI: Optional[float] = None

class AnalysisResult(BaseModel):
    """ the main response model for the /analyze endpoint"""
    ticker :str
    model_performance : Dict
    timeseries_data : List[TimeSeriesDataPoint]

app = FastAPI(titile="Stock Analysis & Prediction API",
              description='api to run analysis and retrun data for charting')
app.include_router(users.router)
@app.post("/analyze/{ticker}",response_model=AnalysisResult)
def analyze_stock(ticker:str,start_date:str="2023-01-01",end_date:str="2024-12-31"):
    """Runs the full analysis pipeline and returns the resutls and time series data"""
    try:
        orchestrator = Orchestrator(ticker,start_date,end_date)
        if not orchestrator.execute():
            raise HTTPException(status_code=404,detail='Could not perform analysis, check ticker or dates.')
        
        # -- prepraring dframe for json conv
        df = orchestrator.final_df
        chart_columns = [
                'Date', 'Open', 'High', 'Low', 'Close', 
                'SMA_50', 'SMA_200', 'MACD', 'MACD_Signal', 'RSI'
        ]
        chart_df = df[chart_columns].copy()

        chart_df['Date'] = chart_df['Date'].dt.strftime('%Y-%m-%d')

        chart_df.replace({pd.NA:None,np.nan:None},inplace=True)
        timeseries_data = chart_df.to_dict(orient='records')
        #now returing the pydantic model object
        return AnalysisResult(
            ticker=ticker,
            model_performance=orchestrator.ml_results,
            timeseries_data=timeseries_data
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred for ticker {ticker}: {e}", exc_info=True)
        # Return a generic error message to the client
        raise HTTPException(status_code=500, detail=f"An internal server error occurred.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Stock Analysis API. Go to /docs to see the endpoints."}




        
