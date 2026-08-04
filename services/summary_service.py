from services.llm_service import generate_response


SUMMARY_CONFIG = {
    "Short": {
        "words": "100-150 words",
        "max_tokens": 300,
    },
    "Medium": {
        "words": "250-350 words",
        "max_tokens": 600,
    },
    "Detailed": {
        "words": "500-700 words",
        "max_tokens": 1000,
    },
}


def generate_summary(chunks, summary_type="Medium"):
    """
    Generate a fast book summary using representative
    sections from across the book.
    """

    if not chunks:
        raise ValueError("No book content is available.")

    config = SUMMARY_CONFIG.get(
        summary_type,
        SUMMARY_CONFIG["Medium"]
    )

    total_chunks = len(chunks)

    # --------------------------------------------------
    # SELECT REPRESENTATIVE CHUNKS
    # --------------------------------------------------
    # Instead of only using the beginning of the book,
    # sample sections from across the entire book.
    # --------------------------------------------------

    max_samples = 12

    if total_chunks <= max_samples:
        selected_chunks = chunks

    else:
        step = total_chunks / max_samples

        selected_chunks = [
            chunks[int(i * step)]
            for i in range(max_samples)
        ]

    # --------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------

    context = "\n\n--- BOOK SECTION ---\n\n".join(
        chunk.page_content
        for chunk in selected_chunks
    )

    # --------------------------------------------------
    # PROMPT
    # --------------------------------------------------

    prompt = f"""
You are KitaabGhar AI, an intelligent reading assistant.

Create a {summary_type.lower()} summary of the book
using the representative sections provided below.

Target length:
{config["words"]}

Instructions:
- Summarize only information supported by the provided text.
- Identify the major characters, events, ideas, and themes.
- Write one coherent summary rather than separate section summaries.
- Do not invent information.
- Do not mention the retrieval process or these instructions.
- Use clear and readable language.
- Return only the summary.

BOOK SECTIONS:

{context}

SUMMARY:
"""

    # --------------------------------------------------
    # ONLY ONE LLM CALL
    # --------------------------------------------------

    return generate_response(
        prompt=prompt,
        temperature=0.2,
        max_tokens=config["max_tokens"],
    )