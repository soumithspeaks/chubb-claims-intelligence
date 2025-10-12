from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from PIL import Image
import io
import json
import datetime
from pathlib import Path

app = FastAPI(title="Insurance Claims AI")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Insurance Claims AI System"}

@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # TODO: Add model prediction
        
        return {
            "status": "success",
            "message": "Image analyzed successfully",
            "data": {
                "damage_type": "pending",
                "severity": "pending",
                "cost_estimate": "pending"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)