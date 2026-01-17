"""
AGTR Merkezi - Global Search Service
Site geneli arama sistemi
"""

from typing import Dict, List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.database import Announcement, ForumPost, ForumTopic, GameServer, User


class SearchService:
    """Site geneli arama servisi"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_all(self, query: str, limit: int = 20) -> Dict[str, List[Dict]]:
        """Tum kategorilerde ara"""
        if not query or len(query) < 2:
            return {"users": [], "forum": [], "servers": [], "announcements": []}
        
        results = {
            "users": self.search_users(query, limit=5),
            "forum": self.search_forum(query, limit=10),
            "servers": self.search_servers(query, limit=5),
            "announcements": self.search_announcements(query, limit=5)
        }
        
        return results
    
    def search_users(self, query: str, limit: int = 10) -> List[Dict]:
        """Kullanici ara"""
        users = self.db.query(User).filter(
            or_(
                User.username.ilike(f"%{query}%"),
                User.display_name.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
        ).limit(limit).all()
        
        return [
            {
                "id": u.id,
                "type": "user",
                "title": u.display_name or u.username,
                "subtitle": f"@{u.username}",
                "url": f"/profile/{u.username}",
                "icon": "fas fa-user",
                "avatar": u.avatar
            }
            for u in users
        ]
    
    def search_forum(self, query: str, limit: int = 20) -> List[Dict]:
        """Forum konulari ve mesajlarda ara"""
        results = []
        
        # Konularda ara (ForumTopic'te content yok, sadece title'da ara)
        topics = self.db.query(ForumTopic).filter(
            ForumTopic.title.ilike(f"%{query}%")
        ).limit(limit // 2).all()
        
        for t in topics:
            results.append({
                "id": t.id,
                "type": "topic",
                "title": t.title,
                "subtitle": f"Forum konusu - {t.view_count} goruntulenme",
                "url": f"/forum/topic/{t.slug}",
                "icon": "fas fa-comments",
                "created_at": t.created_at.isoformat() if t.created_at else None
            })
        
        # Yanitlarda ara
        posts = self.db.query(ForumPost).filter(
            ForumPost.content.ilike(f"%{query}%")
        ).limit(limit // 2).all()
        
        for p in posts:
            # Topic slug'ini al (relationship uzerinden)
            topic_slug = p.topic.slug if p.topic else str(p.topic_id)
            results.append({
                "id": p.id,
                "type": "post",
                "title": f"Forum yaniti",
                "subtitle": p.content[:100] + "..." if len(p.content) > 100 else p.content,
                "url": f"/forum/topic/{topic_slug}#post-{p.id}",
                "icon": "fas fa-reply",
                "created_at": p.created_at.isoformat() if p.created_at else None
            })
        
        return results
    
    def search_servers(self, query: str, limit: int = 10) -> List[Dict]:
        """Sunucularda ara"""
        servers = self.db.query(GameServer).filter(
            or_(
                GameServer.name.ilike(f"%{query}%"),
                GameServer.ip_address.ilike(f"%{query}%")
            )
        ).limit(limit).all()
        
        return [
            {
                "id": s.id,
                "type": "server",
                "title": s.name,
                "subtitle": f"{s.ip_address}:{s.port}",
                "url": f"/server/{s.id}",
                "icon": "fas fa-server",
                "status": s.status.value if s.status else "unknown"
            }
            for s in servers
        ]
    
    def search_announcements(self, query: str, limit: int = 10) -> List[Dict]:
        """Duyurularda ara"""
        announcements = self.db.query(Announcement).filter(
            or_(
                Announcement.title.ilike(f"%{query}%"),
                Announcement.content.ilike(f"%{query}%")
            )
        ).limit(limit).all()
        
        return [
            {
                "id": a.id,
                "type": "announcement",
                "title": a.title,
                "subtitle": a.content[:100] + "..." if len(a.content) > 100 else a.content,
                "url": f"/announcements/{a.id}",
                "icon": "fas fa-bullhorn",
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in announcements
        ]