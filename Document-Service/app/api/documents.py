
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.parsers.pdf_parser import DocumentValidationError
from app.services.ingestion_service import process_pdf


router = APIRouter(prefix="/documents", tags=["Documents"])

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name

    if not filename or Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            total_bytes = 0
            header = b""

            while chunk := await file.read(CHUNK_SIZE):
                total_bytes += len(chunk)

                if total_bytes > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 25 MB upload limit.",
                    )

                if len(header) < 1024:
                    header += chunk[: 1024 - len(header)]

                temp_file.write(chunk)

        if total_bytes == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        if b"%PDF-" not in header:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file does not have a valid PDF header.",
            )

        result = process_pdf(str(temp_path),original_filename=filename)
        research = result["research_validation"]

        # Only accepted research papers can continue downstream.
        if research["status"] != "ACCEPTED":
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Document did not pass research validation.",
                    "research_validation": research,
                },
            )

        return {
            "message": "Research paper validated successfully.",
            "status": "ACCEPTED",
            "document": result,
        }

    except DocumentValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": exc.code,
                "message": exc.message,
            },
        ) from exc

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

        await file.close()
