import streamlit as st

from services.book_loader import load_uploaded_book
from services.text_splitter import split_book
from services.vector_store import create_vector_store
from services.rag_service import answer_question
from services.summary_service import generate_summary
from services.quiz_service import generate_quiz


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="KitaabGhar AI",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# BOOK CONFIGURATION
# =========================================================

# BOOK_PATH = "data/books/jane_eyre.txt"


# =========================================================
# PREPARE BOOK
# =========================================================

# @st.cache_resource
# def prepare_book():
#     documents = load_book(BOOK_PATH)

#     chunks = split_book(documents)

#     vector_store = create_vector_store(chunks)

#     return chunks, vector_store


# =========================================================
# HEADER
# =========================================================

st.title("📚 KitaabGhar AI")

st.caption(
    "An LLM-powered intelligent reading assistant"
)

# =========================================================
# BOOK UPLOAD
# =========================================================

st.sidebar.header("📚 Book Setup")

uploaded_file = st.sidebar.file_uploader(
    "Upload your book",
    type=["pdf", "txt"],
    help="Upload a PDF or TXT book."
)


if uploaded_file is None:

    st.info(
        "👈 Upload a PDF or TXT book from the sidebar to begin."
    )

    st.stop()
    

# =========================================================
# PROCESS BOOK
# =========================================================

@st.cache_resource(show_spinner=False)
def prepare_uploaded_book(
    file_name,
    file_bytes
):
    import io

    class UploadedBook:
        def __init__(
            self,
            name,
            data
        ):
            self.name = name
            self._data = data

        def getvalue(self):
            return self._data

        def read(self, *args, **kwargs):
            return self._data

    book_file = UploadedBook(
        file_name,
        file_bytes
    )

    # PDF reader needs a file-like stream.
    if file_name.lower().endswith(".pdf"):
        book_file = io.BytesIO(
            file_bytes
        )

        book_file.name = file_name

    documents = load_uploaded_book(
        book_file
    )

    chunks = split_book(
        documents
    )

    vector_store = create_vector_store(
        chunks
    )

    return (
        documents,
        chunks,
        vector_store
    )


try:

    with st.spinner(
        "Processing book and building knowledge base..."
    ):

        documents, chunks, vector_store = (
            prepare_uploaded_book(
                uploaded_file.name,
                uploaded_file.getvalue()
            )
        )

except Exception as error:

    st.error(
        f"Unable to process book: {error}"
    )

    st.stop()
    
st.success(
    f"📖 {uploaded_file.name} loaded successfully — "
    f"{len(chunks)} knowledge chunks ready."
)


# =========================================================
# TABS
# =========================================================

chat_tab, summary_tab, quiz_tab = st.tabs(
    [
        "💬 Book Chat",
        "📝 AI Summary",
        "🧠 AI Quiz"
    ]
)
# =========================================================
# BOOK CHAT + CONVERSATION HISTORY
# =========================================================


# =========================================================
# CLEAR CHAT CONFIRMATION DIALOG
# =========================================================

@st.dialog("Delete chat history?")
def confirm_clear_chat():

    st.warning(
        "Are you sure you want to delete the entire chat history?"
    )

    st.write(
        "All questions, answers, and retrieved sources "
        "from this conversation will be permanently removed."
    )

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # CANCEL
    # -----------------------------------------------------

    with col1:

        if st.button(
            "Cancel",
            use_container_width=True,
            key="cancel_clear_chat"
        ):
            st.rerun()

    # -----------------------------------------------------
    # CONFIRM DELETE
    # -----------------------------------------------------

    with col2:

        if st.button(
            "🗑️ Delete Chat",
            type="primary",
            use_container_width=True,
            key="confirm_clear_chat"
        ):

            st.session_state.chat_history = []

            st.rerun()


# =========================================================
# BOOK CHAT TAB
# =========================================================

with chat_tab:

    st.header("💬 Chat With The Book")

    st.write(
        "Ask questions and KitaabGhar AI will retrieve "
        "relevant sections before generating an answer."
    )

    # =====================================================
    # INITIALIZE CHAT HISTORY
    # =====================================================

    if "chat_history" not in st.session_state:

        st.session_state.chat_history = []

    if "active_book" not in st.session_state:

        st.session_state.active_book = uploaded_file.name

    # =====================================================
    # RESET HISTORY WHEN BOOK CHANGES
    # =====================================================

    if st.session_state.active_book != uploaded_file.name:

        st.session_state.chat_history = []

        st.session_state.active_book = uploaded_file.name

    # =====================================================
    # QUESTION INPUT
    # =====================================================
    # The input is intentionally placed before the history
    # so it stays above the previous conversations.
    # =====================================================

    question = st.chat_input(
        "Ask something about the book...",
        key="book_chat_input"
    )

    # =====================================================
    # PROCESS NEW QUESTION
    # =====================================================

    if question:

        try:

            with st.spinner(
                "Searching the book and generating an answer..."
            ):

                answer, sources = answer_question(
                    vector_store,
                    question
                )

            # =================================================
            # CONVERT SOURCES INTO SESSION-SAFE DATA
            # =================================================

            stored_sources = []

            for source in sources:

                stored_sources.append(
                    {
                        "content": source.page_content,

                        "book_name": source.metadata.get(
                            "book_name",
                            uploaded_file.name
                        )
                    }
                )

            # =================================================
            # CREATE CONVERSATION ITEM
            # =================================================

            conversation = {
                "question": question,
                "answer": answer,
                "sources": stored_sources
            }

            # =================================================
            # STORE NEWEST CONVERSATION FIRST
            # =================================================

            st.session_state.chat_history.insert(
                0,
                conversation
            )

        except Exception as error:

            conversation = {
                "question": question,

                "answer": (
                    f"Unable to generate an answer: {error}"
                ),

                "sources": []
            }

            # Store failed request too so the user can see it
            st.session_state.chat_history.insert(
                0,
                conversation
            )

    # =====================================================
    # CHAT CONTROLS
    # =====================================================

    if st.session_state.chat_history:

        control_col1, control_col2 = st.columns(
            [1, 6]
        )

        with control_col1:

            if st.button(
                "🗑️ Clear Chat",
                key="clear_chat_button"
            ):

                confirm_clear_chat()

        st.divider()

    # =====================================================
    # DISPLAY CONVERSATION HISTORY
    # =====================================================
    #
    # Conversation order:
    #
    # Newest conversation
    # ↓
    # Previous conversation
    # ↓
    # Oldest conversation
    #
    # =====================================================

    for conversation_index, conversation in enumerate(
        st.session_state.chat_history
    ):

        # =================================================
        # USER QUESTION
        # =================================================

        with st.chat_message("user"):

            st.markdown(
                conversation["question"]
            )

        # =================================================
        # AI ANSWER
        # =================================================

        with st.chat_message("assistant"):

            st.markdown(
                conversation["answer"]
            )

            sources = conversation.get(
                "sources",
                []
            )

            # =============================================
            # RETRIEVED SOURCES
            # =============================================

            if sources:

                with st.expander(
                    "🔎 View Retrieved Sources"
                ):

                    for source_index, source in enumerate(
                        sources,
                        start=1
                    ):

                        st.markdown(
                            f"**Source {source_index}**"
                        )

                        st.write(
                            source["content"]
                        )

                        if source.get("book_name"):

                            st.caption(
                                f"Source: {source['book_name']}"
                            )

                        # Don't add divider after final source
                        if source_index < len(sources):

                            st.divider()

        # =================================================
        # SEPARATE CONVERSATIONS
        # =================================================

        if (
            conversation_index
            < len(st.session_state.chat_history) - 1
        ):

            st.divider()
            
            
            
# =========================================================
# AI SUMMARY
# =========================================================

with summary_tab:

    st.header("📝 AI Summary Generator")

    st.write(
        "Generate an AI-powered summary of the book."
    )

    summary_type = st.selectbox(
        "Summary length",
        [
            "Short",
            "Medium",
            "Detailed"
        ],
        key="summary_length"
    )

    if st.button(
        "Generate Summary",
        key="generate_summary_button"
    ):

        with st.spinner(
            "Generating summary..."
        ):

            try:

                summary = generate_summary(
                    chunks,
                    summary_type
                )

                st.subheader(
                    f"{summary_type} Summary"
                )

                st.write(summary)

            except Exception as error:

                st.error(
                    f"Unable to generate summary: {error}"
                )


# =========================================================
# AI QUIZ
# =========================================================

with quiz_tab:

    st.header("🧠 AI Quiz Generator")

    st.write(
        "Generate multiple-choice questions "
        "from the book content."
    )

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # NUMBER OF QUESTIONS
    # -----------------------------------------------------

    with col1:

        num_questions = st.selectbox(
            "Number of questions",
            [
                3,
                5,
                10
            ],
            key="num_questions"
        )

    # -----------------------------------------------------
    # DIFFICULTY
    # -----------------------------------------------------

    with col2:

        difficulty = st.selectbox(
            "Difficulty",
            [
                "Easy",
                "Medium",
                "Hard"
            ],
            key="quiz_difficulty"
        )

    # -----------------------------------------------------
    # GENERATE QUIZ
    # -----------------------------------------------------

    if st.button(
        "Generate Quiz",
        key="generate_quiz_button"
    ):

        with st.spinner(
            "Creating your quiz..."
        ):

            try:

                quiz = generate_quiz(
                    chunks,
                    num_questions,
                    difficulty
                )

                if not quiz:

                    st.error(
                        "The AI could not generate a valid quiz. "
                        "Please try again."
                    )

                else:

                    # Save quiz in session state
                    st.session_state.quiz = quiz

                    # Clear previous answers
                    for key in list(
                        st.session_state.keys()
                    ):

                        if key.startswith(
                            "quiz_answer_"
                        ):

                            del st.session_state[key]

            except Exception as error:

                st.error(
                    f"Unable to generate quiz: {error}"
                )


    # =====================================================
    # DISPLAY QUIZ
    # =====================================================

    if "quiz" in st.session_state:

        quiz = st.session_state.quiz

        st.divider()

        st.subheader("Your Quiz")

        answers = []

        for index, question_data in enumerate(
            quiz
        ):

            st.markdown(
                f"### Question {index + 1}"
            )

            st.write(
                question_data.get(
                    "question",
                    "Question unavailable"
                )
            )

            options = question_data.get(
                "options",
                []
            )

            if options:

                answer = st.radio(
                    "Choose your answer:",
                    options,
                    key=f"quiz_answer_{index}",
                    index=None
                )

                answers.append(answer)

            else:

                st.warning(
                    "No options available for this question."
                )

                answers.append(None)

            st.write("")


        # =================================================
        # SUBMIT QUIZ
        # =================================================

        if st.button(
            "Submit Quiz",
            type="primary",
            key="submit_quiz_button"
        ):

            unanswered = sum(
                answer is None
                for answer in answers
            )

            if unanswered > 0:

                st.warning(
                    "Please answer all questions "
                    "before submitting the quiz."
                )

            else:

                score = 0

                results = []

                for index, question_data in enumerate(
                    quiz
                ):

                    user_answer = answers[index]

                    correct_answer = question_data.get(
                        "correct_answer"
                    )

                    is_correct = (
                        user_answer
                        == correct_answer
                    )

                    if is_correct:

                        score += 1

                    results.append(
                        {
                            "question": question_data.get(
                                "question"
                            ),
                            "user_answer": user_answer,
                            "correct_answer": correct_answer,
                            "is_correct": is_correct
                        }
                    )


                # =========================================
                # SCORE
                # =========================================

                st.divider()

                st.header(
                    f"🎯 Score: {score}/{len(quiz)}"
                )

                percentage = (
                    score / len(quiz)
                ) * 100


                if percentage == 100:

                    st.success(
                        "Excellent! Perfect score!"
                    )

                elif percentage >= 60:

                    st.success(
                        "Good job!"
                    )

                else:

                    st.info(
                        "Keep reading and try again!"
                    )


                # =========================================
                # ANSWER REVIEW
                # =========================================

                with st.expander(
                    "📋 Review Answers"
                ):

                    for index, result in enumerate(
                        results,
                        start=1
                    ):

                        st.markdown(
                            f"### Question {index}"
                        )

                        st.write(
                            result["question"]
                        )

                        st.write(
                            f"Your answer: "
                            f"{result['user_answer']}"
                        )

                        if result["is_correct"]:

                            st.success(
                                "Correct"
                            )

                        else:

                            st.error(
                                "Incorrect"
                            )

                            st.write(
                                f"Correct answer: "
                                f"{result['correct_answer']}"
                            )

                        st.divider()