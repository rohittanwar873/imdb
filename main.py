from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

@app.get("/get_direct_image")
def get_direct_image(imdb_url: str = Query(..., description="IMDb media viewer URL")):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(imdb_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Failed to fetch page: {e}"})

    soup = BeautifulSoup(response.text, 'html.parser')

    # Try to locate the full-size image from OpenGraph or other meta
    meta = soup.find("meta", property="og:image")
    if meta and meta.get("content"):
        return {"direct_image_url": meta["content"]}

    # Fallback to regex (not usually needed but extra check)
    match = re.search(r'https://m.media-amazon.com/images/.*?\.(jpg|png|webp)', response.text)
    if match:
        return {"direct_image_url": match.group(0)}

    return JSONResponse(status_code=404, content={"error": "Image not found in provided URL."})
