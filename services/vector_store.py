from langchain_community.vectorstores import FAISS

from services.embeddings import get_embedding_model


def create_vector_store(chunks):
    if not chunks:
        raise ValueError("No chunks were provided.")

    embeddings = get_embedding_model()

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    return vector_store


def save_vector_store(vector_store, path="vector_store/faiss_index"):
    vector_store.save_local(path)


def load_vector_store(path="vector_store/faiss_index"):
    embeddings = get_embedding_model()

    return FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True,
    )