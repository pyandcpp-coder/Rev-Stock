# file: core/financial_copilot.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
import fitz  # PyMuPDF
from newspaper import Article
import subprocess
import shutil

# Configure the Gemini API
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class FinancialCopilot:
    def __init__(self):
        # Initialize the Gemini Pro 1.5 model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.text_content = ""

    def _extract_text_from_pdf(self, file_content: bytes):
        """Extracts text from PDF bytes."""
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            self.text_content = "".join(page.get_text() for page in doc)

    def _extract_text_from_url(self, url: str):
        """Extracts text from a news article URL."""
        article = Article(url)
        article.download()
        article.parse()
        self.text_content = article.text

    # def _extract_text_from_youtube(self, url: str):
    #     """Downloads and transcribes a YouTube video."""
    #     # For simplicity and speed in this example, we'll use yt-dlp to get a transcript if available.
    #     # A full Whisper implementation can be added if needed for non-captioned videos.
    #     temp_dir = "temp_youtube_transcripts"
    #     os.makedirs(temp_dir, exist_ok=True)
    #     command = [
    #         'yt-dlp', '--write-auto-sub', '--skip-download', '--sub-lang', 'en',
    #         '-o', f'{temp_dir}/%(title)s.%(ext)s', url
    #     ]
    #     try:
    #         subprocess.run(command, check=True, capture_output=True, text=True)
    #         vtt_files = [f for f in os.listdir(temp_dir) if f.endswith('.vtt')]
    #         if not vtt_files:
    #             raise RuntimeError("No subtitles found for this video.")
            
    #         with open(os.path.join(temp_dir, vtt_files[0]), 'r') as f:

    #             lines = [line.strip() for line in f if '-->' not in line and line.strip() and not line.strip().isdigit()]
    #             self.text_content = " ".join(lines)
    #     finally:
    #         shutil.rmtree(temp_dir)

    def generate_report(self, source_type: str, source: any) -> dict:
        """
        Orchestrates text extraction and report generation.
        'source' can be file bytes or a URL string.
        """
        print(f"Generating report for source type: {source_type}")
        try:
            if source_type == 'pdf':
                self._extract_text_from_pdf(source)
            elif source_type == 'url':
                self._extract_text_from_url(source)
            # elif source_type == 'youtube':
            #     self._extract_text_from_youtube(source)
            else:
                return {"error": "Unsupported source type"}
            
            if not self.text_content.strip():
                return {"error": "Could not extract any text from the source."}

            # The powerful, single-shot prompt to Gemini 1.5 Pro
            prompt = f"""
            As a world-class financial analyst, your task is to analyze the provided document and generate a structured JSON report.
            The document text is as follows:
            ---
            {self.text_content}
            ---
            Based on the text, produce a JSON object with the following schema. If a section is not applicable, use an empty array or a null value.

            {{
              "executive_summary": "A concise, professional summary of the document's key points and implications.",
              "key_financial_metrics": [
                {{"metric": "Metric Name (e.g., Revenue, EPS)", "value": "Value (e.g., $1.2B, $0.54)", "period": "Time Period (e.g., Q4 2023)"}},
                ...
              ],
              "sentiment_analysis": {{
                "overall_sentiment": "Positive/Negative/Neutral",
                "reasoning": "A brief explanation for the sentiment rating, based on the text."
              }},
              "identified_risks": [
                "A description of the first identified risk.",
                "A description of the second identified risk.",
                ...
              ],
              "notable_quotes": [
                "An exact, impactful quote from a key person mentioned in the document.",
                ...
              ]
            }}
            """
            
            response = self.model.generate_content(prompt)
            # The response from Gemini might have ```json ... ``` markers, so we clean it.
            cleaned_json_string = response.text.strip().replace('```json', '').replace('```', '')
            import json
            return json.loads(cleaned_json_string)

        except Exception as e:
            print(f"An error occurred in generate_report: {e}")
            return {"error": str(e)}