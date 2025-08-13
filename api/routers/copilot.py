from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from core.financial_copilot import FinancialCopilot

router = APIRouter(
    prefix="/copilot",
    tags=["Financial Co-pilot"],
)

@router.post("/analyze-source")
async def analyze_source(
    source_type: str = Form(...),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Analyzes a source (pdf, url, youtube) and returns a structured financial report.
    """
    copilot = FinancialCopilot()
    
    if source_type == 'pdf' and file:
        file_content = await file.read()
        report = copilot.generate_report(source_type='pdf', source=file_content)
    elif source_type == 'url' and url:
        report = copilot.generate_report(source_type='url', source=url)
    elif source_type == 'youtube' and url:
        report = copilot.generate_report(source_type='youtube', source=url)
    else:
        raise HTTPException(status_code=400, detail="Invalid source type or missing required data.")

    if "error" in report:
        raise HTTPException(status_code=500, detail=report["error"])
        
    return report