import tensorflow as tf 
import numpy as np
import time
from typing import Tuple

class SpamDetector:
    def __init__(self, model_path: str):
        self.model= tf.keras.models.load_model(model_path)
        print(f"Model loaded from {model_path}")
    
    def predict(self, text:str) -> Tuple[bool, float, float]:
        start_time=time.time()

        texts=[text]

        predictions= self.model.predict(texts, verbose=0)
        probability=1/(1+np.exp(-predictions[0][0]))

        is_spam=probability>0.5

        inference_time=time.time()-start_time

        return is_spam, probability, inference_time
    
    def batch_predict(self, texts: list) -> list:
        results=[]
        for text in texts:
            is_spam, confidence, inference_time=self.predict(text)
            results.append({
                'text':text,
                'is_spam':is_spam,
                'confidence':confidence,
                'inference_time':inference_time
            })
        return results
