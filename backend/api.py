from fastapi import FastAPI
from pydantic import BaseModel
from backend.main_service import generate_music_pipeline

app = FastAPI()

class MusicRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate_music(req: MusicRequest):
    return generate_music_pipeline(req.prompt)
