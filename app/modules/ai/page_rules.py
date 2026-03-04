from typing import Any, Dict
from __future__ import annotations


PAGE_RULES: Dict[int, Dict[str, Any]] = {
    6:  {
            "chapter_count_range": (2, 3), 
            "intro_words": (180, 220), 
            "intro_paragraphs": (2, 2),
            "body_words": (1060, 1260), 
            "body_paragraphs": (9, 12),
            "conclusion_words": (180, 220), 
            "conclusion_paragraphs": (2, 2),
            "references_count": (2, 3)
        },
    8:  {
            "chapter_count_range": (3, 4), 
            "intro_words": (220, 260), 
            "intro_paragraphs": (2, 3),
            "body_words": (1900, 2100), 
            "body_paragraphs": (15, 20),
            "conclusion_words": (220, 260), 
            "conclusion_paragraphs": (2, 3),
            "references_count": (2, 3)
         },
    10: {
            "chapter_count_range": (4, 5), 
            "intro_words": (260, 300), 
            "intro_paragraphs": (3, 3),
            "body_words": (2740, 2940), 
            "body_paragraphs": (21, 28),
            "conclusion_words": (260, 300), 
            "conclusion_paragraphs": (3, 3),
            "references_count": (3, 4)
         },
    12: {
            "chapter_count_range": (4, 5), 
            "intro_words": (300, 340), 
            "intro_paragraphs": (3, 4),
            "body_words": (3580, 3780), 
            "body_paragraphs": (27, 36),
            "conclusion_words": (300, 340), 
            "conclusion_paragraphs": (3, 4),
            "references_count": (3, 4)
         },
    14: {
            "chapter_count_range": (4, 5), 
            "intro_words": (340, 380), 
            "intro_paragraphs": (3, 4),
            "body_words": (4420, 4620), 
            "body_paragraphs": (33, 44),
            "conclusion_words": (340, 380), 
            "conclusion_paragraphs": (3, 4),
            "references_count": (4, 5)
         },
    16: {
            "chapter_count_range": (4, 5), 
            "intro_words": (380, 420), 
            "intro_paragraphs": (4, 4),
            "body_words": (5260, 5460), 
            "body_paragraphs": (39, 52),
            "conclusion_words": (380, 420), 
            "conclusion_paragraphs": (4, 4),
            "references_count": (4, 5)
         },
    18: {
            "chapter_count_range": (4, 5), 
            "intro_words": (420, 460), 
            "intro_paragraphs": (4, 5),
            "body_words": (6200, 6300), 
            "body_paragraphs": (45, 60),
            "conclusion_words": (420, 460), 
            "conclusion_paragraphs": (4, 5),
            "references_count": (5, 6)
         },
    20: {
            "chapter_count_range": (4, 5), 
            "intro_words": (460, 500), 
            "intro_paragraphs": (5, 5),
            "body_words": (6940, 7140), 
            "body_paragraphs": (51, 68),
            "conclusion_words": (460, 500), 
            "conclusion_paragraphs": (5, 5),
            "references_count": (5, 6)
         },
}


def page_logic(pages: int) -> dict[str, int]:
    if pages not in PAGE_RULES:
        raise ValueError(f"pages={pages} not supported. Allowed: {sorted(PAGE_RULES)}")
    r = PAGE_RULES[pages]
    return {
        "chap_min": r["chapter_count_range"][0],
        "chap_max": r["chapter_count_range"][1],
        "intro_min_w": r["intro_words"][0],
        "intro_max_w": r["intro_words"][1],
        "intro_min_p": r["intro_paragraphs"][0],
        "intro_max_p": r["intro_paragraphs"][1],
        "body_min_w": r["body_words"][0],
        "body_max_w": r["body_words"][1],
        "conc_min_w": r["conclusion_words"][0],
        "conc_max_w": r["conclusion_words"][1],
        "conc_min_p": r["conclusion_paragraphs"][0],
        "conc_max_p": r["conclusion_paragraphs"][1],
        "ref_min": r["references_count"][0],
        "ref_max": r["references_count"][1],
    }

def words(text: str) -> int:
    return len((text or "").split())
