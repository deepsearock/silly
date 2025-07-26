import openai
import os
from functools import lru_cache

# Configure API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_code(prompt_text: str) -> str:
    """
    Uses OpenAI's ChatCompletion API to generate Python code based on the user's prompt.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful coding assistant that outputs only valid Python code without additional explanation."},
            {"role": "user", "content": prompt_text}
        ],
        max_tokens=512,
        temperature=0.0,
        n=1
    )
    return response.choices[0].message.content.strip()

@lru_cache(maxsize=128)
def compute_score(challenge_id: int, prompt_text: str) -> int:
    """
    Simple heuristic: fewer words in prompt yield a higher score.
    """
    length = len(prompt_text.split())
    return max(0, 100 - length)