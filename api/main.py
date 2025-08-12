# file: api/main_api.py
from fastapi import FastAPI, HTTPException
import sys
import os

# Add root directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main_orchestrator import Orchestrator

# Create the FastAPI app
app = FastAPI(
    title="Stock Analysis & Prediction API",
    description="An API for fetching stock data, performing technical analysis, and running ML predictions."
)

@app.post("/analyze/{ticker}")
def analyze_stock(ticker: str, start_date: str = "2022-01-01", end_date: str = "2023-12-31"):
    """
    Runs the full analysis and ML pipeline for a given stock ticker.
    """
    try:
        orchestrator = Orchestrator(ticker, start_date, end_date)
        orchestrator.execute()
        
        if orchestrator.ml_results:
            return {
                "ticker": ticker,
                "status": "Analysis Complete",
                "ml_model_performance": orchestrator.ml_results
            }
        else:
            raise HTTPException(status_code=404, detail="Could not perform analysis. Check ticker or dates.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Stock Analysis API. Go to /docs to see the endpoints."}