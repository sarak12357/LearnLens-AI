# 📚 LearnLens AI

### An AI-Powered Intelligent Reading Assistant using RAG and Large Language Models

KitaabGhar AI is an end-to-end Retrieval-Augmented Generation (RAG) application designed to help users interact intelligently with books and long-form textual documents.

Instead of sending an entire book to a Large Language Model, the application processes the document into smaller semantic chunks, converts them into vector embeddings, stores them in a FAISS vector database, and retrieves only the most relevant sections when answering a user's question.

The application also provides AI-powered book summarization and dynamic quiz generation.

---

## 🎯 Problem Statement

Reading and understanding large books or documents can be time-consuming. Traditional keyword search can locate exact words but cannot effectively answer contextual or semantic questions about the content.

Large Language Models can understand natural-language questions, but sending an entire book to an LLM is inefficient because of context-window limitations, token usage, latency, and cost.

KitaabGhar AI solves this problem using **Retrieval-Augmented Generation (RAG)**.

The system retrieves only the portions of the book that are relevant to a user's question and supplies those passages to the LLM for grounded answer generation.

---

## ✨ Key Features

### 💬 AI Book Chat

Users can ask natural-language questions about the uploaded book.

The system:

1. Converts the user's question into an embedding.
2. Searches the FAISS vector database.
3. Retrieves relevant book passages.
4. Provides those passages as context to the LLM.
5. Generates a grounded answer.
6. Displays the retrieved source passages.

Conversation history is maintained during the session.

---

### 📝 AI Summary Generator

KitaabGhar AI can generate different levels of summaries from book content.

Supported summary modes include:

- Short
- Medium
- Detailed

This allows users to quickly understand the important information contained in a book.

---

### 🧠 AI Quiz Generator

The application dynamically generates multiple-choice questions from book content.

Users can select:

- Number of questions
- Difficulty level

Supported difficulty levels:

- Easy
- Medium
- Hard

The quiz generator includes output validation to check:

- JSON structure
- Number of options
- Duplicate options
- Correct-answer consistency
- Repetitive option patterns
- Duplicate questions

If the first generated quiz does not satisfy the required quality checks, the system can perform a controlled regeneration attempt.

---

### 📖 Dynamic Book Upload

Users can upload a book/document and the application automatically prepares it for AI processing.

The document is:

1. Loaded
2. Extracted
3. Split into chunks
4. Converted into embeddings
5. Indexed inside FAISS

The prepared knowledge base can then be used by the AI features.

---

### 🔎 Source Transparency

For book-chat responses, users can inspect the passages retrieved by the RAG pipeline.

This makes the system more transparent by showing the context used to generate an answer.

---

## 🧠 What is Retrieval-Augmented Generation?

Retrieval-Augmented Generation combines information retrieval with Large Language Model generation.

Instead of asking the LLM to answer entirely from its pretrained knowledge, the system first retrieves relevant information from an external knowledge source.

In KitaabGhar AI, the knowledge source is the uploaded book.

### RAG Pipeline

```text
Book / Document
       ↓
Document Loading
       ↓
Text Extraction
       ↓
Text Chunking
       ↓
Embedding Generation
       ↓
FAISS Vector Database
       ↓
User Question
       ↓
Question Embedding
       ↓
Semantic Similarity Search
       ↓
Relevant Book Chunks
       ↓
Prompt + Retrieved Context
       ↓
Llama 3.1 8B
       ↓
Grounded Answer
```

---

## 🏗️ System Architecture

```text
                     ┌───────────────────────┐
                     │     Streamlit UI      │
                     └───────────┬───────────┘
                                 │
                  ┌──────────────┼──────────────┐
                  │              │              │
                  ▼              ▼              ▼
             Book Chat       AI Summary      AI Quiz
                  │              │              │
                  ▼              │              │
            RAG Service          │              │
                  │              │              │
                  ▼              ▼              ▼
           Retrieval /      Prompt-based    Prompt-based
          Vector Search      Generation      Generation
                  │              │              │
                  └──────────────┼──────────────┘
                                 │
                                 ▼
                        LLM Service
                                 │
                                 ▼
                    Llama 3.1 8B Instant
                         through Groq


Book Processing Pipeline:

Book
 │
 ▼
Book Loader
 │
 ▼
Text Splitter
 │
 ▼
BAAI/bge-small-en-v1.5
 │
 ▼
FAISS Vector Store
```

---

## 🤖 Models Used

### Large Language Model

**Llama 3.1 8B Instant**

The application accesses the model using the Groq API.

The model is used for:

- RAG-based question answering
- Book summarization
- Quiz generation

The model configuration is centralized in the LLM service so that it can be replaced or upgraded without changing the entire application.

---

### Embedding Model

**BAAI/bge-small-en-v1.5**

The embedding model converts textual chunks into numerical vector representations.

These vectors allow the application to perform semantic similarity search.

The embedding model runs on the CPU and uses normalized embeddings.

```python
model_name="BAAI/bge-small-en-v1.5"
```

---

## 🗄️ Vector Database

### FAISS

FAISS is used as the vector store for semantic retrieval.

The workflow is:

```text
Text Chunk
    ↓
Embedding Model
    ↓
Vector
    ↓
FAISS Index
```

When a user asks a question:

```text
Question
    ↓
Question Embedding
    ↓
FAISS Similarity Search
    ↓
Most Relevant Chunks
```

These chunks are then supplied to the LLM.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| LLM | Llama 3.1 8B Instant |
| LLM Provider | Groq |
| Embedding Model | BAAI/bge-small-en-v1.5 |
| Vector Database | FAISS |
| RAG Framework | LangChain |
| Embedding Integration | LangChain Hugging Face |
| Environment Management | python-dotenv |
| Document Processing | PyPDF / Text Processing |

---

## 📁 Project Structure

```text
KITAABGHAR-AI/
│
├── data/
│   └── books/
│       └── Sample book datasets
│
├── services/
│   ├── __init__.py
│   ├── book_loader.py
│   ├── embeddings.py
│   ├── llm_service.py
│   ├── quiz_service.py
│   ├── rag_service.py
│   ├── summary_service.py
│   ├── text_splitter.py
│   └── vector_store.py
│
├── screenshots/
│   └── Application screenshots
│
├── utils/
│   └── __init__.py
│
├── .env.example
├── .gitignore
├── app.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd kitaabghar-ai
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key_here
```

A template is provided in:

```text
.env.example
```

> Never commit your real `.env` file or API keys to GitHub.

---

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Streamlit will normally open the application in the browser at:

```text
http://localhost:8501
```

---

## 📦 Dependencies

Main dependencies include:

```text
streamlit
python-dotenv
langchain
langchain-community
langchain-huggingface
langchain-text-splitters
sentence-transformers
faiss-cpu
pypdf
requests
groq
```

---

## 🔄 Application Workflow

```text
User uploads/selects a book
            ↓
       Extract text
            ↓
       Split into chunks
            ↓
 Generate vector embeddings
            ↓
     Store using FAISS
            ↓
   Knowledge base prepared
            ↓
 ┌──────────┼───────────┐
 ↓          ↓           ↓
Chat      Summary      Quiz
 ↓
Retrieve relevant chunks
 ↓
Construct grounded prompt
 ↓
Send context to LLM
 ↓
Generate response
```

## 🧪 Error Handling and Validation

The application includes error handling for common failures such as:

- Empty prompts
- Missing API configuration
- LLM request failures
- Invalid quiz output
- Missing book content
- Malformed generated JSON

The quiz pipeline additionally validates generated questions before displaying them to the user.

---

## ⚠️ Limitations

Like most LLM-based applications, KitaabGhar AI has some limitations.

- Generated responses depend on the quality of retrieved context.
- LLM outputs are probabilistic and may occasionally be inaccurate.
- Automatically generated quiz distractors may vary in quality.
- Very large documents require additional processing time.
- API-based inference requires an internet connection.
- Semantic retrieval does not guarantee that every relevant passage will always be retrieved.

Retrieval grounding and source display help reduce, but cannot completely eliminate, hallucinations.

---

## 🚀 Future Scope

Future versions of KitaabGhar AI could include:

- Personalized book recommendations
- AI reading coach
- Flashcard generation
- Vocabulary assistant
- Reading analytics
- User accounts
- Persistent conversation history
- Multi-book knowledge bases
- Hybrid retrieval
- Reranking
- Additional document formats
- Improved RAG evaluation
- Local LLM inference

---

## 🎓 Academic Objective

KitaabGhar AI was developed as an end-to-end LLM and Retrieval-Augmented Generation project.

The project demonstrates the complete AI application lifecycle:

```text
Dataset Collection
        ↓
Data Processing
        ↓
Chunking
        ↓
Embedding Generation
        ↓
Vector Storage
        ↓
Semantic Retrieval
        ↓
Prompt Engineering
        ↓
LLM Generation
        ↓
Application Development
        ↓
Deployment
```

The project demonstrates practical understanding of:

- Large Language Models
- Embeddings
- Semantic Search
- Vector Databases
- Retrieval-Augmented Generation
- Prompt Engineering
- LLM Output Validation
- AI Application Architecture
- Streamlit Application Development

---

## 👩‍💻 Author

Developed as an MCA Major Project for the study and implementation of Large Language Models and Retrieval-Augmented Generation.

---

## 📄 License

This project is intended for educational and academic purposes.
