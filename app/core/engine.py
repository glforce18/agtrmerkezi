"""
🎮 AGTR Core Engine - Self-Healing System
Sistem başlangıcında kontrol yapar, hataları otomatik düzeltir
"""
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List


class AGTRLogger:
    """Renkli konsol logger"""
    COLORS = {'INFO':'\033[32m','WARNING':'\033[33m','ERROR':'\033[31m','RESET':'\033[0m'}
    EMOJIS = {'INFO':'✅','WARNING':'⚠️','ERROR':'❌','STARTUP':'🚀','HEALING':'💊'}
    
    def __init__(self):
        self.errors = []
    
    def log(self, level, msg, emoji=None):
        c = self.COLORS.get(level, '')
        r = self.COLORS['RESET']
        e = self.EMOJIS.get(emoji or level, '')
        t = datetime.now().strftime('%H:%M:%S')
        print(f"{c}[{t}] {e} {msg}{r}")
        if level == 'ERROR':
            self.errors.append({"time": t, "msg": msg})
    
    def info(self, msg): self.log('INFO', msg)
    def warning(self, msg): self.log('WARNING', msg)
    def error(self, msg): self.log('ERROR', msg)
    def startup(self, msg): self.log('INFO', msg, 'STARTUP')
    def healing(self, msg): self.log('INFO', msg, 'HEALING')


class SelfHealer:
    """Otomatik hata düzeltici"""
    
    def __init__(self):
        self.fixes = []
        self.logger = AGTRLogger()
    
    def check_directories(self):
        """Eksik dizinleri oluştur"""
        dirs = [
            "static/uploads/assets",
            "static/uploads/avatars",
            "static/uploads/tickets",
            "static/images",
            "logs"
        ]
        for d in dirs:
            p = Path(d)
            if not p.exists():
                p.mkdir(parents=True, exist_ok=True)
                self.fixes.append(f"Dizin oluşturuldu: {d}")
                self.logger.healing(f"Dizin oluşturuldu: {d}")
    
    def check_templates(self):
        """Template syntax hatalarını düzelt"""
        templates = Path("templates")
        if not templates.exists():
            return
        
        for tpl in templates.rglob("*.html"):
            try:
                content = tpl.read_text(encoding='utf-8')
                opens = len(re.findall(r'{%\s*block\s+\w+', content))
                closes = len(re.findall(r'{%\s*endblock', content))
                
                if opens > closes:
                    diff = opens - closes
                    content += "\n{% endblock %}\n" * diff
                    tpl.write_text(content, encoding='utf-8')
                    self.fixes.append(f"Template düzeltildi: {tpl}")
                    self.logger.healing(f"Eksik endblock eklendi: {tpl}")
            except Exception:
                self.logger.warning(f"Template kontrol hatası: {tpl}")
    
    def check_permissions(self):
        """Dosya izinlerini düzelt"""
        for d in ["static/uploads", "logs"]:
            p = Path(d)
            if p.exists():
                try:
                    os.chmod(p, 0o755)
                except:
                    pass
    
    def run_all(self) -> List[str]:
        """Tüm kontrolleri çalıştır"""
        self.check_directories()
        self.check_templates()
        self.check_permissions()
        return self.fixes


class HealthChecker:
    """Sistem sağlık kontrolü"""
    
    async def check_database(self, db):
        """Database bağlantısı"""
        try:
            import time

            from sqlalchemy import text
            start = time.time()
            db.execute(text("SELECT 1"))
            latency = (time.time() - start) * 1000
            return {"status": "healthy", "latency_ms": round(latency, 2)}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def check_redis(self):
        """Redis bağlantısı"""
        try:
            import redis
            r = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=2)
            r.ping()
            return {"status": "healthy"}
        except:
            return {"status": "degraded", "message": "Redis kullanılamıyor"}
    
    async def check_disk(self):
        """Disk kullanımı"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            percent = (used / total) * 100
            status = "healthy" if percent < 80 else "warning" if percent < 90 else "critical"
            return {"status": status, "percent": round(percent, 2), "free_gb": round(free/(1024**3), 2)}
        except:
            return {"status": "unknown"}
    
    async def full_check(self, db=None):
        """Tam sağlık kontrolü"""
        checks = {}
        if db:
            checks["database"] = await self.check_database(db)
        checks["redis"] = await self.check_redis()
        checks["disk"] = await self.check_disk()
        
        statuses = [c.get("status") for c in checks.values()]
        if "unhealthy" in statuses:
            overall = "unhealthy"
        elif "degraded" in statuses or "warning" in statuses:
            overall = "degraded"
        else:
            overall = "healthy"
        
        return {
            "status": overall,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "5.4 Pro",
            "checks": checks
        }


# Global instances
logger = AGTRLogger()
healer = SelfHealer()
health_checker = HealthChecker()


def run_startup_checks():
    """Uygulama başlangıcında çalıştır"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║      🎮 AGTR Merkezi v5.4 Pro - Self-Healing Active 🎮        ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    logger.startup("Sistem kontrolleri başlıyor...")
    
    fixes = healer.run_all()
    
    if fixes:
        logger.healing(f"{len(fixes)} otomatik düzeltme uygulandı")
        for f in fixes:
            print(f"  💊 {f}")
    else:
        logger.info("Tüm kontroller başarılı")
    
    logger.startup("Sistem hazır!")
    return fixes
