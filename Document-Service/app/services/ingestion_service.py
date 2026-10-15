
from pathlib import Path

from app.parsers.pdf_parser import extract_text_from_pdf
from app.services.research_validator import validate_research_paper


def process_pdf(
    file_path: str,
    original_filename: str | None = None,
) -> dict:
    extraction = extract_text_from_pdf(file_path)

    classification = validate_research_paper(
        text=extraction["full_text"],
        total_pages=extraction["total_pages"],
        nonempty_pages=extraction["nonempty_pages"],
        alphanumeric_ratio=extraction["alphanumeric_ratio"],
    )

    return {
        "filename": original_filename or Path(file_path).name,
        "file_validation": "PASSED",
        "page_count": extraction["total_pages"],
        "nonempty_pages": extraction["nonempty_pages"],
        "character_count": extraction["character_count"],
        "duplicate_page_count": 0,
        "research_validation": classification,
    }
