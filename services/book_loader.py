import re
from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


SUPPORTED_TYPES = [".txt", ".pdf"]


def clean_text(text):
    """
    Basic text cleaning.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def load_txt(file):
    """
    Extract text from uploaded TXT file.
    """

    raw_data = file.getvalue()

    text = raw_data.decode(
        "utf-8",
        errors="ignore"
    )

    return clean_text(text)


def load_pdf(file):
    """
    Extract text from uploaded PDF.
    """

    reader = PdfReader(file)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):
        text = page.extract_text()

        if text:
            pages.append(text)

    combined_text = "\n\n".join(pages)

    return clean_text(combined_text)


def load_uploaded_book(file):
    """
    Validate and process an uploaded book.
    """

    if file is None:
        raise ValueError(
            "Please upload a book first."
        )

    extension = Path(
        file.name
    ).suffix.lower()

    if extension not in SUPPORTED_TYPES:
        raise ValueError(
            "Only PDF and TXT files are supported."
        )

    if extension == ".txt":
        text = load_txt(file)

    else:
        text = load_pdf(file)

    if not text:
        raise ValueError(
            "No readable text was found in the uploaded book."
        )

    # Basic dataset validation
    if len(text) < 500:
        raise ValueError(
            "The uploaded document contains too little text."
        )

    metadata = {
        "source": file.name,
        "book_name": Path(file.name).stem,
        "file_type": extension.replace(".", ""),
        "character_count": len(text),
    }

    document = Document(
        page_content=text,
        metadata=metadata
    )

    return [document]