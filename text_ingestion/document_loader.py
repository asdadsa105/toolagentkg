"""Load plaintext and Markdown documents with deterministic provenance."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

SUPPORTED = {'.txt', '.md', '.markdown'}


@dataclass(frozen=True)
class Document:
    doc_id: str
    file_path: str
    content: str


def load_documents(source: str | Path) -> list[Document]:
    root = Path(source).resolve()
    if not root.exists():
        raise FileNotFoundError(f'输入不存在: {root}')
    paths = [root] if root.is_file() else sorted(
        p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED
    )
    if not paths:
        raise ValueError('没有找到 TXT/MD 文件（第一版暂不支持PDF和DOCX）')
    docs: list[Document] = []
    for p in paths:
        if p.suffix.lower() not in SUPPORTED:
            raise ValueError(f'不支持的格式: {p.name}; 当前支持 {sorted(SUPPORTED)}')
        try:
            text = p.read_text(encoding='utf-8-sig')
        except UnicodeDecodeError:
            text = p.read_text(encoding='gb18030')
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        if not text.strip():
            continue
        relative = p.relative_to(root) if root.is_dir() else Path(p.name)
        id_str = f'{relative.as_posix()}\n{text}'
        docs.append(Document(
            doc_id=sha256(id_str.encode('utf-8')).hexdigest()[:16],
            file_path=str(p), content=text
        ))
    if not docs:
        raise ValueError('所有输入文件均为空')
    return docs
