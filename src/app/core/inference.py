import requests
import asyncio
from typing import List, Dict, Any
from app.infisical.infisical import BASETEN_API_KEY
from loguru import logger

class Baseten:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.base_url = f"https://model-{model_id}.api.baseten.co/environments/production/predict"
        self.headers = {"Authorization": f"Api-Key {BASETEN_API_KEY.secretValue}"}
    
    async def embed(self, text: str, model_name: str) -> List[float]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._make_request,
            payload = {
                "input": text,
                "model": model_name,
                "encoding_format": "float"
            }
        )
        logger.info(f"RESULT {result}")
        
        return result
    
    def _make_request(self, payload: Dict[str, Any]) -> List[float]:
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.error(f"Unexpected response format: {result}")
            raise ValueError(f"Could not extract embedding from response")
        except Exception as e:
            logger.error(f"Error processing Baseten response: {str(e)}")
            raise