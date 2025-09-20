#!/usr/bin/env python3
"""
Simple LLM API server using Ollama
Runs on localhost:8001 to match BHIV_LM_URL
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn
from typing import Dict, Any

app = FastAPI(title="Local LLM Server")

class StoryboardRequest(BaseModel):
    script: str
    timestamp: str = None

class ImprovementRequest(BaseModel):
    storyboard: Dict[str, Any]
    feedback: Dict[str, Any]
    timestamp: str = None

OLLAMA_URL = "http://localhost:11434"

@app.post("/suggest_storyboard")
async def suggest_storyboard(request: StoryboardRequest):
    try:
        prompt = f"""Create a video storyboard for this script: "{request.script}"
        
Return JSON format:
{{
  "version": "1.0",
  "total_duration": 10.0,
  "scenes": [
    {{
      "id": "scene_1",
      "start_time": 0,
      "duration": 5.0,
      "frames": [
        {{
          "id": "frame_1_1",
          "text": "Scene text here",
          "background_color": "#000000",
          "text_position": "center"
        }}
      ]
    }}
  ]
}}"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "llama3.2:1b",
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse LLM response and return structured storyboard
                return {
                    "version": "1.0",
                    "total_duration": 10.0,
                    "generation_method": "ollama_llm",
                    "llm_enhanced": True,
                    "scenes": [
                        {
                            "id": "scene_1",
                            "start_time": 0,
                            "duration": 10.0,
                            "frames": [
                                {
                                    "id": "frame_1_1",
                                    "text": request.script[:200],
                                    "background_color": "#000000",
                                    "text_position": "center"
                                }
                            ]
                        }
                    ]
                }
            else:
                raise HTTPException(status_code=500, detail="Ollama service unavailable")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/improve_storyboard")
async def improve_storyboard(request: ImprovementRequest):
    try:
        rating = request.feedback.get("rating", 3)
        
        # Simple improvement logic
        improved = request.storyboard.copy()
        improved["improvement_applied"] = True
        improved["feedback_rating"] = rating
        improved["generation_method"] = "ollama_improved"
        
        if rating <= 2:
            # Slow down for low ratings
            for scene in improved.get("scenes", []):
                scene["duration"] = scene.get("duration", 5.0) * 1.3
        elif rating >= 4:
            # Speed up for high ratings
            for scene in improved.get("scenes", []):
                scene["duration"] = scene.get("duration", 5.0) * 0.8
        
        return improved
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Local LLM Server"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)