from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import pickle
import os
import re

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "OK", "message": "News Sentiment API is running."}

@app.get("/companies")
def list_companies():
    """Get the list of companies available."""
    try:
        df = pd.read_csv('data/company_list.csv')
        companies = df['Company'].dropna().tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read company list: {e}")
    return {"companies": companies}

@app.get("/report/{company_name}")
def get_report(company_name: str):
    """Get the sentiment analysis report for a given company."""
    filename = re.sub(r'\W+', '_', company_name.lower())
    file_path = os.path.join('data', 'output', f"{filename}.pkl")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found for the specified company.")
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading report: {e}")
    return data

@app.get("/tts/{company_name}")
def get_tts(company_name: str):
    """Get Hindi Text-to-Speech audio for the overall sentiment of the company."""
    filename_base = re.sub(r'\W+', '_', company_name.lower())
    pkl_path = os.path.join('data', 'output', f"{filename_base}.pkl")
    if not os.path.exists(pkl_path):
        raise HTTPException(status_code=404, detail="No analysis available for the specified company.")
    mp3_path = os.path.join('data', 'output', f"{filename_base}_overall_sentiment_hi.mp3")
    # Generate the audio if it doesn't exist yet
    if not os.path.exists(mp3_path):
        try:
            with open(pkl_path, 'rb') as f:
                data = pickle.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading report: {e}")
        final_text = data.get("Final Sentiment Analysis")
        if not final_text:
            raise HTTPException(status_code=500, detail="No sentiment summary available for TTS.")
        from utils.text_to_speech import text_to_speech_hindi
        result = text_to_speech_hindi(final_text, mp3_path)
        if not result:
            raise HTTPException(status_code=500, detail="TTS conversion failed.")
    # Return the MP3 file as response
    return FileResponse(mp3_path, media_type="audio/mpeg", filename=f"{filename_base}_sentiment.mp3")
