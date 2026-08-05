import json
import random
import re

from services.llm_service import generate_response


# =========================================================
# DIFFICULTY DEFINITIONS
# =========================================================

DIFFICULTY_INSTRUCTIONS = {

    "Easy": """
Create factual recall questions.

Questions should test information that is directly stated
in the supplied book passages.

Focus on:
- characters
- places
- events
- objects
- actions
- explicitly stated facts

Avoid:
- symbolism
- deep interpretation
- complicated inference
- thematic analysis
""",

    "Medium": """
Create comprehension questions.

Questions should require the reader to understand:
- character motivations
- relationships
- important events
- causes and effects
- consequences of actions

Avoid questions that are only simple factual recall.
""",

    "Hard": """
Create challenging literary comprehension questions.

Questions should require reasoning about:
- implications
- motivations
- comparisons
- conflicts
- themes
- interpretation
- cause-and-effect relationships

The correct answer MUST still be clearly supported
by the supplied book passages.

Do not require outside knowledge about the book.
"""
}


# =========================================================
# BUILD PROMPT
# =========================================================

def _build_prompt(
    context,
    num_questions,
    difficulty,
    retry=False
):

    difficulty_instruction = DIFFICULTY_INSTRUCTIONS.get(
        difficulty,
        DIFFICULTY_INSTRUCTIONS["Medium"]
    )

    variation_id = random.randint(
        100000,
        999999
    )

    retry_instruction = ""

    if retry:
        retry_instruction = """
IMPORTANT QUALITY RETRY:

A previous quiz failed automatic quality validation.

Pay EXTRA attention to the following:

- Do not create repetitive answer patterns.
- Do not make all four options begin with the same phrase.
- Keep distractors plausible.
- Avoid absurd or obviously incorrect distractors.
- Avoid vague options.
- Avoid unnecessarily long options.
- Make each option meaningfully different.
- Do not repeat information already contained in the question.
"""

    prompt = f"""
You are KitaabGhar AI, an educational quiz generator.

Create a high-quality multiple-choice quiz using ONLY
the supplied BOOK CONTENT.

QUIZ SETTINGS

Number of questions:
{num_questions}

Difficulty:
{difficulty}

Difficulty requirements:

{difficulty_instruction}

Quiz variation ID:
{variation_id}

{retry_instruction}


CONTENT RULES

1. Use ONLY information supported by BOOK CONTENT.

2. Every correct answer must be supported by the supplied passages.

3. Do not use outside knowledge about the book.

4. Generate exactly {num_questions} questions.

5. Do not repeat the same question.

6. Do not test the exact same fact more than once.

7. Questions must sound natural and educational.

8. Avoid awkward wording such as:
   "What is the main reason why..."

Prefer:
   "Why does..."
   "How does..."
   "What causes..."
   "Which statement best explains..."
   "What happens when..."


QUESTION QUALITY

Each question should test ONE clear idea.

Do not create questions that are:
- ambiguous
- unnecessarily complicated
- based on missing context
- impossible to answer from the supplied passages

For Medium and Hard questions, reasoning is allowed,
but the correct answer must still be grounded in the text.


OPTION QUALITY RULES

Every question must have exactly FOUR options.

The options must be:

- concise
- clear
- grammatically natural
- meaningfully different
- similar in style
- reasonably similar in length
- plausible alternatives

Incorrect options should be believable enough that
the reader must understand the passage to answer correctly.

Do NOT create ridiculous distractors merely to fill
the four options.


CRITICAL REPETITION RULE

Do NOT make three or four options begin with the same
three or more words.

BAD:

Question:
Why does Jessica refuse to hold the candle?

Options:
"Because she is ashamed of being seen"
"Because she is afraid of Lorenzo"
"Because she dislikes the candle"
"Because she wants to remain inside"

BETTER:

Question:
Why does Jessica refuse to hold the candle?

Options:
"She is ashamed of being seen"
"She fears being recognized"
"She dislikes drawing attention"
"She wants to remain hidden"


BAD:

Question:
What condition is imposed on Shylock?

Options:
"He must become a Christian and give property to Antonio"
"He must become a Christian and give property to Lorenzo"
"He must become a Christian and leave Venice"
"He must become a Christian and pay the Duke"

BETTER:

Question:
Besides converting to Christianity, what condition
is imposed on Shylock?

Options:
"Transfer his estate as required"
"Leave Venice permanently"
"Pay a fine to the Duke"
"Surrender his house to Antonio"


OPTION CONSTRUCTION PROCESS

Before writing each question:

1. Identify the fact or idea being tested.

2. Put shared information in the QUESTION.

3. Do not repeat that shared information in every option.

4. Make each option contain mainly the information
   that distinguishes it from the others.

5. Prefer concise phrases or clauses.

6. Keep options reasonably similar in length.

7. Make distractors plausible within the context.

8. Avoid repeating:
   "Because he..."
   "Because she..."
   "He must..."
   "She must..."
   "The reason is..."
   across all four options.

9. Avoid obviously absurd distractors.

10. Ideally keep each option below 15 words.


ANSWER RULES

1. Exactly ONE option must be correct.

2. The correct answer must be supported by BOOK CONTENT.

3. Incorrect answers should be plausible but incorrect.

4. Do not always make the correct answer the longest.

5. Randomize the position of the correct answer.

6. "correct_answer" MUST exactly match one of the
   four option strings.


FINAL SELF-CHECK

Before returning the quiz, inspect every question.

Rewrite a question if:

- three or more options begin with the same phrase
- distractors are obviously ridiculous
- options repeat the question unnecessarily
- multiple options appear correct
- the question requires information outside BOOK CONTENT
- the options are excessively long


OUTPUT RULES

Return ONLY a valid JSON array.

Do NOT include:
- Markdown
- code fences
- explanations
- introductions
- comments
- text before the JSON
- text after the JSON


Use exactly this structure:

[
  {{
    "question": "Question text?",
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

    return prompt


# =========================================================
# CLEAN + PARSE LLM RESPONSE
# =========================================================

def _parse_quiz_response(response):

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

    # Extract JSON array if the model accidentally
    # adds text before or after the JSON.

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1:

        raise ValueError(
            "The AI response did not contain a valid quiz."
        )

    cleaned = cleaned[
        start:end + 1
    ]

    try:

        quiz = json.loads(
            cleaned
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Unable to read AI quiz response: {error}"
        )

    if not isinstance(
        quiz,
        list
    ):

        raise ValueError(
            "The generated quiz has an invalid format."
        )

    return quiz


# =========================================================
# NORMALIZE TEXT
# =========================================================

def _normalize_text(text):

    text = str(text).lower().strip()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# =========================================================
# GET STARTING WORDS
# =========================================================

def _starting_words(
    text,
    count=3
):

    words = re.findall(
        r"\b[\w']+\b",
        _normalize_text(text)
    )

    return tuple(
        words[:count]
    )


# =========================================================
# DETECT REPETITIVE OPTIONS
# =========================================================

def _has_repetitive_options(options):

    if len(options) != 4:
        return True

    # -----------------------------------------------------
    # CHECK FIRST THREE WORDS
    # -----------------------------------------------------

    three_word_starts = [
        _starting_words(
            option,
            3
        )
        for option in options
    ]

    for start in set(
        three_word_starts
    ):

        if not start:
            continue

        if (
            three_word_starts.count(start)
            >= 3
        ):

            return True

    # -----------------------------------------------------
    # CHECK FIRST TWO WORDS
    # -----------------------------------------------------

    two_word_starts = [
        _starting_words(
            option,
            2
        )
        for option in options
    ]

    for start in set(
        two_word_starts
    ):

        if not start:
            continue

        if (
            two_word_starts.count(start)
            == 4
        ):

            return True

    return False


# =========================================================
# DETECT EXCESSIVELY LONG OPTIONS
# =========================================================

def _has_excessively_long_options(options):

    lengths = [
        len(option.split())
        for option in options
    ]

    # Reject only genuinely excessive options.
    # We do not want the validator to be too strict.

    very_long_count = sum(
        length > 22
        for length in lengths
    )

    return very_long_count >= 2


# =========================================================
# VALIDATE ONE QUESTION
# =========================================================

def _validate_question(
    item,
    seen_questions
):

    if not isinstance(
        item,
        dict
    ):

        return None

    question = item.get(
        "question"
    )

    options = item.get(
        "options"
    )

    correct_answer = item.get(
        "correct_answer"
    )

    # =====================================================
    # QUESTION
    # =====================================================

    if not question:
        return None

    question = str(
        question
    ).strip()

    if len(question) < 5:
        return None

    normalized_question = _normalize_text(
        question
    )

    if normalized_question in seen_questions:
        return None

    # =====================================================
    # OPTIONS
    # =====================================================

    if not isinstance(
        options,
        list
    ):

        return None

    options = [
        str(option).strip()
        for option in options
    ]

    if len(options) != 4:
        return None

    # No empty options

    if any(
        not option
        for option in options
    ):

        return None

    # =====================================================
    # UNIQUE OPTIONS
    # =====================================================

    normalized_options = [
        _normalize_text(option)
        for option in options
    ]

    if len(
        set(normalized_options)
    ) != 4:

        return None

    # =====================================================
    # REPETITION QUALITY CHECK
    # =====================================================

    # Do not reject a valid question merely because several
    # distractors share a grammatical opening. This is common
    # in higher-difficulty questions and was causing Hard quizzes
    # to collapse to zero valid questions.

    # =====================================================
    # OPTION LENGTH CHECK
    # =====================================================

    if _has_excessively_long_options(
        options
    ):

        return None

    # =====================================================
    # CORRECT ANSWER
    # =====================================================

    if correct_answer is None:
        return None

    correct_answer = str(
        correct_answer
    ).strip()

    matched_answer = None

    # -----------------------------------------------------
    # EXACT TEXT MATCH
    # -----------------------------------------------------

    for option in options:

        if (
            _normalize_text(option)
            == _normalize_text(correct_answer)
        ):

            matched_answer = option
            break

    # -----------------------------------------------------
    # HANDLE A / B / C / D
    # -----------------------------------------------------

    if matched_answer is None:

        letter_map = {
            "a": 0,
            "b": 1,
            "c": 2,
            "d": 3
        }

        normalized_answer = (
            correct_answer
            .lower()
            .replace("option", "")
            .replace(".", "")
            .replace(")", "")
            .replace("(", "")
            .replace(":", "")
            .strip()
        )

        if normalized_answer in letter_map:

            matched_answer = options[
                letter_map[
                    normalized_answer
                ]
            ]

    # -----------------------------------------------------
    # HANDLE 1 / 2 / 3 / 4
    # -----------------------------------------------------

    if matched_answer is None:

        numeric_answer = re.sub(
            r"[^1-4]",
            "",
            correct_answer,
        )

        if numeric_answer in {"1", "2", "3", "4"}:
            matched_answer = options[int(numeric_answer) - 1]

    if matched_answer is None:
        return None

    # =====================================================
    # RANDOMIZE OPTION ORDER
    # =====================================================

    random.shuffle(
        options
    )

    seen_questions.add(
        normalized_question
    )

    return {
        "question": question,
        "options": options,
        "correct_answer": matched_answer
    }


# =========================================================
# VALIDATE COMPLETE QUIZ
# =========================================================

def _validate_quiz(
    quiz,
    num_questions
):

    valid_questions = []

    seen_questions = set()

    for item in quiz:

        validated = _validate_question(
            item,
            seen_questions
        )

        if validated is not None:

            valid_questions.append(
                validated
            )

        if (
            len(valid_questions)
            >= num_questions
        ):

            break

    return valid_questions


# =========================================================
# GENERATE QUIZ ONCE
# =========================================================

def _generate_once(
    chunks,
    num_questions,
    difficulty,
    retry=False
):

    # =====================================================
    # RANDOMLY SELECT DIFFERENT BOOK PASSAGES
    # =====================================================

    sample_count = min(
        14,
        len(chunks)
    )

    selected_chunks = random.sample(
        chunks,
        sample_count
    )

    context = "\n\n--- BOOK PASSAGE ---\n\n".join(
        chunk.page_content
        for chunk in selected_chunks
    )

    # =====================================================
    # BUILD PROMPT
    # =====================================================

    # Ask for a small surplus. Validation can discard malformed or
    # duplicate items without forcing the whole quiz to fail.
    requested_from_model = min(num_questions + 2, 12)

    prompt = _build_prompt(
        context=context,
        num_questions=requested_from_model,
        difficulty=difficulty,
        retry=retry
    )

    # =====================================================
    # CALL LLM
    # =====================================================

    response = generate_response(
        prompt=prompt,
        temperature=0.6,
        max_tokens=2400
    )

    # =====================================================
    # PARSE
    # =====================================================

    quiz = _parse_quiz_response(
        response
    )

    # =====================================================
    # VALIDATE
    # =====================================================

    valid_questions = _validate_quiz(
        quiz,
        num_questions
    )

    return valid_questions


# =========================================================
# MAIN QUIZ GENERATOR
# =========================================================

def generate_quiz(
    chunks,
    num_questions=5,
    difficulty="Medium"
):
    """
    Generate exactly the requested number of valid quiz questions.

    The generator keeps valid questions from earlier attempts and
    requests only the missing number on later attempts. It never
    silently returns a partial quiz.
    """

    if not chunks:
        raise ValueError(
            "No book content is available."
        )

    if num_questions not in (3, 5, 10):
        raise ValueError(
            "Number of questions must be 3, 5, or 10."
        )

    if difficulty not in DIFFICULTY_INSTRUCTIONS:
        difficulty = "Medium"

    collected = []
    seen_questions = set()

    # More than one retry is useful here because validation can
    # legitimately reject otherwise parseable LLM questions.
    max_attempts = 4

    for attempt in range(max_attempts):

        missing_count = (
            num_questions
            - len(collected)
        )

        if missing_count <= 0:
            break

        try:
            generated = _generate_once(
                chunks=chunks,
                num_questions=missing_count,
                difficulty=difficulty,
                retry=(attempt > 0),
            )

        except Exception:
            generated = []

        for question in generated:

            normalized_question = _normalize_text(
                question.get(
                    "question",
                    ""
                )
            )

            if not normalized_question:
                continue

            if normalized_question in seen_questions:
                continue

            collected.append(
                question
            )

            seen_questions.add(
                normalized_question
            )

            if len(collected) >= num_questions:
                break

    # Never show 2 questions when the user selected 3,
    # 4 when they selected 5, etc.
    if len(collected) != num_questions:
        raise ValueError(
            "The AI generated only "
            f"{len(collected)} valid question"
            f"{'s' if len(collected) != 1 else ''} "
            f"out of the requested {num_questions}. "
            "Please click Generate Quiz again."
        )

    return collected
