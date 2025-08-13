from fastapi import APIRouter, Query, HTTPException
from typing import List
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from main_orchestrator import Orchestrator

router = APIRouter(
    prefix="/compare",
    tags=["comparison"],
)

@router.get("/")
def compare_stocks(
    tickers: str = Query(..., description="Comma-separated list of stock tickers."),
    start_date: str = "2023-01-01",
    end_date: str = "2023-12-31"
):
    """
    Runs analysis on multiple stocks and returns a comparative summary.
    """
    try:
        ticker_list = [t.strip() for t in tickers.split(",") if t.strip()]
        results = []
        for ticker in ticker_list:
            orch = Orchestrator(ticker, start_date, end_date)
            result = orch.execute()
            if result:
                results.append(result)
        if not results:
            raise HTTPException(status_code=404, detail="Could not produce analysis for the given tickers.")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
