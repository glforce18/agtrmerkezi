# Forum API Endpoints - Backend Örnekleri

## app/api/routes/forum.py

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import json
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.redis_manager import redis_client
from app.models.forum import ForumTopic, ForumReply, ForumCategory
from app.models.user import User
from app.services.forum_service import ForumService

router = APIRouter(prefix="/forum", tags=["forum"])

# ============================================================================
# YENİ ENDPOINT: CANLI AKTİVİTE
# ============================================================================

@router.get("/live-activity")
async def get_live_activity(
    limit: int = Query(default=10, le=20),
    db: Session = Depends(get_db)
):
    """
    Ana sayfada gösterilecek canlı forum aktivitesi
    
    Cache: 10 saniye
    Returns: Son aktiviteler (yanıtlar, yeni konular, level up, vb.)
    """
    
    cache_key = "forum:live_activity"
    cached = await redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    activities = []
    
    # Son yanıtlar
    recent_replies = db.query(ForumReply)\
        .options(
            joinedload(ForumReply.author),
            joinedload(ForumReply.topic)
        )\
        .order_by(ForumReply.created_at.desc())\
        .limit(limit)\
        .all()
    
    for reply in recent_replies:
        activities.append({
            "id": f"reply_{reply.id}",
            "type": "reply",
            "user": {
                "username": reply.author.username,
                "avatar": reply.author.avatar_url,
                "level": reply.author.level
            },
            "action": f"'{reply.topic.title}' konusuna yanıt verdi",
            "time": get_time_ago(reply.created_at),
            "topic_id": reply.topic_id,
            "topic_title": reply.topic.title,
            "created_at": reply.created_at.isoformat()
        })
    
    # Aktiviteleri zamana göre sırala
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    activities = activities[:limit]
    
    # created_at'i kaldır (sadece sıralama için kullandık)
    for activity in activities:
        del activity["created_at"]
    
    result = {
        "activities": activities,
        "count": len(activities)
    }
    
    # 10 saniye cache
    await redis_client.setex(cache_key, 10, json.dumps(result))
    
    return result


# ============================================================================
# YENİ ENDPOINT: TREND KONULAR
# ============================================================================

@router.get("/trending")
async def get_trending_topics(
    days: int = Query(default=7, le=30),
    limit: int = Query(default=5, le=20),
    db: Session = Depends(get_db)
):
    """
    Belirli gün sayısı içinde en popüler konular
    
    Cache: 30 saniye
    Metrikler: view_count, reply_count, like_count
    """
    
    cache_key = f"forum:trending:{days}:{limit}"
    cached = await redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Son X gün içindeki konular
    since_date = datetime.utcnow() - timedelta(days=days)
    
    topics = db.query(ForumTopic)\
        .options(
            joinedload(ForumTopic.author),
            joinedload(ForumTopic.category)
        )\
        .filter(ForumTopic.created_at >= since_date)\
        .order_by(
            (ForumTopic.view_count * 1 + 
             ForumTopic.reply_count * 3 + 
             ForumTopic.like_count * 5).desc()
        )\
        .limit(limit)\
        .all()
    
    result = {
        "topics": [
            {
                "id": topic.id,
                "title": topic.title,
                "slug": topic.slug,
                "author": {
                    "username": topic.author.username,
                    "avatar": topic.author.avatar_url,
                    "level": topic.author.level
                },
                "category": {
                    "name": topic.category.name,
                    "slug": topic.category.slug,
                    "icon": topic.category.icon
                },
                "view_count": topic.view_count,
                "reply_count": topic.reply_count,
                "like_count": topic.like_count,
                "created_at": topic.created_at.isoformat()
            }
            for topic in topics
        ],
        "days": days
    }
    
    # 30 saniye cache
    await redis_client.setex(cache_key, 30, json.dumps(result))
    
    return result


# ============================================================================
# YENİ ENDPOINT: ONLINE KULLANICILAR
# ============================================================================

@router.get("/online-users")
async def get_online_users(
    limit: int = Query(default=12, le=50),
    db: Session = Depends(get_db)
):
    """
    Şu anda online olan kullanıcılar
    
    Cache: 5 saniye
    Online tanımı: Son 5 dakika içinde aktivite
    """
    
    cache_key = "forum:online_users"
    cached = await redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Son 5 dakika içinde aktivite olanlar
    since_time = datetime.utcnow() - timedelta(minutes=5)
    
    online_users = db.query(User)\
        .filter(User.last_seen >= since_time)\
        .order_by(User.last_seen.desc())\
        .limit(limit)\
        .all()
    
    result = {
        "users": [
            {
                "username": user.username,
                "avatar": user.avatar_url,
                "level": user.level,
                "last_seen": user.last_seen.isoformat()
            }
            for user in online_users
        ],
        "total": db.query(User).filter(User.last_seen >= since_time).count()
    }
    
    # 5 saniye cache
    await redis_client.setex(cache_key, 5, json.dumps(result))
    
    return result


# ============================================================================
# YENİ ENDPOINT: FORUM İSTATİSTİKLERİ
# ============================================================================

@router.get("/stats")
async def get_forum_stats(db: Session = Depends(get_db)):
    """
    Forum genel istatistikleri
    
    Cache: 60 saniye
    """
    
    cache_key = "forum:stats"
    cached = await redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Online kullanıcı sayısı
    since_time = datetime.utcnow() - timedelta(minutes=5)
    online_count = db.query(User).filter(User.last_seen >= since_time).count()
    
    # Toplam konu sayısı
    total_topics = db.query(ForumTopic).count()
    
    # Bugün oluşturulan konu sayısı
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    topics_today = db.query(ForumTopic)\
        .filter(ForumTopic.created_at >= today_start)\
        .count()
    
    result = {
        "onlineUsers": online_count,
        "totalTopics": total_topics,
        "topicsToday": topics_today,
        "activeServers": 0  # Bu sunucu API'sinden gelecek
    }
    
    # 60 saniye cache
    await redis_client.setex(cache_key, 60, json.dumps(result))
    
    return result


# ============================================================================
# YENİ ENDPOINT: OKUNMAMIŞ KONU SAYISI
# ============================================================================

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının okunmamış konu/yanıt sayısı
    
    Cache: Kullanıcı bazlı, 30 saniye
    """
    
    cache_key = f"forum:unread:{current_user.id}"
    cached = await redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Kullanıcının son forum ziyaret zamanı
    last_visit = current_user.last_forum_visit or datetime(2000, 1, 1)
    
    # Son ziyaretten sonra oluşturulan konu sayısı
    unread_topics = db.query(ForumTopic)\
        .filter(ForumTopic.created_at > last_visit)\
        .count()
    
    # Takip ettiği konulardaki yeni yanıt sayısı
    # (Bu özellik henüz yoksa, şimdilik 0)
    unread_replies = 0
    
    result = {
        "count": unread_topics + unread_replies,
        "topics": unread_topics,
        "replies": unread_replies
    }
    
    # 30 saniye cache
    await redis_client.setex(cache_key, 30, json.dumps(result))
    
    return result


# ============================================================================
# HELPER FONKSĐYONLAR
# ============================================================================

def get_time_ago(dt: datetime) -> str:
    """Datetime'ı 'X saniye önce' formatına çevir"""
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} saniye önce"
    elif seconds < 3600:
        return f"{int(seconds / 60)} dakika önce"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} saat önce"
    elif seconds < 604800:
        return f"{int(seconds / 86400)} gün önce"
    else:
        return dt.strftime("%d.%m.%Y")
```

## app/api/websocket/forum.py - WebSocket Endpoint

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

from app.core.redis_manager import redis_client

router = APIRouter()

# Aktif WebSocket bağlantıları
active_connections: List[WebSocket] = []

@router.websocket("/ws/forum-live")
async def forum_live_websocket(websocket: WebSocket):
    """
    Forum canlı aktivite WebSocket endpoint'i
    
    Client bağlandığında:
    1. Redis'e "forum:live" kanalına abone ol
    2. Yeni mesajları client'a forward et
    3. Bağlantı koptuğunda cleanup yap
    """
    
    await websocket.accept()
    active_connections.append(websocket)
    
    # Redis Pub/Sub
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("forum:live")
    
    try:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                
                # Tüm bağlı client'lara gönder
                for connection in active_connections:
                    try:
                        await connection.send_json(data)
                    except Exception:
                        # Bağlantı kopmuşsa listeden çıkar
                        active_connections.remove(connection)
                        
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        await pubsub.unsubscribe("forum:live")
        print(f"Client disconnected. Active connections: {len(active_connections)}")


async def broadcast_activity(activity_data: dict):
    """
    Yeni aktiviteyi tüm bağlı client'lara gönder
    
    Kullanım:
    await broadcast_activity({
        "type": "new_activity",
        "activity": {...}
    })
    """
    
    message = json.dumps(activity_data)
    await redis_client.publish("forum:live", message)
```

## app/services/forum_service.py - Business Logic

```python
from app.api.websocket.forum import broadcast_activity

class ForumService:
    
    @staticmethod
    async def create_reply(topic_id: int, content: str, user_id: int, db):
        """
        Yeni yanıt oluştur ve WebSocket'e broadcast et
        """
        
        # Yanıtı oluştur
        reply = ForumReply(
            topic_id=topic_id,
            content=content,
            author_id=user_id
        )
        
        db.add(reply)
        db.commit()
        db.refresh(reply)
        
        # Konuyu güncelle
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
        topic.reply_count += 1
        topic.last_activity = datetime.utcnow()
        db.commit()
        
        # WebSocket'e broadcast et
        await broadcast_activity({
            "type": "new_activity",
            "activity": {
                "id": f"reply_{reply.id}",
                "type": "reply",
                "user": {
                    "username": reply.author.username,
                    "avatar": reply.author.avatar_url,
                    "level": reply.author.level
                },
                "action": f"'{topic.title}' konusuna yanıt verdi",
                "time": "Şimdi",
                "topic_id": topic_id,
                "topic_title": topic.title
            }
        })
        
        return reply
```

## Öncelikli Implementasyon Sırası

1. **GET /forum/stats** → En basit, hızlıca eklenebilir
2. **GET /forum/online-users** → Orta karmaşıklık
3. **GET /forum/trending** → Orta karmaşıklık
4. **GET /forum/live-activity** → Orta-yüksek karmaşıklık
5. **WebSocket /ws/forum-live** → Yüksek karmaşıklık

## Test Örnekleri

```bash
# Stats endpoint test
curl http://localhost:8000/api/forum/stats

# Trending topics test
curl http://localhost:8000/api/forum/trending?days=7&limit=5

# Online users test
curl http://localhost:8000/api/forum/online-users?limit=12

# WebSocket test (JavaScript)
const ws = new WebSocket('ws://localhost:8000/ws/forum-live')
ws.onmessage = (event) => console.log(JSON.parse(event.data))
```
