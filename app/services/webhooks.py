"""
AGTR Merkezi v5.0 - Webhook System
Discord, Telegram ve custom webhook destegi
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

# Shared session for connection pooling
_session: Optional[aiohttp.ClientSession] = None
_session_lock = asyncio.Lock()


async def get_session() -> aiohttp.ClientSession:
    """Get or create shared aiohttp session for connection pooling"""
    global _session
    async with _session_lock:
        if _session is None or _session.closed:
            _session = aiohttp.ClientSession()
    return _session


async def close_session():
    """Close the shared session (call on application shutdown)"""
    global _session
    async with _session_lock:
        if _session is not None and not _session.closed:
            await _session.close()
            _session = None


class WebhookManager:
    """Webhook yoneticisi"""
    
    def __init__(self):
        self.webhooks = {}
        self.queue = asyncio.Queue()
        self._running = False
    
    def register_webhook(self, name: str, url: str, webhook_type: str = "discord"):
        """Webhook kaydet"""
        self.webhooks[name] = {
            "url": url,
            "type": webhook_type,
            "created_at": datetime.utcnow(),
            "sent_count": 0,
            "last_sent": None
        }
        logger.info(f"Webhook registered: {name} ({webhook_type})")
    
    def remove_webhook(self, name: str):
        """Webhook kaldir"""
        if name in self.webhooks:
            del self.webhooks[name]
            logger.info(f"Webhook removed: {name}")
    
    async def send_discord(self, url: str, content: str = None, embeds: list = None, username: str = "AGTR Bot"):
        """Discord webhook gonder"""
        payload = {"username": username}
        
        if content:
            payload["content"] = content
        
        if embeds:
            payload["embeds"] = embeds
        
        try:
            session = await get_session()
            async with session.post(url, json=payload) as response:
                if response.status in [200, 204]:
                    logger.info("Discord webhook sent successfully")
                    return {"success": True}
                else:
                    text = await response.text()
                    logger.error(f"Discord webhook failed: {response.status} - {text}")
                    return {"success": False, "error": text}
        except Exception as e:
            logger.error(f"Discord webhook error: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_telegram(self, bot_token: str, chat_id: str, message: str, parse_mode: str = "HTML"):
        """Telegram mesaji gonder"""
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            session = await get_session()
            async with session.post(url, json=payload) as response:
                result = await response.json()
                if result.get("ok"):
                    logger.info("Telegram message sent successfully")
                    return {"success": True}
                else:
                    logger.error(f"Telegram error: {result}")
                    return {"success": False, "error": result.get("description")}
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_custom(self, url: str, payload: dict, headers: dict = None):
        """Custom webhook gonder"""
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        
        try:
            session = await get_session()
            async with session.post(url, json=payload, headers=default_headers) as response:
                if response.status < 400:
                    logger.info(f"Custom webhook sent: {url}")
                    return {"success": True, "status": response.status}
                else:
                    text = await response.text()
                    logger.error(f"Custom webhook failed: {response.status}")
                    return {"success": False, "error": text}
        except Exception as e:
            logger.error(f"Custom webhook error: {e}")
            return {"success": False, "error": str(e)}
    
    async def broadcast(self, event_type: str, data: dict):
        """Tum kayitli webhook'lara gonder"""
        results = {}
        
        for name, webhook in self.webhooks.items():
            if webhook["type"] == "discord":
                # Discord embed olustur
                embed = self._create_discord_embed(event_type, data)
                result = await self.send_discord(webhook["url"], embeds=[embed])
            elif webhook["type"] == "telegram":
                # Telegram mesaji olustur
                message = self._create_telegram_message(event_type, data)
                # URL'den token ve chat_id cikar
                # Format: telegram://BOT_TOKEN/CHAT_ID
                parts = webhook["url"].replace("telegram://", "").split("/")
                if len(parts) >= 2:
                    result = await self.send_telegram(parts[0], parts[1], message)
                else:
                    result = {"success": False, "error": "Invalid telegram URL format"}
            else:
                result = await self.send_custom(webhook["url"], {"event": event_type, "data": data})
            
            results[name] = result

            if result.get("success"):
                webhook["sent_count"] += 1
                webhook["last_sent"] = datetime.utcnow()
            else:
                webhook["error_count"] = webhook.get("error_count", 0) + 1
                webhook["last_error"] = result.get("error")
                logger.error(f"Webhook '{name}' failed: {result.get('error')}")

        return results
    
    def _create_discord_embed(self, event_type: str, data: dict) -> dict:
        """Discord embed olustur"""
        colors = {
            "new_user": 0x00ff00,      # Yesil
            "new_payment": 0xffd700,   # Altin
            "server_created": 0x00bfff, # Mavi
            "server_expired": 0xff6600, # Turuncu
            "error": 0xff0000,          # Kirmizi
            "warning": 0xffff00,        # Sari
            "info": 0x0099ff            # Acik mavi
        }
        
        titles = {
            "new_user": "🆕 Yeni Kullanici",
            "new_payment": "💰 Yeni Odeme",
            "server_created": "🖥️ Sunucu Olusturuldu",
            "server_expired": "⏰ Sunucu Suresi Doldu",
            "error": "❌ Hata",
            "warning": "⚠️ Uyari",
            "info": "ℹ️ Bilgi"
        }
        
        embed = {
            "title": titles.get(event_type, f"📢 {event_type}"),
            "color": colors.get(event_type, 0x808080),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "AGTR Merkezi"}
        }
        
        # Data'dan field'lar olustur
        fields = []
        for key, value in data.items():
            if key not in ["_internal", "password", "token"]:
                fields.append({
                    "name": key.replace("_", " ").title(),
                    "value": str(value)[:1024],
                    "inline": len(str(value)) < 50
                })
        
        if fields:
            embed["fields"] = fields[:25]  # Discord max 25 field
        
        return embed
    
    def _create_telegram_message(self, event_type: str, data: dict) -> str:
        """Telegram mesaji olustur"""
        emojis = {
            "new_user": "🆕",
            "new_payment": "💰",
            "server_created": "🖥️",
            "server_expired": "⏰",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        emoji = emojis.get(event_type, "📢")
        lines = [f"<b>{emoji} {event_type.replace('_', ' ').title()}</b>", ""]
        
        for key, value in data.items():
            if key not in ["_internal", "password", "token"]:
                lines.append(f"<b>{key.replace('_', ' ').title()}:</b> {value}")
        
        lines.append("")
        lines.append(f"<i>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>")
        
        return "\n".join(lines)


# ==================== EVENT HANDLERS ====================

async def notify_new_user(user_data: dict):
    """Yeni kullanici bildirimi"""
    await webhook_manager.broadcast("new_user", {
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "ip": user_data.get("ip")
    })


async def notify_new_payment(payment_data: dict):
    """Yeni odeme bildirimi"""
    await webhook_manager.broadcast("new_payment", {
        "user": payment_data.get("username"),
        "amount": f"{payment_data.get('amount')} TL",
        "package": payment_data.get("package_name"),
        "method": payment_data.get("method")
    })


async def notify_server_created(server_data: dict):
    """Sunucu olusturuldu bildirimi"""
    await webhook_manager.broadcast("server_created", {
        "name": server_data.get("name"),
        "owner": server_data.get("owner"),
        "ip": server_data.get("ip"),
        "game": server_data.get("game_type")
    })


async def notify_error(error_data: dict):
    """Hata bildirimi"""
    await webhook_manager.broadcast("error", {
        "type": error_data.get("type"),
        "message": error_data.get("message"),
        "location": error_data.get("location")
    })


# Global instance
webhook_manager = WebhookManager()
