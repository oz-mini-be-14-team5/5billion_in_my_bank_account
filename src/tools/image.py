from fastapi import HTTPException, UploadFile, status
from pathlib import Path
from uuid import uuid4
from config import storage_path

async def _process_image(upload: UploadFile, user_id: int) -> str:
    if not upload.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file requires a filename.",
        )
    img_extenstions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    extension = Path(upload.filename).suffix
    if extension.lower() not in img_extenstions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file"
        )
    image_dir = Path(storage_path) / "posts" / str(user_id)
    image_dir.mkdir(parents=True, exist_ok=True)
    destination = image_dir / f"{uuid4().hex}{extension}"
    try:
        contents = await upload.read()
        with destination.open("wb") as buffer:
            buffer.write(contents)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store image file: {exc}",
        ) from exc
    finally:
        await upload.close()
    return str(destination)