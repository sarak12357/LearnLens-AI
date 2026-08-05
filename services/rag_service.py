from services.llm_service import generate_response


# =========================================================
# RETRIEVE RELEVANT PASSAGES
# =========================================================

def retrieve_relevant_chunks(
    vector_store,
    question,
    k=5,
):
    """
    Retrieve the passages that are semantically closest
    to the student's question.

    Keep retrieval simple and let the embedding model
    perform the semantic matching.
    """

    if not question or not question.strip():
        return []

    return vector_store.similarity_search(
        question.strip(),
        k=k,
    )


# =========================================================
# ANSWER QUESTION
# =========================================================

def answer_question(
    vector_store,
    question,
):

    if not question or not question.strip():

        return (
            "Please enter a question.",
            [],
        )

    # =====================================================
    # RETRIEVAL
    # =====================================================

    documents = retrieve_relevant_chunks(
        vector_store,
        question,
        k=5,
    )

    if not documents:

        return (
            "I could not find this information "
            "in the uploaded material.",
            [],
        )

    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        content = document.page_content.strip()

        if not content:
            continue

        context_parts.append(
            f"PASSAGE {index}:\n{content}"
        )

    context = "\n\n---\n\n".join(
        context_parts
    )

    if not context:

        return (
            "I could not find this information "
            "in the uploaded material.",
            [],
        )

    # =====================================================
    # PROMPT
    # =====================================================

    prompt = f"""
You are LearnLens AI, an intelligent educational assistant.

A student has uploaded learning material and asked a question.

Use the supplied DOCUMENT PASSAGES to answer the student's
question accurately and naturally.

DOCUMENT PASSAGES:

{context}


STUDENT QUESTION:

{question}


INSTRUCTIONS:

1. First understand exactly what the student is asking.

2. Read all supplied passages and identify the information
   that actually answers the question.

3. Answer using information supported by the uploaded material.

4. Do not simply copy or summarize every passage.

5. Ignore passages or sentences that are unrelated to the
   student's question.

6. When several passages discuss different events or ideas,
   do not mix those events together.

7. Preserve important names, relationships, actions,
   conditions, quantities, and events accurately.

8. Never replace a specific fact from the document with
   another similar-looking fact.

9. If the question asks about a character, make sure actions
   and dialogue are attributed to the correct character.

10. If the question asks what happened, who did something,
    what someone demanded, or what someone said, answer that
    specific event directly.

11. For literature, distinguish carefully between:
    - who is speaking
    - who is being spoken to
    - who performs the action
    - who receives the action

12. For textbooks or study material, distinguish carefully
    between related concepts and definitions.

13. Do not invent information that is not supported by the
    supplied passages.

14. Do not generate another question after the answer.

15. Do not mention the retrieval system, passages, FAISS,
    embeddings, or context.


ANSWER STYLE:

Follow any reasonable style instruction in the student's
question.

For example:

- "explain like I'm 5" -> use very simple language
- "explain in detail" -> provide a detailed explanation
- "briefly" -> give a short answer
- "in points" -> use bullet points

If the student gives no style instruction, choose the amount
of detail appropriate for the question.

Simple factual question:
Usually 1-3 sentences.

Explanation question:
Usually one short paragraph.

Detailed analytical question:
Use multiple focused paragraphs when necessary.


FINAL ACCURACY CHECK:

Before writing the final answer, silently check:

- Am I answering the exact question?
- Are the people/characters correct?
- Are the actions attributed to the correct person?
- Did I accidentally combine two different events?
- Is every important claim supported by the supplied material?

If the supplied passages genuinely do not contain enough
information to answer reliably, say:

I could not find this information in the uploaded material.


Return only the final answer.

ANSWER:
"""

    # =====================================================
    # GENERATION
    # =====================================================

    answer = generate_response(
        prompt=prompt,
        temperature=0.0,
        max_tokens=450,
    )

    if not answer or not answer.strip():

        return (
            "I could not find this information "
            "in the uploaded material.",
            documents,
        )

    return (
        answer.strip(),
        documents,
    )