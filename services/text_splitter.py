from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_book(documents):
    """
    Split book documents into smaller chunks for retrieval.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
    )

    chunks = splitter.split_documents(documents)

    return chunks