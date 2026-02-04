from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .models import SpamDetector
import logging

app=FastAPI(title="Spam Detection API", version="1.0.0")

# the CORS middleware
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )

try:
    spam_detector= SpamDetector("data/text_model.keras")
except Exception as e:
    logging.error(f"Failed to load model:{e}")
    spma_detector= None

class MessageRequest(BaseModel):
    text: str
    user_id: str=None

class PredictionResponse(BaseModel):
    is_spam: bool
    confidence: float
    prediction_time: float

@app.get("/")
async def root():
    return {"message": "Spam Detection API", "status":"online"}

@app.post("/predict", response_model=PredictionResponse)
async def predict_spam(request: MessageRequest):
    if spam_detector is None:
        raise HTTPException(status_code=503, detail="Model not loading")
    
    try:
        is_spam, confidence, inference_time= spam_detector.predict(request.text)
        return PredictionResponse(
            is_spam=bool(is_spam),
            confidence=float(confidence),
            prediction_time=float(inference_time)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health")
async def health_check():
    return {
        "status":"healthy" if spam_detector else "unhealthy",
        "model_loaded": spam_detector is not None
    }

@app.post("/batch_predict")
async def batch_predict(messages: list[MessageRequest]):
    results=[]
    for msg in messages:
        try:
            is_spam, confidence, _ = spam_detector.predict(msg.text)
            results.append({
                "text":msg.text[:100] + "...." if len(msg.text) > 100 else msg.text,
                "is_spam": bool(is_spam),
                "confidence":float(confidence),
                "user_id":msg.user_id
            })
        except Exception as e:
            results.append({"error":str(e), "text":msg.text})
        
    return {"results":results, "total":len(results)}