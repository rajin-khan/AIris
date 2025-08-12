# llm_integrations.py
import os
from groq import Groq
from typing import List
from dotenv import load_dotenv

load_dotenv()

try:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file.")
    groq_client = Groq(api_key=api_key)
    print("Groq client initialized successfully.")
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    groq_client = None

def get_llm_response(descriptions: List[str], system_prompt: str, model_name: str = "openai/gpt-oss-120b") -> str:
    """
    Sends a list of descriptions and a system prompt to the Groq API.
    """
    if not groq_client:
        return "Error: Groq client is not configured."

    prompt_content = ". ".join(descriptions)

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_content},
            ],
            model=model_name,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred with the Groq API: {e}")
        return f"Error communicating with LLM: {e}"