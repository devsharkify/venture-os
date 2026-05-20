from fastapi import APIRouter, HTTPException, UploadFile, File
import uuid
from database import db, logger, imagekit, IMAGEKIT_PUBLIC_KEY

router = APIRouter(prefix="/api")


def _extract_url(result) -> tuple[str, str]:
    """Pull (url, file_id) out of an imagekitio FileUploadResponse or dict."""
    if result is None:
        return "", ""
    # imagekitio v3+ returns a Pydantic-like model
    url = getattr(result, "url", None)
    file_id = getattr(result, "file_id", None)
    if url:
        return url, file_id or ""
    if isinstance(result, dict):
        return result.get("url", "") or "", result.get("file_id", "") or result.get("fileId", "") or ""
    # Try .model_dump() or .dict() if available
    try:
        d = result.model_dump() if hasattr(result, "model_dump") else result.dict()
        return d.get("url", "") or "", d.get("file_id", "") or d.get("fileId", "") or ""
    except Exception:
        return "", ""


def _ext(filename: str, default: str) -> str:
    if filename and "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    return default


@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        ext = _ext(file.filename or "", "png")
        
        result = imagekit.files.upload(
            file=content,
            file_name=f"img_{uuid.uuid4().hex[:12]}.{ext}",
            folder="/kaizer-news/",
            is_private_file=False,
            public_key=IMAGEKIT_PUBLIC_KEY,
            use_unique_file_name=True,
        )
        url, file_id = _extract_url(result)
        if not url:
            raise HTTPException(status_code=500, detail="Upload failed: no URL in response")
        return {"url": url, "file_id": file_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload/video")
async def upload_video(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        ext = _ext(file.filename or "", "mp4")
        
        result = imagekit.files.upload(
            file=content,
            file_name=f"vid_{uuid.uuid4().hex[:12]}.{ext}",
            folder="/kaizer-news/videos/",
            is_private_file=False,
            public_key=IMAGEKIT_PUBLIC_KEY,
            use_unique_file_name=True,
        )
        url, file_id = _extract_url(result)
        if not url:
            raise HTTPException(status_code=500, detail="Upload failed: no URL in response")
        return {"url": url, "file_id": file_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload/document")
async def upload_document(file: UploadFile = File(...)):
    try:
        ext = _ext(file.filename or "", "pdf")
        if ext not in {"pdf", "doc", "docx"}:
            raise HTTPException(status_code=400, detail=f"Only PDF/DOC/DOCX allowed (got .{ext})")
        content = await file.read()
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 15MB)")
        
        result = imagekit.files.upload(
            file=content,
            file_name=f"doc_{uuid.uuid4().hex[:12]}.{ext}",
            folder="/kaizer-news/documents/",
            is_private_file=False,
            public_key=IMAGEKIT_PUBLIC_KEY,
            use_unique_file_name=True,
        )
        url, file_id = _extract_url(result)
        if not url:
            raise HTTPException(status_code=500, detail="Upload failed: no URL in response")
        return {"url": url, "file_id": file_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
