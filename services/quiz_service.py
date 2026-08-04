import json
import random
import re

from services.llm_service import generate_response


DIFFICULTY_INSTRUCTIONS = {
    "Easy": """
Create straightforward factual questions based directly on the text.
Focus on characters, places, events, objects, and explicitly stated facts.
""",

    "Medium": """
Create questions that require understanding of the text.
Focus on character motivations, relationships, causes and effects,
important events, and meaning within the passage.
""",

    "Hard": """
Create challenging questions requiring deeper understanding.
Focus on implications, motivations, comparisons, themes,
cause-and-effect relationships, and interpretation.
The answer must still be clearly supported by the supplied text.
"""
}


def generate_quiz(
    chunks,
    num_questions=5,
    difficulty="Medium"
):
    if not chunks:
        raise ValueError("No book content is available.")

    # ==================================================
    # RANDOMLY SELECT CONTENT
    # ==================================================

    sample_count = min(12, len(chunks))

    selected_chunks = random.sample(
        chunks,
        sample_count
    )

    context = "\n\n--- BOOK SECTION ---\n\n".join(
        chunk.page_content
        for chunk in selected_chunks
    )

    difficulty_instruction = DIFFICULTY_INSTRUCTIONS.get(
        difficulty,
        DIFFICULTY_INSTRUCTIONS["Medium"]
    )

    variation_id = random.randint(
        100000,
        999999
    )

    # ==================================================
    # PROMPT
    # ==================================================

    prompt = f"""
You are KitaabGhar AI, an educational quiz generator.

Create exactly {num_questions} NEW multiple-choice questions.

Difficulty:
{difficulty}

Difficulty instructions:
{difficulty_instruction}

Quiz variation ID:
{variation_id}

IMPORTANT RULES:

1. Use ONLY information contained in BOOK CONTENT.
2. Every question must have exactly four answer options.
3. Exactly one option must be correct.
4. The value of "correct_answer" MUST exactly match
   one of the four option strings.
5. Do not label options A, B, C, or D.
6. Do not add explanations.
7. Do not add introductory text.
8. Do not use Markdown.
9. Return ONLY a valid JSON array.
10. Generate questions different from previous quizzes.

Return exactly this structure:

[
  {{
    "question": "Question here?",
    "options": [
      "First option",
      "Second option",
      "Third option",
      "Fourth option"
    ],
    "correct_answer": "Second option"
  }}
]

BOOK CONTENT:

{context}
"""

    # ==================================================
    # CALL LLM
    # ==================================================

    response = generate_response(
        prompt=prompt,
        temperature=0.4,
        max_tokens=2200
    )

    # ==================================================
    # CLEAN RESPONSE
    # ==================================================

    cleaned = response.strip()

    cleaned = re.sub(
        r"```json",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = cleaned.replace(
        "```",
        ""
    ).strip()

    # Sometimes models add text before/after JSON.
    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1:
        raise ValueError(
            "The AI response did not contain a valid quiz."
        )

    cleaned = cleaned[
        start:end + 1
    ]

    # ==================================================
    # PARSE JSON
    # ==================================================

    try:
        quiz = json.loads(cleaned)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Unable to read AI quiz response: {error}"
        )

    if not isinstance(quiz, list):
        raise ValueError(
            "The generated quiz has an invalid format."
        )

    # ==================================================
    # VALIDATE + NORMALIZE QUESTIONS
    # ==================================================

    valid_questions = []

    for item in quiz:

        if not isinstance(item, dict):
            continue

        question = item.get(
            "question"
        )

        options = item.get(
            "options"
        )

        correct_answer = item.get(
            "correct_answer"
        )

        if not question:
            continue

        if not isinstance(options, list):
            continue

        # Convert everything to strings
        options = [
            str(option).strip()
            for option in options
        ]

        # Exactly four options required
        if len(options) != 4:
            continue

        if correct_answer is None:
            continue

        correct_answer = str(
            correct_answer
        ).strip()

        # ------------------------------------------------
        # EXACT MATCH
        # ------------------------------------------------

        matched_answer = None

        for option in options:

            if (
                option.lower()
                == correct_answer.lower()
            ):
                matched_answer = option
                break

        # ------------------------------------------------
        # HANDLE A/B/C/D ANSWERS
        # ------------------------------------------------

        if matched_answer is None:

            letter_map = {
                "a": 0,
                "b": 1,
                "c": 2,
                "d": 3
            }

            normalized = (
                correct_answer
                .lower()
                .replace("option", "")
                .replace(".", "")
                .replace(")", "")
                .strip()
            )

            if normalized in letter_map:

                matched_answer = options[
                    letter_map[normalized]
                ]

        if matched_answer is None:
            continue

        valid_questions.append(
            {
                "question": str(question).strip(),
                "options": options,
                "correct_answer": matched_answer
            }
        )

    # ==================================================
    # FINAL VALIDATION
    # ==================================================

    if not valid_questions:
        raise ValueError(
            "The AI did not generate any valid questions. "
            "Please click Generate Quiz again."
        )

    return valid_questions[
        :num_questions
    ]