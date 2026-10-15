
import re


MINIMUM_CHARACTERS = 1000

SECTION_PATTERNS = {
    "abstract": r"\babstract\b",
    "introduction": r"\bintroduction\b",
    "methodology": (
        r"\b(methodology|methods|materials and methods|"
        r"experimental setup)\b"
    ),
    "results": r"\b(results|findings|experiments|evaluation)\b",
    "conclusion": r"\b(conclusion|conclusions|discussion)\b",
    "references": (
        r"\b(references|bibliography|works cited|"
        r"literature cited)\b"
    ),
}

NON_RESEARCH_SIGNALS = {
    "blog": r"\b(blog post|blog article)\b",
    "news": r"\b(breaking news|news article)\b",
    "presentation": r"\b(slide \d+ of \d+|speaker notes)\b",
    "assignment": r"\b(homework assignment|student assignment)\b",
    "textbook": r"\b(chapter \d+|textbook)\b",
    "proposal": r"\b(research proposal|project proposal)\b",
    "thesis": r"\b(thesis|dissertation)\b",
    "supplementary": (
        r"\b(supplementary materials|supplementary information)\b"
    ),
}


def validate_research_paper(
    text: str,
    total_pages: int,
    nonempty_pages: int,
    alphanumeric_ratio: float,
) -> dict:
    normalized = re.sub(r"\s+", " ", text).strip().lower()

    def result(status, reason, sections=None, flags=None):
        return {
            "status": status,
            "reason": reason,
            "matched_sections": sections or [],
            "flags": flags or [],
        }

    if not normalized:
        return result(
            "NEEDS_OCR",
            "No extractable text was found. The PDF may be scanned.",
        )

    if len(normalized) < MINIMUM_CHARACTERS:
        # Short content could be a short paper or just an abstract.
        return result(
            "REVIEW_REQUIRED",
            "The document contains too little text for reliable classification.",
        )

    if alphanumeric_ratio < 0.35:
        return result(
            "REVIEW_REQUIRED",
            "Extracted text has an unusually low alphanumeric ratio.",
        )

    if total_pages and nonempty_pages / total_pages < 0.5:
        return result(
            "REVIEW_REQUIRED",
            "Fewer than half of the pages contain extractable text.",
        )

    matched_sections = [
        name
        for name, pattern in SECTION_PATTERNS.items()
        if re.search(pattern, normalized)
    ]

    flags = [
        name
        for name, pattern in NON_RESEARCH_SIGNALS.items()
        if re.search(pattern, normalized)
    ]

    # Strong document-type signals: route for review instead of
    # automatically rejecting every document with these words.
    if flags:
        return result(
            "REVIEW_REQUIRED",
            "Possible non-paper document type detected.",
            matched_sections,
            flags,
        )

    required_sections = {"abstract", "introduction", "references"}

    if (
        len(matched_sections) >= 4
        and required_sections.issubset(matched_sections)
    ):
        return result(
            "ACCEPTED",
            "Academic research structure detected.",
            matched_sections,
        )

    return result(
        "REVIEW_REQUIRED",
        "Research-paper structure could not be confirmed confidently.",
        matched_sections,
    )
