from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

STATIC_ROOT = Path(__file__).resolve().parent.parent / "static"
STATIC_HTML_DIR = STATIC_ROOT / "html"
STATIC_DIR = STATIC_ROOT / "ast"
STATIC_RESPONSE_DIR = STATIC_ROOT / "response"
INDEX_FILE = STATIC_HTML_DIR / "index.html"
NOT_FOUND_FILE = STATIC_RESPONSE_DIR / "404.html"

router = APIRouter(tags=["static"], include_in_schema=False)

@router.get("/")
async def serve_index():
    return FileResponse(INDEX_FILE)

@router.get("/ast/{asset_path:path}")
async def serve_asset(asset_path: str):
    asset_file = STATIC_DIR / asset_path
    if not asset_file.exists():
        return {"detail": "Asset not found"}, 404
    return FileResponse(asset_file)

@router.get("/{full_path:path}")
async def serve_static(full_path: str):

    if full_path.startswith("src/"):
        return FileResponse(NOT_FOUND_FILE, status_code=404)

    target = STATIC_HTML_DIR / full_path

    if target.is_dir():
        target = target / "index.html"
    elif target.suffix == "":
        html_candidate = target.with_suffix(".html")
        if html_candidate.exists():
            target = html_candidate

    if not target.exists():
        return FileResponse(NOT_FOUND_FILE, status_code=404)

    return FileResponse(target)
