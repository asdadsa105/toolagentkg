"""Heading-aware text chunking, followed by bounded token windows.

Inspired by LightRAG's fixed-token and structural chunking concepts, but not a
copy of LightRAG internals. Uses tiktoken when installed (otherwise a rough
character/word counter). The fallback is only for debugging, not token-exact.
"""
from dataclasses import dataclass
from pathlib import Path
import re
from .document_loader import Document

try:
    import tiktoken
    _ENCODING = tiktoken.get_encoding('cl100k_base')
except (ImportError, Exception):
    _ENCODING = None


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    file_path: str
    text: str
    section: str
    start_char: int
    end_char: int
    start_line: int
    end_line: int


def token_count(s: str) -> int:
    if _ENCODING is not None:
        return len(_ENCODING.encode(s))
    # Conservative rough estimate only; install tiktoken for accurate caps.
    return len(s) if s else 0


def _sections(text: str) -> list[tuple[int, int, str]]:
    headings = list(re.finditer(r'^#{1,6}[ \t]+(.+?)\s*$', text, flags=re.MULTILINE))
    if not headings:
        return [(0, len(text), '')]
    result = []
    if headings[0].start() > 0 and text[:headings[0].start()].strip():
        result.append((0, headings[0].start(), ''))
    context_headings = []
    for i, match in enumerate(headings):
        stop = headings[i+1].start() if i+1 < len(headings) else len(text)
        title = match.group(1).strip()
        # LightRAG-style heading glue: skip heading-only sections and use
        # their titles as context for the following nonempty section.
        if not text[match.end():stop].strip() and i+1 < len(headings):
            context_headings.append(title)
            continue
        label = ' → '.join((context_headings + [title])[-4:])
        result.append((match.start(), stop, label))
        context_headings=[]
    return result


def _max_end(text: str, start: int, cap: int) -> int:
    lo, hi, best = start + 1, len(text), start + 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if token_count(text[start:mid]) <= cap:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def _overlap_start(text: str, start: int, end: int, overlap: int) -> int:
    if overlap <= 0:
        return end
    lo, hi, ans = start + 1, end, end
    while lo <= hi:
        mid = (lo + hi) // 2
        if token_count(text[mid:end]) <= overlap:
            ans = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return ans


def split_document(doc: Document, size: int = 1200, overlap: int = 100) -> list[Chunk]:
    if size < 100 or not (0 <= overlap < size):
        raise ValueError('要求 size >= 100 且 0 <= overlap < size')
    chunks = []
    for a, b, heading in _sections(doc.content):
        local = doc.content[a:b]
        pos = 0
        while pos < len(local):
            if not local[pos:].strip():
                break
            end = _max_end(local, pos, size)
            if end < len(local):
                # Prefer ending at a paragraph/sentence boundary when one lies
                # within the last 30% of the available window.
                window = local[pos:end]
                lower = int(len(window)*0.70)
                boundaries = [m.end() for m in re.finditer(r'\n\n+|(?<=[。！？.!?])\s+', window)]
                acceptable = [x for x in boundaries if x >= lower]
                if acceptable:
                    end = pos + acceptable[-1]
            if end <= pos:
                raise RuntimeError('分块未前进')
            absolute_start, absolute_end = a + pos, a + end
            piece = doc.content[absolute_start:absolute_end]
            if piece.strip():
                start_line = 1 + doc.content.count('\n', 0, absolute_start)
                end_line = 1 + doc.content.count('\n', 0, max(absolute_start, absolute_end-1))
                chunks.append(Chunk(
                    chunk_id=f'{doc.doc_id}_c{len(chunks)+1:04d}',
                    doc_id=doc.doc_id, file_path=doc.file_path,
                    text=piece, section=heading, start_char=absolute_start,
                    end_char=absolute_end, start_line=start_line, end_line=end_line
                ))
            if end >= len(local):
                break
            next_pos = _overlap_start(local, pos, end, overlap)
            pos = min(end, max(pos + 1, next_pos))
    return chunks


def write_chunk_manifest(chunks: list[Chunk], destination: Path) -> None:
    import json
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps([{
        'chunk_id': c.chunk_id, 'file_path': c.file_path,
        'section': c.section, 'start_line': c.start_line,
        'end_line': c.end_line, 'text': c.text,
    } for c in chunks], ensure_ascii=False, indent=2), encoding='utf-8')
