import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY was not found. "
        "Please add it to your .env file."
    )


client = Groq(api_key=API_KEY)

# We will keep the model name in one place so it is easy to change.
MODEL_NAME = "llama-3.1-8b-instant"


def generate_response(
    prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 700,
) -> str:

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,

            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],

            temperature=temperature,
            max_tokens=max_tokens,
        )

        answer = response.choices[0].message.content

        if not answer:
            return "The model returned an empty response."

        return answer.strip()

    except Exception as error:
        raise RuntimeError(
            f"LLM request failed: {error}"
        )