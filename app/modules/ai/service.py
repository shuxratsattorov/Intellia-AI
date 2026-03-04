# app/modules/ai/service.py
from __future__ import annotations
from typing import Generator, List, Optional

from app.core.config import settings
from app.integrations.ai.client import AIClient
from app.integrations.ai.prompts import load_prompt
from app.integrations.ai import safety
from .page_rules import page_logic, words

def build_system_prompt(*, topic: str, language: str, level: str) -> str:
    # Global context SYSTEM'da: promptlar kichrayadi va izchillik oshadi
    return (
        "You are a professional academic writing assistant. "
        "Write original, formal academic text. No plagiarism. No emojis.\n"
        f"Language: {language}\n"
        f"Academic level: {level}\n"
        f"Topic: {topic}\n"
    )

def choose_model(is_premium: bool) -> str:
    return settings.OPENAI_MODEL_PREMIUM if is_premium else settings.OPENAI_MODEL_FREE

def extract_between(text: str, a: str, b: str) -> str:
    if a not in text or b not in text:
        return ""
    return text.split(a, 1)[1].split(b, 1)[0].strip()

def calc_chapter_min_words(rules: dict, total_target_words: Optional[int]) -> tuple[int, int]:
    """
    Qancha bob yozish va har bob minimum so‘z.
    Hozircha: chap_minni olamiz (stable).
    Keyin heuristic qo‘shamiz (topic length, complexity).
    """
    chap_count = rules["chap_min"]
    if total_target_words:
        # intro+conclusion minimumlarini ayiramiz
        body_target = max(0, total_target_words - (rules["intro_min_w"] + rules["conc_min_w"]))
        per_ch = max(250, body_target // chap_count)
        return chap_count, per_ch

    # default: page_rules body_min_w ni bobga bo‘lamiz
    body_min = rules["body_min_w"]
    per_ch = max(250, body_min // chap_count)
    return chap_count, per_ch

def generate_until_min_stream(
    *,
    ai: AIClient,
    model: str,
    system: str,
    first_prompt: str,
    min_words: int,
    continue_tag: str,
) -> Generator[str, None, str]:
    """
    1) Sectionni stream qiladi
    2) Min so‘zga yetmasa yoki continue_tag bo‘lsa, auto-continue qiladi
    3) Return: full section text
    """
    full = ""
    user_prompt = first_prompt

    while True:
        chunk = ""
        for piece in ai.stream(
            model=model,
            system=system,
            user=user_prompt,
            max_tokens=1800,
            temperature=settings.AI_TEMPERATURE,
        ):
            chunk += piece
            yield piece

        full += chunk

        hit_continue = continue_tag in chunk
        if hit_continue:
            full = full.replace(continue_tag, "").rstrip()

        if words(full) >= min_words and not hit_continue:
            return full

        # continue request
        current = words(full)
        user_prompt = (
            "Continue EXACTLY where you stopped. Do not repeat. "
            "Keep the same section only.\n"
            f"Current words: {current}. Minimum required: {min_words}.\n"
            f"If still unfinished, end with {continue_tag}."
        )

def generate_report_stream(
    *,
    topic: str,
    language: str,
    education_level: str,
    citation_style: str,
    pages: int,
    is_premium: bool,
    total_target_words: Optional[int] = None,
) -> Generator[dict, None, None]:
    # ---- Safety validations ----
    topic = safety.ensure_len("topic", topic, 200)
    language = safety.ensure_in_set("language", language, safety.ALLOWED_LANG)
    education_level = safety.ensure_in_set("education_level", education_level, safety.ALLOWED_LEVEL)

    rules = page_logic(pages)
    ai = AIClient()
    model = choose_model(is_premium)
    system = build_system_prompt(topic=topic, language=language, level=education_level)

    # ---- 1) Outline + Global Brief ----
    yield {"type": "status", "data": "Generating outline + global brief..."}
    tpl = load_prompt("outline_brief.txt")
    outline_prompt = tpl.format(
        topic=topic,
        language=language,
        education_level=education_level,
        chap_min=rules["chap_min"],
        chap_max=rules["chap_max"],
    )
    outline = ai.complete(model=model, system=system, user=outline_prompt, max_tokens=1400, temperature=0.4)
    toc = extract_between(outline, "[TOC]", "[/TOC]") or outline
    brief = extract_between(outline, "[BRIEF]", "[/BRIEF]") or ""

    yield {"type": "toc", "data": toc}
    yield {"type": "brief", "data": brief}

    # ---- Word budget plan ----
    chap_count, per_ch_min = calc_chapter_min_words(rules, total_target_words)

    # ---- 2) Intro ----
    yield {"type": "status", "data": "Generating introduction..."}
    intro_tpl = load_prompt("intro.txt")
    intro_prompt = intro_tpl.format(
        global_brief=brief,
        toc=toc,
        intro_min_w=rules["intro_min_w"],
        intro_max_w=rules["intro_max_w"],
        intro_min_p=rules["intro_min_p"],
        intro_max_p=rules["intro_max_p"],
    )
    intro_text = yield from generate_until_min_stream(
        ai=ai, model=model, system=system,
        first_prompt=intro_prompt,
        min_words=rules["intro_min_w"],
        continue_tag="[CONTINUE_INTRO]",
    )
    yield {"type": "section_done", "data": "intro"}

    # ---- 3) Chapters + Recaps ----
    recaps: List[str] = []
    for ch_no in range(1, chap_count + 1):
        yield {"type": "status", "data": f"Generating chapter {ch_no}..."}
        chapter_tpl = load_prompt("chapter.txt")

        # Hozircha minimal: keyin TOC parser qilib ch_no ga mos block ajratamiz
        chapter_outline_block = f"{ch_no} BOB. (use TOC titles)\n{ch_no}.1. ...\n{ch_no}.2. ..."

        prev_recap = recaps[-1] if recaps else "None"
        chapter_prompt = chapter_tpl.format(
            chapter_no=ch_no,
            global_brief=brief,
            prev_recap=prev_recap,
            chapter_outline_block=chapter_outline_block,
            chapter_min_words=per_ch_min,
        )

        chapter_text = yield from generate_until_min_stream(
            ai=ai, model=model, system=system,
            first_prompt=chapter_prompt,
            min_words=per_ch_min,
            continue_tag=f"[CONTINUE_CH{ch_no}]",
        )
        yield {"type": "section_done", "data": f"chapter_{ch_no}"}

        # Recap (tiny call)
        recap_tpl = load_prompt("recap.txt")
        recap = ai.complete(
            model=model,
            system=system,
            user=f"{recap_tpl}\n\nCHAPTER TEXT:\n{chapter_text}",
            max_tokens=450,
            temperature=0.2,
        )
        recaps.append(recap)
        yield {"type": "recap", "data": recap}

    # ---- 4) Conclusion ----
    yield {"type": "status", "data": "Generating conclusion..."}
    conc_tpl = load_prompt("conclusion.txt")
    conc_prompt = conc_tpl.format(
        global_brief=brief,
        conc_min_w=rules["conc_min_w"],
        conc_max_w=rules["conc_max_w"],
        conc_min_p=rules["conc_min_p"],
        conc_max_p=rules["conc_max_p"],
    )
    _ = yield from generate_until_min_stream(
        ai=ai, model=model, system=system,
        first_prompt=conc_prompt,
        min_words=rules["conc_min_w"],
        continue_tag="[CONTINUE_CONC]",
    )
    yield {"type": "section_done", "data": "conclusion"}

    # ---- 5) References ----
    yield {"type": "status", "data": "Generating references..."}
    ref_tpl = load_prompt("references.txt")
    ref_prompt = ref_tpl.format(
        topic=topic,
        language=language,
        citation_style=citation_style,
        ref_min=rules["ref_min"],
        ref_max=rules["ref_max"],
    )
    refs = ai.complete(model=model, system=system, user=ref_prompt, max_tokens=900, temperature=0.3)
    yield {"type": "references", "data": refs}

    # ---- 6) Final consistency pass ----
    yield {"type": "status", "data": "Final consistency check..."}
    final_tpl = load_prompt("final_check.txt")
    final_prompt = final_tpl.format(
        global_brief=brief,
        toc=toc,
        recaps="\n".join(recaps),
    )
    check = ai.complete(model=model, system=system, user=final_prompt, max_tokens=650, temperature=0.2)
    yield {"type": "final_check", "data": check}

    yield {"type": "done", "data": "Report generation complete."}
