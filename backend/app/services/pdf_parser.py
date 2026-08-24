import io
import os
import pymupdf
from typing import Tuple, Dict, Any
from app.utils.text_cleaner import clean_text


class PDFParsingError(Exception):
    """Custom exception raised when PDF parsing fails."""
    pass


class PDFParser:
    """Robust extractor for PDF and text resumes with safety and edge-case handling."""

    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text from raw file bytes.
        Supports: PDF, TXT, MD
        Returns: (cleaned_text, metadata_dict)
        """
        if not file_bytes or len(file_bytes.strip()) == 0:
            raise PDFParsingError("File is empty (0 bytes).")

        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        metadata: Dict[str, Any] = {
            "filename": filename,
            "file_size": len(file_bytes),
            "file_type": ext,
            "page_count": 1,
            "is_scanned": False,
        }

        if ext in ["txt", "md"]:
            try:
                raw_text = file_bytes.decode("utf-8", errors="replace")
                cleaned = clean_text(raw_text)
                if not cleaned:
                    raise PDFParsingError("Text file is empty or contains only whitespace.")
                return cleaned, metadata
            except Exception as e:
                raise PDFParsingError(f"Failed to read text file: {str(e)}")

        elif ext == "pdf":
            try:
                # Open PDF from stream
                doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            except Exception as e:
                raise PDFParsingError(f"Corrupted or invalid PDF file: {str(e)}")

            if doc.page_count == 0:
                doc.close()
                raise PDFParsingError("PDF contains 0 pages.")

            metadata["page_count"] = doc.page_count
            extracted_pages = []
            total_raw_len = 0

            for page_idx in range(doc.page_count):
                try:
                    page = doc.load_page(page_idx)
                    page_text = page.get_text("text")
                    if page_text:
                        extracted_pages.append(page_text)
                        total_raw_len += len(page_text.strip())
                except Exception as e:
                    # Log page error but continue other pages
                    continue

            doc.close()

            # Check if PDF appears to be image-only / scanned
            if total_raw_len < 30:
                metadata["is_scanned"] = True
                raise PDFParsingError(
                    "No selectable text found. This document appears to be an image-only/scanned PDF without an embedded text layer."
                )

            combined_raw = "\n\n".join(extracted_pages)
            cleaned = clean_text(combined_raw)

            if len(cleaned.strip()) < 15:
                raise PDFParsingError("Extracted text is too short to be a valid resume.")

            return cleaned, metadata

        else:
            raise PDFParsingError(f"Unsupported file format '.{ext}'. Please upload a PDF or text file.")
