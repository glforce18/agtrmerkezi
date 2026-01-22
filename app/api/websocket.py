"""
AGTR Merkezi - WebSocket Endpoints
Real-time server stats, notifications, chat
"""

import asyncio
import json
import logging
import time
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_token
from app.models.connection import db_session
from app.models.database import GameServer, Notification, ServerStatus, User

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== CONNECTION MANAGER ====================

class ConnectionManager:
    """WebSocket bağlantı yöneticisi"""
    
    def __init__(self):
        # endpoint -> set of websockets
        self.connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> user_id (authenticated users)
        self.authenticated: Dict[WebSocket, int] = {}
        # room_id -> set of websockets (for chat)
        self.rooms: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, endpoint: str):
        await websocket.accept()
        if endpoint not in self.connections:
            self.connections[endpoint] = set()
        self.connections[endpoint].add(websocket)
        logger.info(f"WebSocket connected: {endpoint}")
    
    def disconnect(self, websocket: WebSocket, endpoint: str):
        if endpoint in self.connections:
            self.connections[endpoint].discard(websocket)
        if websocket in self.authenticated:
            del self.authenticated[websocket]
        # Remove from all rooms
        for room in self.rooms.values():
            room.discard(websocket)
        logger.info(f"WebSocket disconnected: {endpoint}")
    
    async def broadcast(self, endpoint: str, message: dict):
        """Endpoint'e bağlı tüm client'lara mesaj gönder"""
        if endpoint not in self.connections:
            return
        
        disconnected = set()
        for ws in self.connections[endpoint]:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                disconnected.add(ws)
        
        # Clean up disconnected
        for ws in disconnected:
            self.connections[endpoint].discard(ws)
    
    async def send_to_user(self, user_id: int, message: dict):
        """Belirli kullanıcıya mesaj gönder"""
        for ws, uid in self.authenticated.items():
            if uid == user_id:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    logger.error(f"Send to user error: {e}")
    
    async def broadcast_to_room(self, room_id: str, message: dict):
        """Odadaki tüm kullanıcılara mesaj gönder"""
        if room_id not in self.rooms:
            return
        
        for ws in self.rooms[room_id]:
            try:
                await ws.send_json(message)
            except Exception:
                pass
    
    def join_room(self, websocket: WebSocket, room_id: str):
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(websocket)
    
    def leave_room(self, websocket: WebSocket, room_id: str):
        if room_id in self.rooms:
            self.rooms[room_id].discard(websocket)
    
    def authenticate(self, websocket: WebSocket, user_id: int):
        self.authenticated[websocket] = user_id


manager = ConnectionManager()


# ==================== SERVER STATS ====================

@router.websocket("/ws/server-stats")
async def server_stats_ws(websocket: WebSocket):
    """Real-time sunucu istatistikleri"""
    await manager.connect(websocket, "server-stats")
    
    try:
        while True:
            # Client'tan mesaj bekle (ping/pong için)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                
                # Belirli sunucu için stats iste
                if data:
                    try:
                        request = json.loads(data)
                        server_id = request.get("server_id")
                        if server_id:
                            stats = await get_server_stats(server_id)
                            await websocket.send_json(stats)
                    except json.JSONDecodeError:
                        pass
            except asyncio.TimeoutError:
                # Keep-alive ping
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "server-stats")


async def get_server_stats(server_id: int) -> dict:
    """Sunucu istatistiklerini getir"""
    try:
        with db_session() as db:
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
            
            if not server:
                return {"error": "Server not found"}
            
            # Gerçek stats için server_manager.sh veya RCON kullanılabilir
            # Şimdilik mock data
            return {
                "server_id": server_id,
                "stats": {
                    "status": server.status.value if server.status else "offline",
                    "players": 0,  # TODO: RCON ile al
                    "max_players": server.slots,
                    "map": "crossfire",  # TODO: RCON ile al
                    "cpu": 15,  # TODO: Sistemden al
                    "ram": 25,  # TODO: Sistemden al
                    "uptime": 3600  # TODO: Hesapla
                }
            }
    except Exception as e:
        logger.error(f"Get server stats error: {e}")
        return {"error": str(e)}


# ==================== DASHBOARD STATS ====================

@router.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    """Dashboard real-time stats"""
    await manager.connect(websocket, "dashboard")
    
    try:
        while True:
            # Her 5 saniyede dashboard stats gönder
            stats = await get_dashboard_stats()
            await websocket.send_json(stats)
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard")


async def get_dashboard_stats() -> dict:
    """Dashboard istatistikleri"""
    try:
        with db_session() as db:
            total_online = db.query(GameServer).filter(
                GameServer.status == ServerStatus.RUNNING
            ).count()
            
            # TODO: Gerçek oyuncu sayısı için RCON
            total_players = total_online * 5  # Mock
            
            return {
                "total_online": total_online,
                "total_players": total_players,
                "today_revenue": 0,  # TODO: Payments'tan hesapla
                "active_users": 0  # TODO: Sessions'tan hesapla
            }
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return {}


# ==================== NOTIFICATIONS ====================

@router.websocket("/ws/notifications")
async def notifications_ws(websocket: WebSocket):
    """Kullanıcı bildirimleri"""
    await manager.connect(websocket, "notifications")
    
    try:
        # İlk mesajda token ile authenticate
        data = await websocket.receive_text()
        try:
            payload = json.loads(data)
            token = payload.get("token")
            if token:
                decoded = decode_token(token)
                if decoded:
                    user_id = decoded.get("sub")
                    if user_id:
                        manager.authenticate(websocket, int(user_id))
                        
                        # Okunmamış bildirimleri gönder
                        await send_unread_notifications(websocket, int(user_id))
        except Exception:
            pass
        
        # Bağlantıyı açık tut
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "notifications")


async def send_unread_notifications(websocket: WebSocket, user_id: int):
    """Okunmamış bildirimleri gönder"""
    try:
        with db_session() as db:
            notifications = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).order_by(Notification.created_at.desc()).limit(10).all()
            
            for notif in notifications:
                await websocket.send_json({
                    "type": notif.type,
                    "title": notif.title,
                    "message": notif.message,
                    "link": notif.link,
                    "created_at": notif.created_at.isoformat()
                })
    except Exception as e:
        logger.error(f"Send notifications error: {e}")


# ==================== CHAT ====================

@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket):
    """Chat odaları"""
    await manager.connect(websocket, "chat")
    current_room = None
    username = "Misafir"
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "auth":
                    # Token ile authenticate
                    token = message.get("token")
                    if token:
                        decoded = decode_token(token)
                        if decoded:
                            user_id = decoded.get("sub")
                            manager.authenticate(websocket, int(user_id))
                            # Username'i DB'den al
                            with db_session() as db:
                                user = db.query(User).filter(User.id == user_id).first()
                                if user:
                                    username = user.display_name or user.username
                
                elif action == "join":
                    # Odaya katıl
                    room = message.get("room")
                    if room:
                        if current_room:
                            manager.leave_room(websocket, current_room)
                        current_room = room
                        manager.join_room(websocket, room)
                        
                        await manager.broadcast_to_room(room, {
                            "type": "system",
                            "message": f"{username} odaya katıldı",
                            "timestamp": time.time()
                        })
                
                elif action == "leave":
                    # Odadan ayrıl
                    if current_room:
                        await manager.broadcast_to_room(current_room, {
                            "type": "system",
                            "message": f"{username} odadan ayrıldı",
                            "timestamp": time.time()
                        })
                        manager.leave_room(websocket, current_room)
                        current_room = None
                
                elif action == "message":
                    # Mesaj gönder
                    if current_room:
                        text = message.get("message", "").strip()
                        if text and len(text) <= 500:
                            await manager.broadcast_to_room(current_room, {
                                "type": "message",
                                "user": username,
                                "message": text,
                                "timestamp": time.time()
                            })
                            
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        if current_room:
            await manager.broadcast_to_room(current_room, {
                "type": "system",
                "message": f"{username} bağlantısı koptu",
                "timestamp": time.time()
            })
            manager.leave_room(websocket, current_room)
        manager.disconnect(websocket, "chat")


# ==================== ACTIVITY FEED ====================

@router.websocket("/ws/activity")
async def activity_ws(websocket: WebSocket):
    """Aktivite akışı"""
    await manager.connect(websocket, "activity")
    
    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "activity")


# ==================== LEADERBOARD ====================

@router.websocket("/ws/leaderboard")
async def leaderboard_ws(websocket: WebSocket):
    """Sıralama tablosu"""
    await manager.connect(websocket, "leaderboard")
    
    try:
        # İlk yüklemede varsayılan sıralama
        await websocket.send_json(await get_leaderboard("kills"))
        
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                leaderboard_type = message.get("type", "kills")
                
                result = await get_leaderboard(leaderboard_type)
                await websocket.send_json(result)
                
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, "leaderboard")


async def get_leaderboard(leaderboard_type: str) -> dict:
    """Sıralama verisi (mock)"""
    # TODO: Gerçek veritabanından al
    mock_players = [
        {"name": "ProPlayer", "avatar": None, "server": "AGTR #1", "score": 15420},
        {"name": "HeadshotKing", "avatar": None, "server": "AGTR #2", "score": 12350},
        {"name": "AimBot", "avatar": None, "server": "CS #1", "score": 11200},
        {"name": "NoScope", "avatar": None, "server": "AGTR #1", "score": 9800},
        {"name": "Rusher", "avatar": None, "server": "CS #2", "score": 8500},
    ]
    
    return {
        "type": leaderboard_type,
        "players": mock_players
    }


# ==================== BROADCAST HELPERS ====================

async def broadcast_server_update(server_id: int, status: str):
    """Sunucu durumu değiştiğinde broadcast"""
    await manager.broadcast("server-stats", {
        "server_id": server_id,
        "stats": {"status": status}
    })


async def broadcast_notification(user_id: int, notification: dict):
    """Kullanıcıya bildirim gönder"""
    await manager.send_to_user(user_id, notification)


async def broadcast_activity(activity: dict):
    """Aktivite feed'e ekle"""
    await manager.broadcast("activity", activity)


# ==================== JACKPOT WEBSOCKET ====================

# Jackpot için ayrı manager (state takibi için)
jackpot_state = {
    "current_round": None,
    "players": [],
    "total_pot": 0,
    "status": "waiting",
    "countdown": 0
}


@router.websocket("/ws/jackpot")
async def jackpot_ws(websocket: WebSocket):
    """Jackpot gerçek zamanlı bağlantı"""
    await manager.connect(websocket, "jackpot")

    try:
        # İlk bağlantıda mevcut tur bilgisini gönder
        await websocket.send_json({
            "type": "round_info",
            "data": await get_jackpot_state()
        })

        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                action = message.get("action")

                if action == "auth":
                    # Token ile authenticate
                    token = message.get("token")
                    if token:
                        decoded = decode_token(token)
                        if decoded:
                            user_id = decoded.get("sub")
                            if user_id:
                                manager.authenticate(websocket, int(user_id))
                                await websocket.send_json({
                                    "type": "auth_success",
                                    "user_id": int(user_id)
                                })

                elif action == "ping":
                    await websocket.send_json({"type": "pong"})

                elif action == "get_state":
                    # Güncel durum iste
                    await websocket.send_json({
                        "type": "round_info",
                        "data": await get_jackpot_state()
                    })

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket, "jackpot")


async def get_jackpot_state() -> dict:
    """Jackpot mevcut durumunu getir"""
    try:
        with db_session() as db:
            from app.services.jackpot import get_jackpot_service
            jackpot = get_jackpot_service(db)
            round_info = jackpot.get_round_info()

            if round_info:
                return round_info
            else:
                # Yeni tur oluştur
                new_round = jackpot.get_or_create_round()
                return jackpot.get_round_info(new_round.id)
    except Exception as e:
        logger.error(f"Get jackpot state error: {e}")
        return {"error": str(e)}


async def broadcast_jackpot_bet(bet_data: dict):
    """Yeni bahis broadcast et"""
    await manager.broadcast("jackpot", {
        "type": "new_bet",
        "data": bet_data
    })


async def broadcast_jackpot_round_update(round_data: dict):
    """Tur güncellemesi broadcast et"""
    await manager.broadcast("jackpot", {
        "type": "round_update",
        "data": round_data
    })


async def broadcast_jackpot_countdown(seconds: int):
    """Geri sayım broadcast et"""
    await manager.broadcast("jackpot", {
        "type": "countdown",
        "seconds": seconds
    })


async def broadcast_jackpot_rolling(animation_data: dict):
    """Çark dönüyor broadcast et"""
    await manager.broadcast("jackpot", {
        "type": "rolling",
        "data": animation_data
    })


async def broadcast_jackpot_winner(winner_data: dict):
    """Kazanan broadcast et"""
    await manager.broadcast("jackpot", {
        "type": "winner",
        "data": winner_data
    })
