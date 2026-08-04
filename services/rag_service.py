from services.llm_service import generate_response


def retrieve_relevant_chunks(
    vector_store,
    question,
    k=6,
):
    if not question or not question.strip():
        return []

    return vector_store.similarity_search(
        question,
        k=k,
    )


def answer_question(
    vector_store,
    question,
):
    documents = retrieve_relevant_chunks(
        vector_store,
        question,
        k=6,
    )

    if not documents:
        return (
            "I could not find relevant information "
            "in the selected book."
        )

    context = "\n\n---\n\n".join(
        document.page_content
        for document in documents
    )

    prompt = f"""
You are KitaabGhar AI, an intelligent reading assistant.

Answer the user's question using the provided BOOK CONTEXT.

Important rules:
- Base your answer on the provided book context.
- You may combine information from multiple provided passages.
- Do not invent events or facts that contradict the book.
- If the passages contain relevant information, answer the question clearly.
- Only say "I could not find this information in the selected book"
  when the provided passages genuinely contain no relevant information.

BOOK CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    answer = generate_response(
        prompt=prompt,
        temperature=0.1,
        max_tokens=500,
    )

    return answer, documents