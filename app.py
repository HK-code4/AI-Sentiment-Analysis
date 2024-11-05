import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
import requests
from bs4 import BeautifulSoup

# Environment variable for TensorFlow
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

class ReviewInput(BaseModel):
    review: str

class URLInput(BaseModel):
    url: str

@app.post("/analyze/")
async def analyze_review(input: ReviewInput):
    sentiment = sentiment_model(input.review)
    return {"sentiment": sentiment[0]["label"], "score": sentiment[0]["score"]}

@app.post("/fetch_and_analyze/")
async def fetch_and_analyze(input: URLInput):
    try:
        response = requests.get(input.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        reviews = [review.get_text() for review in soup.select(".product-review")]

        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found.")

        results = []
        for review in reviews:
            sentiment = sentiment_model(review)
            results.append({"review": review, "sentiment": sentiment[0]["label"], "score": sentiment[0]["score"]})

        return {"results": results}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


