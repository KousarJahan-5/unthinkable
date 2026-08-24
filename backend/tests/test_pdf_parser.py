import os
import pytest
from app.services.pdf_parser import PDFParser, PDFParsingError


def test_pdf_parser_valid_text():
    text_content = "John Doe\nSoftware Engineer\nSkills: Python, SQL"
    raw_bytes = text_content.encode("utf-8")
    cleaned, meta = PDFParser.extract_text_from_bytes(raw_bytes, "resume.txt")
    assert "John Doe" in cleaned
    assert meta["file_type"] == "txt"


def test_pdf_parser_empty_file():
    with pytest.raises(PDFParsingError, match="empty"):
        PDFParser.extract_text_from_bytes(b"", "empty.txt")


def test_pdf_parser_corrupted_pdf():
    fake_bytes = b"This is not a real PDF binary content header"
    with pytest.raises(PDFParsingError, match="Corrupted or invalid"):
        PDFParser.extract_text_from_bytes(fake_bytes, "corrupt.pdf")


def test_pdf_parser_sample_pdf_file():
    pdf_path = "backend/data/sample_resumes/Alex_Chen_Senior_AI_FullStack.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        cleaned, meta = PDFParser.extract_text_from_bytes(pdf_bytes, "Alex_Chen.pdf")
        assert "Alex Chen" in cleaned
        assert "Python" in cleaned
        assert meta["page_count"] >= 1
