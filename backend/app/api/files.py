"""文件上传 + 解析 — PDF / Word → 纯文本"""

import io
from fastapi import APIRouter, UploadFile, HTTPException, Depends
from ..core.auth_deps import get_current_user

router = APIRouter()


@router.post("/parse")
async def parse_file(
    file: UploadFile,
    user_id: str = Depends(get_current_user),
):
    """上传 PDF 或 Word 文件，返回提取的文本"""
    content = await file.read()
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        text = _parse_pdf(content)
    elif ext in ("docx", "doc"):
        text = _parse_docx(content)
    elif ext == "txt":
        text = content.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(400, detail=f"不支持的文件格式: .{ext}（支持 PDF/DOCX/TXT）")

    return {"filename": filename, "text": text.strip(), "length": len(text)}


def _parse_pdf(content: bytes) -> str:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise HTTPException(500, detail="PDF 解析库未安装，请运行 pip install PyPDF2")

    reader = PdfReader(io.BytesIO(content))
    parts = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            parts.append(t)
    return "\n".join(parts)


def _parse_docx(content: bytes) -> str:
    try:
        from docx import Document
    except ImportError:
        raise HTTPException(500, detail="Word 解析库未安装，请运行 pip install python-docx")

    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs if p.text)
