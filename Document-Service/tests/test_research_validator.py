
from app.services.research_validator import validate_research_paper


def make_research_text():
    return """
    Abstract
    This research paper investigates a technical problem using experiments.

    Introduction
    The problem and its background are discussed in this section.

    Methodology
    We collected data and evaluated the proposed approach.

    Results
    The experimental results show measurable improvements.

    Conclusion
    The proposed approach has several useful applications.

    References
    Reference One. Reference Two. Reference Three.
    """ + ("Additional research details. " * 100)


def classify(text, pages=5, nonempty_pages=5, ratio=0.8):
    return validate_research_paper(
        text=text,
        total_pages=pages,
        nonempty_pages=nonempty_pages,
        alphanumeric_ratio=ratio,
    )


def test_research_paper_is_accepted():
    result = classify(make_research_text())
    assert result["status"] == "ACCEPTED"


def test_scanned_pdf_needs_ocr():
    result = classify("")
    assert result["status"] == "NEEDS_OCR"


def test_short_document_needs_review():
    result = classify("A short document.")
    assert result["status"] == "REVIEW_REQUIRED"


def test_poor_text_quality_needs_review():
    result = classify(make_research_text(), ratio=0.1)
    assert result["status"] == "REVIEW_REQUIRED"


def test_too_many_empty_pages_needs_review():
    result = classify(
        make_research_text(),
        pages=10,
        nonempty_pages=2,
    )
    assert result["status"] == "REVIEW_REQUIRED"


def test_missing_research_sections_needs_review():
    text = "General document content. " * 100
    result = classify(text)
    assert result["status"] == "REVIEW_REQUIRED"
