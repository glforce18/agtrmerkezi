"""
AGTR Merkezi v5.0 - Backup System
Otomatik yedekleme sistemi
"""

import logging
import os
import tarfile
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

BACKUP_DIR = "/var/backups/agtrmerkezi"


class BackupManager:
    """Yedekleme yoneticisi"""
    
    def __init__(self, backup_dir: str = BACKUP_DIR):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    async def backup_database(self) -> dict:
        """MySQL database yedekle"""
        from app.core.config import settings
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"db_backup_{timestamp}.sql"
        filepath = self.backup_dir / filename
        
        try:
            # mysqldump komutu - guvenli versiyon
            import gzip
            import subprocess

            # Environment variable ile sifre gonder (komut satirinda gorunmez)
            env = os.environ.copy()
            env['MYSQL_PWD'] = settings.DB_PASSWORD

            # Guvenli mysqldump komutu (shell=False)
            mysqldump_cmd = [
                'mysqldump',
                f'-u{settings.DB_USER}',
                f'-h{settings.DB_HOST}',
                f'-P{settings.DB_PORT}',
                settings.DB_NAME
            ]

            result = subprocess.run(
                mysqldump_cmd,
                capture_output=True,
                env=env,
                timeout=300
            )

            if result.returncode != 0:
                raise Exception(result.stderr.decode())

            # Compress - dogrudan gzip'e yaz
            compressed = f"{filepath}.gz"
            with gzip.open(compressed, 'wb') as f_out:
                f_out.write(result.stdout)
            
            file_size = os.path.getsize(compressed)
            
            logger.info(f"Database backup created: {compressed} ({file_size} bytes)")
            return {
                "success": True,
                "filename": os.path.basename(compressed),
                "path": compressed,
                "size": file_size,
                "created_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def backup_server_configs(self, server_id: int, server_path: str) -> dict:
        """Sunucu config dosyalarini yedekle"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"server_{server_id}_config_{timestamp}.tar.gz"
        filepath = self.backup_dir / filename
        
        try:
            config_files = [
                "server.cfg",
                "mapcycle.txt",
                "motd.txt",
                "users.ini",
                "plugins.ini"
            ]
            
            with tarfile.open(filepath, "w:gz") as tar:
                for cfg in config_files:
                    cfg_path = Path(server_path) / cfg
                    if cfg_path.exists():
                        tar.add(cfg_path, arcname=cfg)
            
            file_size = os.path.getsize(filepath)
            
            logger.info(f"Server config backup: {filepath} ({file_size} bytes)")
            return {
                "success": True,
                "filename": filename,
                "path": str(filepath),
                "size": file_size,
                "server_id": server_id
            }
        except Exception as e:
            logger.error(f"Config backup failed for server {server_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def backup_full_server(self, server_id: int, server_path: str) -> dict:
        """Tam sunucu yedegi"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"server_{server_id}_full_{timestamp}.tar.gz"
        filepath = self.backup_dir / filename
        
        try:
            with tarfile.open(filepath, "w:gz") as tar:
                tar.add(server_path, arcname=f"server_{server_id}")
            
            file_size = os.path.getsize(filepath)
            
            logger.info(f"Full server backup: {filepath} ({file_size} bytes)")
            return {
                "success": True,
                "filename": filename,
                "path": str(filepath),
                "size": file_size,
                "server_id": server_id
            }
        except Exception as e:
            logger.error(f"Full backup failed for server {server_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def list_backups(self, backup_type: str = None) -> list:
        """Yedekleri listele"""
        backups = []
        
        for f in self.backup_dir.glob("*.tar.gz"):
            backup_info = {
                "filename": f.name,
                "path": str(f),
                "size": f.stat().st_size,
                "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            }
            
            if "db_backup" in f.name:
                backup_info["type"] = "database"
            elif "_config_" in f.name:
                backup_info["type"] = "config"
            elif "_full_" in f.name:
                backup_info["type"] = "full"
            else:
                backup_info["type"] = "unknown"
            
            if backup_type is None or backup_info["type"] == backup_type:
                backups.append(backup_info)
        
        for f in self.backup_dir.glob("*.sql.gz"):
            backup_info = {
                "filename": f.name,
                "path": str(f),
                "size": f.stat().st_size,
                "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "type": "database"
            }
            if backup_type is None or backup_type == "database":
                backups.append(backup_info)
        
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)
    
    async def cleanup_old_backups(self, days: int = 30) -> dict:
        """Eski yedekleri temizle"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = []
        
        for f in self.backup_dir.glob("*"):
            if f.is_file():
                file_time = datetime.fromtimestamp(f.stat().st_mtime)
                if file_time < cutoff:
                    f.unlink()
                    deleted.append(f.name)
                    logger.info(f"Deleted old backup: {f.name}")
        
        return {"deleted": deleted, "count": len(deleted)}
    
    async def restore_database(self, backup_path: str) -> dict:
        """Database yedegini geri yukle"""
        from app.core.config import settings

        try:
            import gzip
            import subprocess

            # Decompress
            backup_path.replace(".gz", "")
            with gzip.open(backup_path, 'rb') as f_in:
                sql_content = f_in.read()

            # Guvenli restore - environment variable ile sifre
            env = os.environ.copy()
            env['MYSQL_PWD'] = settings.DB_PASSWORD

            # Guvenli mysql komutu (shell=False)
            mysql_cmd = [
                'mysql',
                f'-u{settings.DB_USER}',
                f'-h{settings.DB_HOST}',
                f'-P{settings.DB_PORT}',
                settings.DB_NAME
            ]

            result = subprocess.run(
                mysql_cmd,
                input=sql_content,
                capture_output=True,
                env=env,
                timeout=600
            )

            if result.returncode != 0:
                raise Exception(result.stderr.decode())

            logger.info(f"Database restored from: {backup_path}")
            return {"success": True, "message": "Database restored successfully"}
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return {"success": False, "error": str(e)}


# Global instance
backup_manager = BackupManager()
