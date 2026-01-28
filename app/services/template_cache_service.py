"""
AGTR Merkezi v6.2 - Template Cache Service
Pre-download and cache game server templates for fast installation
"""

import asyncio
import hashlib
import logging
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.database import TemplateCache

logger = logging.getLogger(__name__)


class TemplateCacheService:
    """
    Template caching service for fast server installations.

    Instead of using rsync (slow), we:
    1. Pre-download templates as tar.gz archives
    2. Extract them on demand (3x faster than rsync)
    3. Validate and auto-update daily
    """

    # Cache storage
    CACHE_BASE = "/opt/agtr/templates"
    EXTRACT_BASE = "/home/gameservers/templates/hlds"

    # Template definitions
    TEMPLATE_DEFINITIONS = {
        "ag": {
            "name": "Adrenaline Gamer",
            "version": "6.6",
            "source_path": "/home/gameservers/templates/hlds/ag",
        },
        "ag_openag": {
            "name": "OpenAG",
            "version": "1.0",
            "source_path": "/home/gameservers/templates/hlds/ag_openag",
        },
        "cs16": {
            "name": "Counter-Strike 1.6",
            "version": "latest",
            "source_path": "/home/gameservers/templates/hlds/cstrike",
        },
        "hldm": {
            "name": "Half-Life Deathmatch",
            "version": "latest",
            "source_path": "/home/gameservers/templates/hlds/valve",
        },
        "valve_new": {
            "name": "Half-Life (New)",
            "version": "latest",
            "source_path": "/home/gameservers/templates/hlds/valvenewvalve",
        },
    }

    def __init__(self, db: Session):
        self.db = db
        self._ensure_cache_directory()

    def _ensure_cache_directory(self):
        """Create cache directory if it doesn't exist"""
        Path(self.CACHE_BASE).mkdir(parents=True, exist_ok=True)
        logger.info(f"Template cache directory: {self.CACHE_BASE}")

    def get_cache_path(self, mod_type: str) -> Path:
        """Get cache file path for a mod type"""
        return Path(self.CACHE_BASE) / f"{mod_type}.tar.gz"

    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    async def create_template_archive(
        self, mod_type: str, source_path: str
    ) -> Tuple[bool, str, Optional[Path]]:
        """
        Create tar.gz archive from template source.

        Args:
            mod_type: Mod type (ag, cs16, etc.)
            source_path: Source template directory

        Returns:
            (success, message, archive_path)
        """
        source = Path(source_path)

        if not source.exists():
            return False, f"Source template not found: {source_path}", None

        cache_file = self.get_cache_path(mod_type)

        try:
            # Create tar.gz archive
            logger.info(f"Creating template archive: {mod_type} from {source_path}")

            # Use tar command for better compression
            cmd = [
                "tar",
                "-czf",
                str(cache_file),
                "-C",
                str(source.parent),
                source.name,
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown tar error"
                logger.error(f"tar creation failed: {error_msg}")
                return False, f"Archive creation failed: {error_msg}", None

            # Calculate checksum and size
            checksum = self.calculate_checksum(cache_file)
            size_mb = cache_file.stat().st_size / (1024**2)

            logger.info(
                f"Template archive created: {cache_file.name} ({size_mb:.2f} MB, "
                f"checksum: {checksum[:16]}...)"
            )

            return True, "Archive created successfully", cache_file

        except Exception as e:
            logger.error(f"Archive creation error: {e}")
            return False, str(e), None

    async def extract_template_archive(self, mod_type: str, destination: Path) -> Tuple[bool, str]:
        """
        Extract cached template archive to destination.

        Args:
            mod_type: Mod type
            destination: Extraction destination

        Returns:
            (success, message)
        """
        cache_file = self.get_cache_path(mod_type)

        if not cache_file.exists():
            return False, f"Cache file not found: {cache_file}"

        try:
            # Remove destination if exists
            if destination.exists():
                shutil.rmtree(destination)

            # Create parent directory
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Extract tar.gz (much faster than rsync)
            logger.info(f"Extracting template: {cache_file} -> {destination}")

            with tarfile.open(cache_file, "r:gz") as tar:
                # Extract to parent, then rename
                tar.extractall(path=destination.parent)

            # Find extracted directory and rename if needed
            template_def = self.TEMPLATE_DEFINITIONS.get(mod_type)
            if template_def:
                source_name = Path(template_def["source_path"]).name
                extracted_path = destination.parent / source_name

                if extracted_path.exists() and extracted_path != destination:
                    extracted_path.rename(destination)

            logger.info(f"Template extracted successfully: {destination}")
            return True, "Extraction successful"

        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return False, str(e)

    async def cache_template(self, mod_type: str) -> Tuple[bool, str]:
        """
        Cache a template (create archive and store metadata).

        Args:
            mod_type: Mod type to cache

        Returns:
            (success, message)
        """
        template_def = self.TEMPLATE_DEFINITIONS.get(mod_type)

        if not template_def:
            return False, f"Unknown mod type: {mod_type}"

        # Create archive
        success, message, archive_path = await self.create_template_archive(
            mod_type, template_def["source_path"]
        )

        if not success:
            return False, message

        # Calculate metadata
        checksum = self.calculate_checksum(archive_path)
        size_mb = archive_path.stat().st_size / (1024**2)

        # Store/update in database
        cache_record = (
            self.db.query(TemplateCache).filter(TemplateCache.mod_type == mod_type).first()
        )

        if cache_record:
            # Update existing
            cache_record.template_name = template_def["name"]
            cache_record.version = template_def["version"]
            cache_record.file_path = str(archive_path)
            cache_record.file_size_mb = size_mb
            cache_record.checksum = checksum
            cache_record.is_active = True
            cache_record.last_updated = datetime.utcnow()
            cache_record.last_validated = datetime.utcnow()
        else:
            # Create new
            cache_record = TemplateCache(
                mod_type=mod_type,
                template_name=template_def["name"],
                version=template_def["version"],
                file_path=str(archive_path),
                file_size_mb=size_mb,
                checksum=checksum,
                is_active=True,
                last_updated=datetime.utcnow(),
                last_validated=datetime.utcnow(),
            )
            self.db.add(cache_record)

        self.db.commit()

        logger.info(f"Template cached: {mod_type} ({size_mb:.2f} MB, checksum: {checksum[:16]}...)")

        return True, f"Template cached successfully: {mod_type}"

    async def cache_all_templates(self) -> Dict[str, bool]:
        """
        Cache all defined templates.

        Returns:
            Dict mapping mod_type to success status
        """
        results = {}

        for mod_type in self.TEMPLATE_DEFINITIONS.keys():
            logger.info(f"Caching template: {mod_type}")
            success, message = await self.cache_template(mod_type)
            results[mod_type] = success

            if not success:
                logger.warning(f"Failed to cache {mod_type}: {message}")

        return results

    def validate_cache(self, mod_type: str) -> Tuple[bool, str]:
        """
        Validate cached template (check file exists and checksum matches).

        Args:
            mod_type: Mod type

        Returns:
            (is_valid, message)
        """
        cache_record = (
            self.db.query(TemplateCache).filter(TemplateCache.mod_type == mod_type).first()
        )

        if not cache_record:
            return False, "No cache record found"

        cache_file = Path(cache_record.file_path)

        if not cache_file.exists():
            return False, f"Cache file missing: {cache_file}"

        # Verify checksum
        current_checksum = self.calculate_checksum(cache_file)

        if current_checksum != cache_record.checksum:
            return False, "Checksum mismatch (file corrupted)"

        # Update last_validated
        cache_record.last_validated = datetime.utcnow()
        self.db.commit()

        return True, "Cache valid"

    def get_cache_info(self, mod_type: str) -> Optional[Dict]:
        """
        Get cache information for a mod type.

        Returns:
            Cache info dict or None
        """
        cache_record = (
            self.db.query(TemplateCache).filter(TemplateCache.mod_type == mod_type).first()
        )

        if not cache_record:
            return None

        return {
            "mod_type": cache_record.mod_type,
            "template_name": cache_record.template_name,
            "version": cache_record.version,
            "file_size_mb": cache_record.file_size_mb,
            "checksum": cache_record.checksum[:16] + "...",
            "is_active": cache_record.is_active,
            "last_updated": (
                cache_record.last_updated.isoformat() if cache_record.last_updated else None
            ),
            "last_validated": (
                cache_record.last_validated.isoformat() if cache_record.last_validated else None
            ),
        }

    def get_all_cached_templates(self) -> List[Dict]:
        """Get info for all cached templates"""
        caches = self.db.query(TemplateCache).all()

        return [
            {
                "mod_type": cache.mod_type,
                "template_name": cache.template_name,
                "version": cache.version,
                "file_size_mb": cache.file_size_mb,
                "is_active": cache.is_active,
                "last_updated": cache.last_updated.isoformat() if cache.last_updated else None,
            }
            for cache in caches
        ]

    def is_cache_available(self, mod_type: str) -> bool:
        """Check if cache is available for a mod type"""
        cache_record = (
            self.db.query(TemplateCache)
            .filter(TemplateCache.mod_type == mod_type, TemplateCache.is_active == True)
            .first()
        )

        if not cache_record:
            return False

        cache_file = Path(cache_record.file_path)
        return cache_file.exists()

    def get_cache_stats(self) -> Dict:
        """Get overall cache statistics"""
        total_caches = self.db.query(TemplateCache).count()
        active_caches = self.db.query(TemplateCache).filter(TemplateCache.is_active == True).count()

        total_size = (
            self.db.query(TemplateCache)
            .with_entities(func.sum(TemplateCache.file_size_mb))
            .scalar()
            or 0.0
        )

        return {
            "total_templates": total_caches,
            "active_templates": active_caches,
            "total_size_mb": round(total_size, 2),
            "cache_directory": self.CACHE_BASE,
        }


# ==================== DAILY CACHE UPDATE TASK ====================


async def update_template_caches(db: Session) -> Dict:
    """
    Daily scheduled task to update template caches.

    Runs at 3 AM daily.
    """
    service = TemplateCacheService(db)

    logger.info("Starting daily template cache update...")

    # Cache all templates
    results = await service.cache_all_templates()

    # Validate all caches
    validation_results = {}
    for mod_type in service.TEMPLATE_DEFINITIONS.keys():
        is_valid, message = service.validate_cache(mod_type)
        validation_results[mod_type] = is_valid

    # Get stats
    stats = service.get_cache_stats()

    success_count = sum(1 for success in results.values() if success)
    valid_count = sum(1 for valid in validation_results.values() if valid)

    logger.info(
        f"Template cache update complete: {success_count}/{len(results)} cached, "
        f"{valid_count}/{len(validation_results)} valid, "
        f"Total size: {stats['total_size_mb']} MB"
    )

    return {
        "cache_results": results,
        "validation_results": validation_results,
        "stats": stats,
    }


# Import fix for func
from sqlalchemy.sql import func
