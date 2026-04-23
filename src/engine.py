"""
Detection and anonymization engine.
Works on plain text strings; callers handle file I/O and format preservation.
"""
import re
import copy
from dataclasses import dataclass, field
from typing import List, Optional
from patterns import BUILTIN_CATEGORIES


@dataclass
class Finding:
    category_id: str
    tag: str
    original: str
    start: int
    end: int
    line_number: int
    kept: bool = True   # True = will be replaced; False = user ignored it


def detect(text: str,
           enabled_ids: List[str],
           custom_patterns: List[dict]) -> List[Finding]:
    """
    Run all enabled patterns over `text`.
    Returns a deduplicated, sorted list of Finding objects.
    """
    findings: List[Finding] = []
    lines = text.splitlines(keepends=True)

    # Build line-start offset map
    offsets = []
    pos = 0
    for ln in lines:
        offsets.append(pos)
        pos += len(ln)

    def line_num_for(char_pos: int) -> int:
        for i, start in enumerate(offsets):
            if i + 1 < len(offsets):
                if start <= char_pos < offsets[i + 1]:
                    return i + 1
            else:
                return i + 1
        return 1

    # Builtin categories
    for cat in BUILTIN_CATEGORIES:
        if cat["id"] not in enabled_ids:
            continue
        for pat in cat["patterns"]:
            for m in pat.finditer(text):
                findings.append(Finding(
                    category_id=cat["id"],
                    tag=cat["tag"],
                    original=m.group(0),
                    start=m.start(),
                    end=m.end(),
                    line_number=line_num_for(m.start()),
                ))

    # Custom patterns
    for cp in custom_patterns:
        if not cp.get("pattern", "").strip():
            continue
        try:
            pat = re.compile(cp["pattern"])
        except re.error:
            continue
        tag = f"[{cp.get('name', 'CUSTOM').upper().replace(' ', '_')}]"
        for m in pat.finditer(text):
            findings.append(Finding(
                category_id="custom",
                tag=tag,
                original=m.group(0),
                start=m.start(),
                end=m.end(),
                line_number=line_num_for(m.start()),
            ))

    # Sort by position, deduplicate overlapping matches (keep longest)
    findings.sort(key=lambda f: (f.start, -(f.end - f.start)))
    deduped: List[Finding] = []
    last_end = -1
    for f in findings:
        if f.start >= last_end:
            deduped.append(f)
            last_end = f.end

    return deduped


def apply_redactions(text: str, findings: List[Finding]) -> str:
    """
    Replace kept findings with their tags in a single pass.
    """
    result = []
    cursor = 0
    for f in sorted(findings, key=lambda x: x.start):
        if not f.kept:
            continue
        result.append(text[cursor:f.start])
        result.append(f.tag)
        cursor = f.end
    result.append(text[cursor:])
    return "".join(result)
