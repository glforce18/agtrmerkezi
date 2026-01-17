"""
AGTR Merkezi - Import/Export Service
Veri aktarim sistemi
"""

import csv
import io
import json
from datetime import datetime
from typing import Dict, List

from sqlalchemy.orm import Session


class ImportExportService:
    """Veri aktarim servisi"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_users(self, format: str = "json") -> str:
        """Kullanicilari export et"""
        from app.models.database import User
        users = self.db.query(User).all()
        
        data = [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "display_name": u.display_name,
                "role": u.role.value,
                "balance": float(u.balance) if u.balance else 0,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ]
        
        if format == "csv":
            return self._to_csv(data)
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_servers(self, format: str = "json") -> str:
        """Sunuculari export et"""
        from app.models.database import GameServer
        servers = self.db.query(GameServer).all()
        
        data = [
            {
                "id": s.id,
                "name": s.name,
                "ip_address": s.ip_address,
                "port": s.port,
                "game_type": s.game_type.value if s.game_type else None,
                "status": s.status.value if s.status else None,
                "owner_id": s.owner_id
            }
            for s in servers
        ]
        
        if format == "csv":
            return self._to_csv(data)
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_payments(self, format: str = "json") -> str:
        """Odemeleri export et"""
        from app.models.database import Payment
        payments = self.db.query(Payment).all()
        
        data = [
            {
                "id": p.id,
                "user_id": p.user_id,
                "amount": float(p.amount) if p.amount else 0,
                "status": p.status.value if p.status else None,
                "payment_method": p.payment_method,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in payments
        ]
        
        if format == "csv":
            return self._to_csv(data)
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_forum(self, format: str = "json") -> str:
        """Forum verilerini export et"""
        from app.models.database import ForumCategory, ForumTopic
        
        categories = self.db.query(ForumCategory).all()
        topics = self.db.query(ForumTopic).all()
        
        data = {
            "categories": [
                {"id": c.id, "name": c.name, "slug": c.slug, "description": c.description}
                for c in categories
            ],
            "topics": [
                {"id": t.id, "title": t.title, "slug": t.slug, "category_id": t.category_id}
                for t in topics
            ]
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_all(self) -> str:
        """Tum verileri export et"""
        data = {
            "exported_at": datetime.now().isoformat(),
            "users": json.loads(self.export_users()),
            "servers": json.loads(self.export_servers()),
            "payments": json.loads(self.export_payments()),
            "forum": json.loads(self.export_forum())
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _to_csv(self, data: List[Dict]) -> str:
        """JSON verisini CSV'ye cevir"""
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
