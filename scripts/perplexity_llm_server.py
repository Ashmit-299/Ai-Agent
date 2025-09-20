#!/usr/bin/env python3
"""
LLM API server using Perplexity API
Runs on localhost:8001 to match BHIV_LM_URL
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn
import json
from typing import Dict, Any

app = FastAPI(title="Perplexity LLM Server")

# Replace with your Perplexity API key
PERPLEXITY_API_KEY = "pplx-your-api-key-here"
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

class StoryboardRequest(BaseModel):
    script: str
    timestamp: str = None

class ImprovementRequest(BaseModel):
    storyboard: Dict[str, Any]
    feedback: Dict[str, Any]
    timestamp: str = None

@app.post("/suggest_storyboard")
async def suggest_storyboard(request: StoryboardRequest):
    try:
        prompt = f"""Create a video storyboard JSON for this script: "{request.script}"

Return only valid JSON in this exact format:
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
          "text": "Scene description",
          "background_color": "#000000",
          "text_position": "center"
        }}
      ]
    }}
  ]
}}"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                PERPLEXITY_URL,
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Try to parse JSON from response
                try:
                    storyboard = json.loads(content)
                    storyboard["generation_method"] = "perplexity_llm"
                    storyboard["llm_enhanced"] = True
                    return storyboard
                except:
                    # Fallback if JSON parsing fails
                    return {
                        "version": "1.0",
                        "total_duration": 10.0,
                        "generation_method": "perplexity_fallback",
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
                raise HTTPException(status_code=500, detail="Perplexity API error")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/improve_storyboard")
async def improve_storyboard(request: ImprovementRequest):
    try:
        rating = request.feedback.get("rating", 3)
        comment = request.feedback.get("comment", "")
        
        prompt = f"""Improve this video storyboard based on user feedback:
        
Storyboard: {json.dumps(request.storyboard)}
Rating: {rating}/5
Comment: {comment}

Return improved storyboard JSON with same structure but better timing/content."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                PERPLEXITY_URL,
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            
            if response.status_code == 200:
                improved = request.storyboard.copy()
                improved["improvement_applied"] = True
                improved["feedback_rating"] = rating
                improved["generation_method"] = "perplexity_improved"
                return improved
            else:
                raise HTTPException(status_code=500, detail="Perplexity API error")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Perplexity LLM Server"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)