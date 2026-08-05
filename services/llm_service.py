import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

# Loads variables from .env when running locally.
load_dotenv()


# =========================================================
# GET GROQ API KEY
# =========================================================

def get_groq_api_key():
    """
    Get the Groq API key.

    Local development:
        Reads GROQ_API_KEY from the .env file.

    Streamlit Cloud:
        Reads GROQ_API_KEY from Streamlit Secrets.
    """

    # -----------------------------------------------------
    # OPTION 1: LOCAL .ENV FILE
    # -----------------------------------------------------

    api_key = os.getenv("GROQ_API_KEY")

    if api_key:
        return api_key

    # -----------------------------------------------------
    # OPTION 2: STREAMLIT CLOUD SECRETS
    # -----------------------------------------------------

    try:
        api_key = st.secrets["GROQ_API_KEY"]

        if api_key:
            return api_key

    except (KeyError, FileNotFoundError):
        pass

    # -----------------------------------------------------
    # API KEY NOT FOUND
    # -----------------------------------------------------

    raise RuntimeError(
        "GROQ_API_KEY was not found. "
        "Add it to the .env file when running locally "
        "or add it to Streamlit Secrets when deployed."
    )


# =========================================================
# INITIALIZE GROQ CLIENT
# =========================================================

API_KEY = get_groq_api_key()

client = Groq(
    api_key=API_KEY
)


# =========================================================
# MODEL CONFIGURATION
# =========================================================

# Centralized model name so it can easily be changed later.
MODEL_NAME = "llama-3.1-8b-instant"


# =========================================================
# GENERATE LLM RESPONSE
# =========================================================

def generate_response(
    prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 700,
) -> str:
    """
    Send a prompt to the Groq-hosted Llama model
    and return the generated response.
    """

    # -----------------------------------------------------
    # VALIDATE PROMPT
    # -----------------------------------------------------

    if not prompt or not prompt.strip():
        raise ValueError(
            "Prompt cannot be empty."
        )

    # -----------------------------------------------------
    # SEND REQUEST TO GROQ
    # -----------------------------------------------------

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,

            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],

            temperature=temperature,
            max_tokens=max_tokens,
        )

        # -------------------------------------------------
        # EXTRACT RESPONSE
        # -------------------------------------------------

        answer = response.choices[0].message.content

        if not answer:
            return (
                "The model returned an empty response."
            )

        return answer.strip()

    # -----------------------------------------------------
    # ERROR HANDLING
    # -----------------------------------------------------

    except Exception as error:

        raise RuntimeError(
            f"LLM request failed: {error}"
        )