"""
AGTR Merkezi - Game Server Scraper
Half-Life, CS 1.6, AG sunucularini tara ve veritabanina kaydet
Steam Query Protocol (A2S) + Harici kaynaklar
"""

import asyncio
import logging
import struct
import socket
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import a2s
import httpx
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class GameTypeEnum(Enum):
    """Desteklenen oyun turleri"""
    HLDM = "hldm"
    AG = "ag"
    CS16 = "cs16"
    TFC = "tfc"
    DOD = "dod"
    RICOCHET = "ricochet"


@dataclass
class ScrapedServer:
    """Taranan sunucu bilgisi"""
    ip: str
    port: int
    name: str = ""
    map: str = ""
    players: int = 0
    max_players: int = 0
    game_type: GameTypeEnum = GameTypeEnum.HLDM
    game_dir: str = ""
    ping: int = 999
    password_protected: bool = False
    vac_enabled: bool = False
    os: str = ""
    version: str = ""
    tags: List[str] = field(default_factory=list)
    country: str = ""
    last_seen: datetime = field(default_factory=datetime.utcnow)
    is_online: bool = True
    player_list: List[Dict] = field(default_factory=list)
    rules: Dict = field(default_factory=dict)

    @property
    def address(self) -> str:
        return f"{self.ip}:{self.port}"


class ServerScraper:
    """
    Half-Life / CS 1.6 sunucu tarayici
    - Steam Master Server sorgusu
    - A2S protokolu ile sunucu bilgisi
    - GameTracker entegrasyonu
    - Topluluk sunucu listesi
    """

    # Steam Master Server adresleri
    MASTER_SERVERS = [
        ("hl1master.steampowered.com", 27010),
        ("hl1master.steampowered.com", 27011),
        ("208.64.200.65", 27010),
    ]

    # Oyun filtreleri
    GAME_FILTERS = {
        GameTypeEnum.HLDM: "\\gamedir\\valve",
        GameTypeEnum.AG: "\\gamedir\\ag",
        GameTypeEnum.CS16: "\\gamedir\\cstrike",
        GameTypeEnum.TFC: "\\gamedir\\tfc",
        GameTypeEnum.DOD: "\\gamedir\\dod",
    }

    # Turkiye IP araliklari (RIPE veritabanindan)
    TR_IP_RANGES = [
        ("78.160.0.0", "78.191.255.255"),
        ("85.96.0.0", "85.111.255.255"),
        ("88.224.0.0", "88.255.255.255"),
        ("176.32.0.0", "176.63.255.255"),
        ("193.140.0.0", "193.143.255.255"),
        ("212.58.0.0", "212.58.255.255"),
        ("212.174.0.0", "212.175.255.255"),
        ("213.14.0.0", "213.15.255.255"),
    ]

    def __init__(self, timeout: float = 2.0, max_concurrent: int = 50):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._http_client = None

    async def get_http_client(self) -> httpx.AsyncClient:
        """HTTP client singleton"""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=10.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
        return self._http_client

    async def close(self):
        """Kaynaklari temizle"""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    # ==================== STEAM MASTER SERVER ====================

    async def query_master_server(
        self,
        game_type: GameTypeEnum = GameTypeEnum.AG,
        region: int = 0xFF,  # 0xFF = all regions, 0x03 = Europe
        limit: int = 500
    ) -> List[Tuple[str, int]]:
        """
        Steam Master Server'dan sunucu listesi al

        Region codes:
        0x00 = US East, 0x01 = US West, 0x02 = South America
        0x03 = Europe, 0x04 = Asia, 0x05 = Australia
        0x06 = Middle East, 0x07 = Africa, 0xFF = All
        """
        servers = []
        game_filter = self.GAME_FILTERS.get(game_type, "\\gamedir\\ag")

        for master_addr in self.MASTER_SERVERS:
            try:
                result = await self._query_single_master(
                    master_addr, game_filter, region, limit
                )
                servers.extend(result)
                if len(servers) >= limit:
                    break
            except Exception as e:
                logger.warning(f"Master server {master_addr} hatasi: {e}")
                continue

        # Tekrarlari kaldir
        unique_servers = list(set(servers))
        logger.info(f"Master server'dan {len(unique_servers)} sunucu alindi ({game_type.value})")
        return unique_servers[:limit]

    async def _query_single_master(
        self,
        master_addr: Tuple[str, int],
        game_filter: str,
        region: int,
        limit: int
    ) -> List[Tuple[str, int]]:
        """Tek master server sorgula"""
        servers = []
        last_ip = "0.0.0.0:0"

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)

        try:
            while len(servers) < limit:
                # Master server query packet
                # 0x31 = query type, region byte, last_ip, filter string
                packet = b'\x31' + bytes([region])
                packet += last_ip.encode() + b'\x00'
                packet += game_filter.encode() + b'\x00'

                sock.sendto(packet, master_addr)
                data, _ = sock.recvfrom(4096)

                if not data or len(data) < 6:
                    break

                # Response: 0xFF 0xFF 0xFF 0xFF 0x66 0x0A + server list
                if data[:6] != b'\xff\xff\xff\xff\x66\x0a':
                    break

                data = data[6:]

                # 6 byte per server (4 byte IP + 2 byte port)
                while len(data) >= 6:
                    ip_bytes = data[:4]
                    port_bytes = data[4:6]
                    data = data[6:]

                    ip = ".".join(str(b) for b in ip_bytes)
                    port = struct.unpack(">H", port_bytes)[0]

                    if ip == "0.0.0.0" and port == 0:
                        return servers

                    servers.append((ip, port))
                    last_ip = f"{ip}:{port}"

                if len(data) < 6:
                    break

        except socket.timeout:
            pass
        except Exception as e:
            logger.error(f"Master query hatasi: {e}")
        finally:
            sock.close()

        return servers

    # ==================== A2S QUERY ====================

    async def query_server(self, ip: str, port: int) -> Optional[ScrapedServer]:
        """
        Tek sunucuyu A2S protokolu ile sorgula
        """
        async with self._semaphore:
            try:
                address = (ip, port)

                # A2S_INFO sorgusu
                start_time = asyncio.get_event_loop().time()
                info = await asyncio.wait_for(
                    asyncio.to_thread(a2s.info, address, timeout=self.timeout),
                    timeout=self.timeout + 0.5
                )
                ping = int((asyncio.get_event_loop().time() - start_time) * 1000)

                # Oyun turunu belirle
                game_type = self._detect_game_type(info.folder, info.game)

                server = ScrapedServer(
                    ip=ip,
                    port=port,
                    name=info.server_name,
                    map=info.map_name,
                    players=info.player_count,
                    max_players=info.max_players,
                    game_type=game_type,
                    game_dir=info.folder,
                    ping=ping,
                    password_protected=info.password_protected,
                    vac_enabled=getattr(info, 'vac_enabled', False),
                    os=getattr(info, 'platform', ''),
                    version=getattr(info, 'version', ''),
                    is_online=True,
                    last_seen=datetime.utcnow()
                )

                # Oyuncu listesi (opsiyonel)
                try:
                    players = await asyncio.wait_for(
                        asyncio.to_thread(a2s.players, address, timeout=1.0),
                        timeout=1.5
                    )
                    server.player_list = [
                        {
                            "name": p.name,
                            "score": p.score,
                            "duration": round(p.duration, 1)
                        }
                        for p in players
                    ]
                except Exception:
                    pass

                return server

            except asyncio.TimeoutError:
                return None
            except Exception as e:
                logger.debug(f"Sunucu sorgu hatasi {ip}:{port}: {e}")
                return None

    def _detect_game_type(self, folder: str, game_name: str) -> GameTypeEnum:
        """Oyun turunu tespit et"""
        folder_lower = folder.lower() if folder else ""
        game_lower = game_name.lower() if game_name else ""

        if folder_lower == "ag" or "adrenaline" in game_lower:
            return GameTypeEnum.AG
        elif folder_lower == "cstrike" or "counter-strike" in game_lower:
            return GameTypeEnum.CS16
        elif folder_lower == "tfc":
            return GameTypeEnum.TFC
        elif folder_lower == "dod":
            return GameTypeEnum.DOD
        elif folder_lower == "ricochet":
            return GameTypeEnum.RICOCHET
        else:
            return GameTypeEnum.HLDM

    async def scan_servers(
        self,
        server_list: List[Tuple[str, int]],
        progress_callback=None
    ) -> List[ScrapedServer]:
        """
        Sunucu listesini paralel olarak tara
        """
        results = []
        total = len(server_list)

        tasks = [self.query_server(ip, port) for ip, port in server_list]

        for i, coro in enumerate(asyncio.as_completed(tasks)):
            try:
                server = await coro
                if server:
                    results.append(server)

                if progress_callback and (i + 1) % 10 == 0:
                    progress_callback(i + 1, total, len(results))

            except Exception as e:
                logger.debug(f"Scan hatasi: {e}")

        logger.info(f"Tarama tamamlandi: {len(results)}/{total} sunucu online")
        return results

    # ==================== COMMUNITY SERVER LISTS ====================

    async def fetch_known_servers(self) -> List[Tuple[str, int]]:
        """
        Bilinen topluluk sunucu listelerinden sunucu cek
        """
        servers = []

        # Bilinen AG/HL sunuculari (hardcoded fallback)
        known_servers = [
            # Turkiye AG sunuculari
            ("85.95.238.59", 27015),
            ("85.95.238.59", 27016),
            ("176.53.66.33", 27015),
            ("212.154.206.122", 27015),
            ("193.140.100.101", 27015),
            # Avrupa AG sunuculari
            ("51.91.22.132", 27015),
            ("51.91.22.132", 27016),
            ("145.239.205.5", 27015),
            ("178.32.58.168", 27015),
            # CS 1.6 Turkiye
            ("85.95.238.60", 27015),
            ("176.53.66.34", 27015),
        ]

        servers.extend(known_servers)

        # GameTracker'dan AG sunuculari
        try:
            gt_servers = await self._fetch_gametracker_servers("ag")
            servers.extend(gt_servers)
        except Exception as e:
            logger.warning(f"GameTracker AG hatasi: {e}")

        # GameTracker'dan CS 1.6 sunuculari
        try:
            gt_cs_servers = await self._fetch_gametracker_servers("cs16")
            servers.extend(gt_cs_servers)
        except Exception as e:
            logger.warning(f"GameTracker CS hatasi: {e}")

        # GameTracker'dan HLDM sunuculari
        try:
            gt_hl_servers = await self._fetch_gametracker_servers("hldm")
            servers.extend(gt_hl_servers)
        except Exception as e:
            logger.warning(f"GameTracker HLDM hatasi: {e}")

        return list(set(servers))

    async def _fetch_gametracker_servers(
        self,
        game: str,
        limit: int = 100
    ) -> List[Tuple[str, int]]:
        """
        GameTracker'dan sunucu listesi cek
        """
        servers = []
        client = await self.get_http_client()

        game_map = {
            "ag": "hl",  # AG, HL kategorisinde
            "hldm": "hl",
            "cs16": "cs",
            "tfc": "tfc",
        }

        gt_game = game_map.get(game, "hl")

        try:
            # GameTracker search API
            url = f"https://www.gametracker.com/search/{gt_game}/"
            params = {
                "searchpge": "server",
                "sort": "c_numplayers",
                "order": "DESC",
            }

            response = await client.get(url, params=params)

            if response.status_code == 200:
                # HTML parse (basit regex ile)
                import re
                # IP:Port pattern
                pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{4,5})'
                matches = re.findall(pattern, response.text)

                for ip, port in matches[:limit]:
                    try:
                        servers.append((ip, int(port)))
                    except ValueError:
                        continue

            logger.info(f"GameTracker'dan {len(servers)} {game} sunucusu alindi")

        except Exception as e:
            logger.warning(f"GameTracker fetch hatasi: {e}")

        return servers

    # ==================== FULL SCAN ====================

    async def full_scan(
        self,
        game_types: List[GameTypeEnum] = None,
        include_community: bool = True,
        progress_callback=None
    ) -> Dict[str, List[ScrapedServer]]:
        """
        Tam tarama - master server + topluluk listeleri
        """
        if game_types is None:
            game_types = [GameTypeEnum.AG, GameTypeEnum.CS16, GameTypeEnum.HLDM]

        all_servers = {}
        all_addresses = set()

        # Master server'dan al
        for game_type in game_types:
            try:
                addresses = await self.query_master_server(game_type, limit=300)
                all_addresses.update(addresses)
                logger.info(f"{game_type.value}: {len(addresses)} adres master server'dan")
            except Exception as e:
                logger.error(f"Master server hatasi ({game_type.value}): {e}")

        # Topluluk listelerinden al
        if include_community:
            try:
                community = await self.fetch_known_servers()
                all_addresses.update(community)
                logger.info(f"Topluluk listesinden {len(community)} adres eklendi")
            except Exception as e:
                logger.error(f"Topluluk listesi hatasi: {e}")

        # Tum sunuculari tara
        logger.info(f"Toplam {len(all_addresses)} sunucu taranacak")
        servers = await self.scan_servers(list(all_addresses), progress_callback)

        # Oyun turune gore grupla
        for server in servers:
            game_key = server.game_type.value
            if game_key not in all_servers:
                all_servers[game_key] = []
            all_servers[game_key].append(server)

        # Istatistikler
        total = sum(len(s) for s in all_servers.values())
        logger.info(f"Tarama tamamlandi: {total} online sunucu bulundu")
        for game, srvs in all_servers.items():
            logger.info(f"  - {game}: {len(srvs)} sunucu")

        return all_servers

    # ==================== TURKEY FILTER ====================

    def is_turkish_ip(self, ip: str) -> bool:
        """IP'nin Turkiye'ye ait olup olmadigini kontrol et"""
        try:
            parts = [int(p) for p in ip.split('.')]
            ip_num = (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]

            for start, end in self.TR_IP_RANGES:
                start_parts = [int(p) for p in start.split('.')]
                end_parts = [int(p) for p in end.split('.')]
                start_num = (start_parts[0] << 24) + (start_parts[1] << 16) + (start_parts[2] << 8) + start_parts[3]
                end_num = (end_parts[0] << 24) + (end_parts[1] << 16) + (end_parts[2] << 8) + end_parts[3]

                if start_num <= ip_num <= end_num:
                    return True
            return False
        except Exception:
            return False

    def filter_turkish_servers(self, servers: List[ScrapedServer]) -> List[ScrapedServer]:
        """Sadece Turkiye sunucularini filtrele"""
        return [s for s in servers if self.is_turkish_ip(s.ip)]


# ==================== DATABASE INTEGRATION ====================

async def save_scraped_servers_to_db(
    servers: List[ScrapedServer],
    db: Session,
    source: str = "scraper"
) -> Dict:
    """
    Taranan sunuculari veritabanina kaydet
    CommunityServer modeli kullan
    """
    from app.models.database import CommunityServer, GameType

    stats = {"added": 0, "updated": 0, "errors": 0}

    game_type_map = {
        GameTypeEnum.AG: GameType.AG,
        GameTypeEnum.CS16: GameType.CS16,
        GameTypeEnum.HLDM: GameType.HLDM,
    }

    for server in servers:
        try:
            # Mevcut kaydi kontrol et
            existing = db.query(CommunityServer).filter(
                CommunityServer.ip_address == server.ip,
                CommunityServer.port == server.port
            ).first()

            if existing:
                # Guncelle
                existing.name = server.name[:100] if server.name else existing.name
                existing.current_map = server.map
                existing.current_players = server.players
                existing.max_players = server.max_players
                existing.ping = server.ping
                existing.is_online = server.is_online
                existing.last_seen = server.last_seen
                existing.password_protected = server.password_protected
                stats["updated"] += 1
            else:
                # Yeni ekle
                game_type = game_type_map.get(server.game_type, GameType.HLDM)
                new_server = CommunityServer(
                    ip_address=server.ip,
                    port=server.port,
                    name=server.name[:100] if server.name else f"Server {server.address}",
                    game_type=game_type,
                    game_dir=server.game_dir,
                    current_map=server.map,
                    current_players=server.players,
                    max_players=server.max_players,
                    ping=server.ping,
                    is_online=server.is_online,
                    password_protected=server.password_protected,
                    source=source,
                    last_seen=server.last_seen
                )
                db.add(new_server)
                stats["added"] += 1

        except Exception as e:
            logger.error(f"Sunucu kayit hatasi {server.address}: {e}")
            stats["errors"] += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"DB commit hatasi: {e}")
        stats["errors"] += 1

    return stats


# ==================== ASYNC RUNNER ====================

async def run_scraper_task(
    game_types: List[str] = None,
    db: Session = None
) -> Dict:
    """
    Scraper gorevini calistir (background task icin)
    """
    scraper = ServerScraper(timeout=2.0, max_concurrent=100)

    try:
        # Oyun turlerini enum'a cevir
        if game_types:
            types = []
            for gt in game_types:
                try:
                    types.append(GameTypeEnum(gt))
                except ValueError:
                    continue
        else:
            types = [GameTypeEnum.AG, GameTypeEnum.CS16, GameTypeEnum.HLDM]

        # Tarama yap
        results = await scraper.full_scan(game_types=types)

        # Veritabanina kaydet
        stats = {"total_found": 0, "db_stats": {}}
        if db:
            all_servers = []
            for game_servers in results.values():
                all_servers.extend(game_servers)

            stats["total_found"] = len(all_servers)
            stats["db_stats"] = await save_scraped_servers_to_db(all_servers, db)

        return {
            "success": True,
            "games_scanned": [t.value for t in types],
            "servers_by_game": {k: len(v) for k, v in results.items()},
            **stats
        }

    except Exception as e:
        logger.error(f"Scraper task hatasi: {e}")
        return {"success": False, "error": str(e)}

    finally:
        await scraper.close()
