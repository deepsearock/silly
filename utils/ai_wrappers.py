import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def call_llm(prompt: str) -> dict:
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512
    )
    return resp.to_dict()