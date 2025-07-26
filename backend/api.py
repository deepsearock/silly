from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.challenge_runner import run_challenge
from utils.prompt_score import generate_code, compute_score

app = FastAPI()

class PromptRequest(BaseModel):
    challenge_id: int
    prompt_text: str

class PromptResponse(BaseModel):
    code: str
    results: dict
    score: int

@app.post('/prompt', response_model=PromptResponse)
async def handle_prompt(req: PromptRequest):
    # Generate code via OpenAI
    code = await generate_code(req.prompt_text)
    # Run code against tests
    results = run_challenge(req.challenge_id, code)
    if results.get('error'):
        raise HTTPException(status_code=400, detail=results['error'])
    # Compute prompt-based score
    score = compute_score(req.challenge_id, req.prompt_text)
    return PromptResponse(code=code, results=results, score=score)