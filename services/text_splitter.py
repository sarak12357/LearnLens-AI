from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_book(documents):
    """
    Split uploaded learning material into retrieval-friendly chunks.

    The splitter tries to preserve paragraphs and dialogue before
    falling back to smaller text boundaries.
    """

    if not documents:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1400,
        chunk_overlap=250,

        separators=[
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            "; ",
            ", ",
            " ",
            "",
        ],

        length_function=len,
        is_separator_regex=False,
    )

    chunks = splitter.split_documents(
        documents
    )

    return chunks