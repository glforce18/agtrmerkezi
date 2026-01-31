"""
AGTR Merkezi - Admin Shared Installation System Management
Shared template monitoring, disk usage analytics, maintenance tools
"""

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.common import BadRequestError, NotFoundError
from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import GameServer, ServerStatus, User

router = APIRouter()

# Cache for disk usage (5 minutes TTL)
_disk_cache: Dict[str, Tuple[dict, datetime]] = {}
_cache_ttl = timedelta(minutes=5)


def get_directory_size(path: Path) -> int:
    """Get directory size in MB using du command"""
    try:
        result = subprocess.run(
            ["du", "-sm", str(path)], capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return int(result.stdout.split()[0])
    except (subprocess.TimeoutExpired, ValueError):
        pass
    return 0


def get_mod_folder_for_server(server: GameServer) -> str:
    """Get mod folder name based on server game type"""
    mod_folders = {
        "ag": "ag",
        "hldm": "valve",
        "cs16": "cstrike",
    }
    game_type_value = (
        server.game_type.value if hasattr(server.game_type, "value") else str(server.game_type)
    )
    return mod_folders.get(game_type_value, "valve")


def check_template_health(template_dir: Path) -> Tuple[str, List[str]]:
    """
    Check template integrity and health

    Returns:
        (status, issues) - status is "healthy" or "degraded", issues is list of problems
    """
    issues = []

    # Check directory exists and is readable
    if not template_dir.exists():
        return "degraded", ["Template directory does not exist"]

    if not os.access(template_dir, os.R_OK):
        issues.append("Template directory not readable")

    # Check for required HLDS core files
    if template_dir.name == "hlds_base":
        required_files = ["hlds_linux", "hlds_run", "engine_i486.so"]
        for file_name in required_files:
            file_path = template_dir / file_name
            if not file_path.exists():
                issues.append(f"Missing required file: {file_name}")
            elif not os.access(file_path, os.X_OK):
                issues.append(f"File not executable: {file_name}")

    # Check for mod-specific directories
    if template_dir.name.endswith("_base") and template_dir.name != "hlds_base":
        required_dirs = ["dlls", "models", "sound", "sprites"]
        for dir_name in required_dirs:
            dir_path = template_dir / dir_name
            if not dir_path.exists():
                issues.append(f"Missing required directory: {dir_name}")
            elif not dir_path.is_dir():
                issues.append(f"Not a directory: {dir_name}")

    # Check for broken symlinks
    try:
        for item in template_dir.rglob("*"):
            if item.is_symlink() and not item.exists():
                issues.append(f"Broken symlink: {item.relative_to(template_dir)}")
    except PermissionError:
        issues.append("Permission denied while scanning for symlinks")

    # Check available disk space
    try:
        statvfs = os.statvfs(template_dir)
        free_gb = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)
        if free_gb < 1:
            issues.append(f"Critical: Low disk space ({free_gb:.1f} GB free)")
        elif free_gb < 5:
            issues.append(f"Warning: Low disk space ({free_gb:.1f} GB free)")
    except OSError:
        issues.append("Could not check disk space")

    status = "healthy" if not issues else "degraded"
    return status, issues


@router.get("/status")
async def get_shared_system_status(
    current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)
):
    """
    Get shared installation system status

    Returns:
        - Template list with sizes, file counts, health status
        - Total disk usage
        - Server count using shared system
        - Calculated disk savings
    """
    shared_base = Path("/home/gameservers/shared")

    if not shared_base.exists():
        raise NotFoundError("Shared base directory not found")

    templates = []

    # Scan all template directories
    for template_dir in sorted(shared_base.iterdir()):
        if not template_dir.is_dir():
            continue

        # Get directory size
        size_mb = get_directory_size(template_dir)

        # Count files
        try:
            file_count = sum(1 for _ in template_dir.rglob("*") if _.is_file())
        except PermissionError:
            file_count = 0

        # Check health
        status, issues = check_template_health(template_dir)

        # Get last modified time
        try:
            last_modified = datetime.fromtimestamp(template_dir.stat().st_mtime).isoformat()
        except OSError:
            last_modified = None

        templates.append(
            {
                "name": template_dir.name,
                "path": str(template_dir),
                "size_mb": size_mb,
                "file_count": file_count,
                "last_modified": last_modified,
                "status": status,
                "issues": issues,
            }
        )

    # Calculate total size
    total_size_mb = sum(t["size_mb"] for t in templates)

    # Count active servers (not deleted)
    server_count = db.query(GameServer).filter(GameServer.status != ServerStatus.DELETED).count()

    # Calculate disk savings vs full copy
    # From docs: Full copy = 839 MB, Shared system = ~350 MB per server
    full_copy_size = 839
    shared_size = 350
    savings_mb = (full_copy_size - shared_size) * server_count

    return {
        "shared_base_path": str(shared_base),
        "total_size_mb": total_size_mb,
        "templates": templates,
        "servers_using_shared": server_count,
        "disk_savings_mb": savings_mb,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/disk-usage")
async def get_disk_usage_analytics(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    force_refresh: bool = Query(False, description="Force cache refresh"),
):
    """
    Get detailed disk usage analytics with caching

    Cache TTL: 5 minutes

    Returns:
        - Overview: total, shared, individual disk usage
        - Per-server breakdown with subdirectory sizes
        - Top 10 disk consumers
    """
    cache_key = "disk_usage"
    now = datetime.utcnow()

    # Check cache
    if not force_refresh and cache_key in _disk_cache:
        cached_data, cached_time = _disk_cache[cache_key]
        if now - cached_time < _cache_ttl:
            cached_data["cached"] = True
            cached_data["cache_age_seconds"] = int((now - cached_time).total_seconds())
            return cached_data

    # Calculate fresh data
    servers_base = Path("/home/gameservers/servers")
    shared_base = Path("/home/gameservers/shared")

    # Get shared templates total size
    shared_mb = get_directory_size(shared_base)

    # Get all active servers from database
    servers = db.query(GameServer).filter(GameServer.status != ServerStatus.DELETED).all()

    per_server = []
    for server in servers:
        server_path = servers_base / f"server_{server.id}"

        if not server_path.exists():
            continue

        # Get total server size
        total_mb = get_directory_size(server_path)

        # Get breakdown by subdirectory
        breakdown = {}
        mod_folder = get_mod_folder_for_server(server)
        mod_path = server_path / mod_folder

        if mod_path.exists():
            for subdir in ["maps", "addons", "logs", "demos"]:
                subdir_path = mod_path / subdir
                if subdir_path.exists():
                    breakdown[f"{subdir}_mb"] = get_directory_size(subdir_path)

        per_server.append(
            {
                "server_id": server.id,
                "server_name": server.name,
                "owner_username": server.owner.username if server.owner else "unknown",
                "owner_id": server.owner_id,
                "game_type": (
                    server.game_type.value
                    if hasattr(server.game_type, "value")
                    else str(server.game_type)
                ),
                "disk_usage_mb": total_mb,
                "breakdown": breakdown,
            }
        )

    # Sort by disk usage (descending)
    per_server.sort(key=lambda x: x["disk_usage_mb"], reverse=True)

    # Get top 10 consumers
    top_consumers = [
        {
            "server_id": s["server_id"],
            "name": s["server_name"],
            "disk_mb": s["disk_usage_mb"],
            "owner_username": s["owner_username"],
        }
        for s in per_server[:10]
    ]

    # Calculate totals
    individual_mb = sum(s["disk_usage_mb"] for s in per_server)
    total_mb = shared_mb + individual_mb

    result = {
        "overview": {
            "total_disk_used_mb": total_mb,
            "shared_templates_mb": shared_mb,
            "individual_servers_mb": individual_mb,
            "servers_base_path": str(servers_base),
            "server_count": len(per_server),
        },
        "per_server": per_server,
        "top_consumers": top_consumers,
        "cached": False,
        "timestamp": now.isoformat(),
    }

    # Update cache
    _disk_cache[cache_key] = (result, now)

    return result


@router.post("/validate-template/{template_name}")
async def validate_template(
    template_name: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Validate template integrity and health

    Checks:
        - File permissions
        - Required files/directories exist
        - No broken symlinks
        - Sufficient disk space
    """
    # Validate template name (prevent path traversal)
    if "/" in template_name or "\\" in template_name or ".." in template_name:
        raise BadRequestError("Invalid template name")

    template_path = Path("/home/gameservers/shared") / template_name

    if not template_path.exists():
        raise NotFoundError(f"Template not found: {template_name}")

    if not template_path.is_dir():
        raise BadRequestError(f"Not a directory: {template_name}")

    # Run health check
    status, issues = check_template_health(template_path)

    # Get additional info
    size_mb = get_directory_size(template_path)
    file_count = sum(1 for _ in template_path.rglob("*") if _.is_file())

    return {
        "template_name": template_name,
        "status": status,
        "issues": issues,
        "size_mb": size_mb,
        "file_count": file_count,
        "validated_at": datetime.utcnow().isoformat(),
    }


@router.post("/cleanup-orphans")
async def cleanup_orphan_directories(
    confirm: bool = Query(False, description="Confirm deletion"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Find and optionally remove orphaned server directories

    Orphans are server directories with no corresponding database entry.

    - confirm=false: Preview mode (returns list, no deletion)
    - confirm=true: Actually delete orphaned directories
    """
    servers_base = Path("/home/gameservers/servers")

    if not servers_base.exists():
        return {"preview": not confirm, "orphans_found": 0, "orphans": [], "total_size_mb": 0}

    # Get all server IDs from database
    db_server_ids = {s.id for s in db.query(GameServer.id).all()}

    # Scan server directories
    orphans = []
    for item in servers_base.iterdir():
        if not item.is_dir():
            continue

        # Extract server ID from directory name
        match = re.match(r"server_(\d+)", item.name)
        if not match:
            # Directory doesn't match server_X pattern, skip
            continue

        server_id = int(match.group(1))

        # Check if server exists in database
        if server_id not in db_server_ids:
            size_mb = get_directory_size(item)
            orphans.append({"server_id": server_id, "path": str(item), "size_mb": size_mb})

    total_size_mb = sum(o["size_mb"] for o in orphans)

    # Preview mode - just return list
    if not confirm:
        return {
            "preview": True,
            "orphans_found": len(orphans),
            "orphans": orphans,
            "total_size_mb": total_size_mb,
            "message": "Call again with confirm=true to delete these directories",
        }

    # Deletion mode - actually remove directories
    deleted = []
    errors = []

    for orphan in orphans:
        try:
            shutil.rmtree(orphan["path"])
            deleted.append(orphan["server_id"])
        except Exception as e:
            errors.append({"server_id": orphan["server_id"], "error": str(e)})

    return {
        "preview": False,
        "deleted_count": len(deleted),
        "deleted": deleted,
        "errors": errors,
        "total_size_freed_mb": sum(o["size_mb"] for o in orphans if o["server_id"] in deleted),
    }


@router.get("/servers/{server_id}/installation-log")
async def get_installation_log(
    server_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    lines: int = Query(50, ge=10, le=500, description="Number of log lines to return"),
):
    """
    Get installation progress and logs for a server

    Parses uvicorn logs to extract server installation messages.
    Useful for monitoring ongoing installations or debugging failures.
    """
    # Verify server exists
    server = db.query(GameServer).filter(GameServer.id == server_id).first()
    if not server:
        raise NotFoundError("Server not found")

    log_entries = []
    errors = []

    # Read uvicorn log file
    log_path = Path("/var/www/agtrmerkezi/logs/uvicorn.log")

    if not log_path.exists():
        return {
            "server_id": server_id,
            "status": (
                server.status.value if hasattr(server.status, "value") else str(server.status)
            ),
            "log_entries": [],
            "errors": [],
            "message": "Log file not found",
        }

    try:
        # Read last 2000 lines of log
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()[-2000:]

        # Filter for this server
        server_patterns = [
            f"server_{server_id}",
            f"Server {server_id}",
            f"server_id={server_id}",
            f'server_id": {server_id}',
        ]

        for line in all_lines:
            # Check if line mentions this server
            if any(pattern in line for pattern in server_patterns):
                try:
                    # Try to parse as JSON
                    log_entry = json.loads(line.strip())
                    entry = {
                        "timestamp": log_entry.get("timestamp", ""),
                        "level": log_entry.get("level", "INFO"),
                        "message": log_entry.get("message", ""),
                        "module": log_entry.get("module", ""),
                    }
                    log_entries.append(entry)

                    if log_entry.get("level") in ["ERROR", "CRITICAL"]:
                        errors.append(entry)

                except (json.JSONDecodeError, ValueError):
                    # Not JSON, parse as plain text
                    log_entries.append(
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "level": "INFO",
                            "message": line.strip(),
                            "module": "unknown",
                        }
                    )

    except Exception as e:
        return {
            "server_id": server_id,
            "status": (
                server.status.value if hasattr(server.status, "value") else str(server.status)
            ),
            "log_entries": [],
            "errors": [],
            "message": f"Error reading log file: {str(e)}",
        }

    # Return last N entries
    return {
        "server_id": server_id,
        "server_name": server.name,
        "status": server.status.value if hasattr(server.status, "value") else str(server.status),
        "log_entries": log_entries[-lines:],
        "errors": errors,
        "total_entries": len(log_entries),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/cache/clear")
async def clear_disk_cache(current_admin: User = Depends(get_current_admin)):
    """Clear disk usage cache (force refresh on next request)"""
    global _disk_cache
    cache_size = len(_disk_cache)
    _disk_cache.clear()

    return {"cleared": True, "entries_cleared": cache_size, "message": "Disk usage cache cleared"}
