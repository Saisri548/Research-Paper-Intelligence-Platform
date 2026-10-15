
import re
from pathlib import Path
import fitz
MAX_PAGES = 300
class DocumentValidationError(Exception):
    """An expected document validation failure."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
def extract_text_from_pdf(file_path: str) -> dict:
    path = Path(file_path)

    try:
        with fitz.open(path) as pdf:
            if not pdf.is_pdf:
                raise DocumentValidationError(
                    "INVALID_PDF", "The uploaded file is not a valid PDF."
                )

            if pdf.needs_pass:
                raise DocumentValidationError(
                    "ENCRYPTED_PDF",
                    "Password-protected PDFs are not supported yet.",
                )

            total_pages = pdf.page_count

            if total_pages == 0:
                raise DocumentValidationError(
                    "EMPTY_PDF", "The PDF contains no pages."
                )

            if total_pages > MAX_PAGES:
                raise DocumentValidationError(
                    "PAGE_LIMIT_EXCEEDED",
                    f"The PDF exceeds the {MAX_PAGES}-page limit.",
                )

            pages = []
            failed_pages = []
            page_signatures = set()
            duplicate_pages = 0

            for page_number in range(total_pages):
                try:
                    page = pdf.load_page(page_number)
                    text = page.get_text("text").strip()
                    normalized = re.sub(r"\s+", " ", text).strip()

                    if normalized:
                        signature = normalized[:500].lower()

                        if signature in page_signatures:
                            duplicate_pages += 1

                        page_signatures.add(signature)

                        pages.append({
                            "page_number": page_number + 1,
                            "text": text,
                        })

                    else:
                        pages.append({
                            "page_number": page_number + 1,
                            "text": "",
                        })

                except Exception:
                    failed_pages.append(page_number + 1)
                    pages.append({
                        "page_number": page_number + 1,
                        "text": "",
                    })

            if failed_pages:
                raise DocumentValidationError(
                    "PAGE_EXTRACTION_FAILED",
                    f"Text extraction failed on pages: {failed_pages}.",
                )

            full_text = "\n\n".join(
                page["text"] for page in pages
            ).strip()

            alphanumeric_count = sum(
                character.isalnum() for character in full_text
            )

            character_count = len(full_text)
            quality_ratio = (
                alphanumeric_count / character_count
                if character_count else 0
            )

            empty_pages = sum(
                not page["text"].strip() for page in pages
            )

            return {
                "pages": pages,
                "total_pages": total_pages,
                "nonempty_pages": total_pages - empty_pages,
                "empty_pages": empty_pages,
                "character_count": character_count,
                "alphanumeric_ratio": round(quality_ratio, 3),
                "duplicate_page_count": duplicate_pages,
                "full_text": full_text,
            }

    except DocumentValidationError:
        raise
    except (fitz.FileDataError, RuntimeError, ValueError, OSError) as exc:
        raise DocumentValidationError(
            "INVALID_OR_CORRUPTED_PDF",
            "The PDF is corrupted, malformed, or cannot be opened.",
        ) from exc
