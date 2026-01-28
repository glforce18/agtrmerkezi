"""
AGTR Merkezi v6.0 - File Manager API
Dosya yonetimi API'leri
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import GameServer, User
from app.services.file_manager import FileManagerService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/servers/{server_id}/files", tags=["FileManager"])


# ============================================
# Pydantic Schemas
# ============================================


class FileWrite(BaseModel):
    """Dosya yazma istegi"""

    content: str


class DirectoryCreate(BaseModel):
    """Dizin olusturma istegi"""

    name: str


class BatchDownloadRequest(BaseModel):
    """Toplu dosya indirme istegi"""

    file_paths: list[str]


class RenameRequest(BaseModel):
    """Dosya yeniden adlandirma istegi"""

    new_name: str


# ============================================
# Helper Functions
# ============================================


async def verify_server_ownership(server_id: int, current_user: User, db: Session) -> GameServer:
    """
    Sunucu sahipligini dogrula

    Admin/Superadmin kullanıcılar tüm sunuculara erişebilir
    """
    from app.models.database import UserRole

    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Admin bypass - admin kullanıcılar tüm sunuculara erişebilir
    if current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        return server

    # Normal kullanıcı - sadece kendi sunucusu
    if server.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return server


# ============================================
# API Endpoints
# ============================================


@router.get("/browse")
async def browse_directory(
    server_id: int,
    path: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Sunucu dizinini goz at

    Args:
        server_id: Sunucu ID
        path: Dizin yolu (varsayilan root)

    Returns:
        Dosya ve dizin listesi
    """
    await verify_server_ownership(server_id, current_user, db)

    file_manager = FileManagerService()
    return file_manager.list_directory(server_id, path)


@router.get("/read")
async def read_file(
    server_id: int,
    path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Dosya icerigini oku

    Args:
        server_id: Sunucu ID
        path: Dosya yolu

    Returns:
        Dosya icerigi ve metadata
    """
    await verify_server_ownership(server_id, current_user, db)

    file_manager = FileManagerService()
    return file_manager.read_file(server_id, path)


@router.post("/write")
async def write_file(
    server_id: int,
    path: str,
    data: FileWrite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Dosyaya yaz

    Args:
        server_id: Sunucu ID
        path: Dosya yolu
        data: Dosya icerigi

    Returns:
        Basari mesaji
    """
    await verify_server_ownership(server_id, current_user, db)

    file_manager = FileManagerService()
    return file_manager.write_file(server_id, path, data.content, current_user.id)


@router.post("/upload")
async def upload_file(
    server_id: int,
    directory: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Sunucuya dosya yukle

    Args:
        server_id: Sunucu ID
        directory: Hedef dizin
        file: Yuklenen dosya

    Returns:
        Upload sonucu
    """
    await verify_server_ownership(server_id, current_user, db)

    file_manager = FileManagerService()
    return await file_manager.upload_file(db, server_id, directory, file, current_user.id)


@router.delete("/delete")
async def delete_file(
    server_id: int,
    path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Dosya/dizin sil

    Args:
        server_id: Sunucu ID
        path: Dosya/dizin yolu

    Returns:
        Silme sonucu
    """
    await verify_server_ownership(server_id, current_user, db)

    file_manager = FileManagerService()
    return file_manager.delete_file(server_id, path, current_user.id)


@router.post("/mkdir")
async def create_directory(
    server_id: int,
    parent_path: str,
    data: DirectoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Yeni dizin olustur

    Args:
        server_id: Sunucu ID
        parent_path: Ust dizin
        data: Yeni dizin adi

    Returns:
        Olusturma sonucu
    """
    await verify_server_ownership(server_id, current_user, db)

    file_manager = FileManagerService()
    return file_manager.create_directory(server_id, parent_path, data.name, current_user.id)


# ==================== WEBFTP ENHANCED ENDPOINTS ====================


@router.get("/tree")
async def get_directory_tree(
    server_id: int,
    path: str = "",
    max_depth: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Get hierarchical directory tree

    Args:
        server_id: Server ID
        path: Starting path (empty = root)
        max_depth: Maximum recursion depth (1-10)

    Returns:
        Tree structure with metadata
    """
    await verify_server_ownership(server_id, current_user, db)

    # Validate max_depth
    if max_depth < 1 or max_depth > 10:
        raise HTTPException(400, "max_depth must be between 1 and 10")

    file_manager = FileManagerService()
    return file_manager.get_directory_tree(db, server_id, path, max_depth)


@router.get("/download")
async def download_file(
    server_id: int,
    path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Download a single file

    Args:
        server_id: Server ID
        path: File path relative to cstrike/

    Returns:
        StreamingResponse with file content
    """
    await verify_server_ownership(server_id, current_user, db)

    if not path:
        raise HTTPException(400, "path parameter is required")

    file_manager = FileManagerService()
    return await file_manager.download_file(db, server_id, path)


@router.post("/batch-download")
async def batch_download_files(
    server_id: int,
    data: BatchDownloadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Download multiple files as ZIP

    Args:
        server_id: Server ID
        data: List of file paths

    Returns:
        ZIP archive
    """
    await verify_server_ownership(server_id, current_user, db)

    if not data.file_paths:
        raise HTTPException(400, "file_paths cannot be empty")

    file_manager = FileManagerService()
    zip_bytes = await file_manager.batch_download(db, server_id, data.file_paths)

    from fastapi.responses import Response

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="server_{server_id}_files.zip"'},
    )


@router.get("/permissions")
async def get_file_permissions(
    server_id: int,
    path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Get file Unix permissions

    Args:
        server_id: Server ID
        path: File path

    Returns:
        Permission info (mode, octal, owner, group, flags)
    """
    await verify_server_ownership(server_id, current_user, db)

    if not path:
        raise HTTPException(400, "path parameter is required")

    from pathlib import Path

    SERVERS_BASE = "/home/gameservers/servers"
    server_path = Path(SERVERS_BASE) / f"server_{server_id}" / "cstrike"
    file_path = server_path / path

    file_manager = FileManagerService()
    return file_manager.get_file_permissions(file_path)


@router.post("/rename")
async def rename_file(
    server_id: int,
    old_path: str,
    data: RenameRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Rename file or directory

    Args:
        server_id: Server ID
        old_path: Current file path
        data: New filename

    Returns:
        Rename result
    """
    await verify_server_ownership(server_id, current_user, db)

    if not old_path:
        raise HTTPException(400, "old_path parameter is required")

    if not data.new_name:
        raise HTTPException(400, "new_name cannot be empty")

    file_manager = FileManagerService()
    return await file_manager.rename_file(db, server_id, old_path, data.new_name, current_user.id)


@router.post("/upload")
async def upload_file(
    server_id: int,
    target_directory: str,
    file: UploadFile = File(...),
    overwrite: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Upload file to server

    Args:
        server_id: Server ID
        target_directory: Target directory (must be whitelisted)
        file: File to upload
        overwrite: Allow overwriting existing files

    Returns:
        Upload result
    """
    await verify_server_ownership(server_id, current_user, db)

    if not target_directory:
        raise HTTPException(400, "target_directory parameter is required")

    file_manager = FileManagerService()
    return await file_manager.upload_file(
        db, server_id, target_directory, file, current_user.id, overwrite
    )
