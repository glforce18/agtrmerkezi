# AGTR Anti-Cheat - FastAPI Integration
**Date:** 2026-01-24
**Status:** ✅ COMPLETED
**Task:** #8 - Migrate to FastAPI and integrate with AGTR Merkezi

---

## Summary

Anti-cheat data from the halflife database is now accessible through FastAPI endpoints with Role-Based Access Control (RBAC). Server owners can only see their own server's anti-cheat data, while superadmins can see all servers.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  AGTR Merkezi (FastAPI - Port 8000)                    │
│  ───────────────────────────────────────────────────── │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │  /api/anticheat/* Endpoints                   │    │
│  │  ─────────────────────────────────────────── │    │
│  │  • RBAC Middleware (verify_server_access)    │    │
│  │  • Server ownership check                    │    │
│  │  • Superadmin bypass                         │    │
│  └───────────────────────────────────────────────┘    │
│                         │                              │
│                         ↓                              │
│  ┌───────────────────────────────────────────────┐    │
│  │  Database Connections                         │    │
│  │  ─────────────────────────────────────────── │    │
│  │  • agtrmerkezi DB - User & server ownership  │    │
│  │  • halflife DB - Anti-cheat scan data        │    │
│  └───────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                         │
                         ↓
         ┌───────────────────────────────┐
         │  halflife Database            │
         │  ─────────────────────────── │
         │  • agtr_scans (server_id)    │
         │  • agtr_player_info          │
         │  • agtr_hwid_bans            │
         │  • agtr_server_mapping       │
         └───────────────────────────────┘
```

---

## Files Created/Modified

### New Files

**1. `/var/www/agtrmerkezi/app/api/anticheat.py` (650 lines)**
```python
# Anti-Cheat API endpoints with RBAC
- Scan endpoints
- Player endpoints
- Ban endpoints
- Dashboard endpoint
```

**2. `/var/www/agtrmerkezi/ANTICHEAT_API_INTEGRATION.md`**
- This documentation file

### Modified Files

**1. `/var/www/agtrmerkezi/app/models/connection.py`**
```python
# Added halflife database connection
+ init_halflife_db()
+ get_halflife_db()  # Dependency injection
+ halflife_db_session()  # Context manager
```

**2. `/var/www/agtrmerkezi/app/main.py`**
```python
# Import anticheat router
+ from app.api import anticheat

# Register router
+ app.include_router(anticheat.router, tags=["Anti-Cheat"])

# Initialize halflife DB on startup
+ init_halflife_db()
```

**3. `/home/halflife/agtr-anticheat/` (Organized folder)**
```
agtr-anticheat/
├── README.md
├── .env
├── .gitignore
├── config_loader.py
├── authentication.py
├── migrations/
│   ├── 001_add_server_mapping.sql
│   ├── 002_add_performance_indexes.sql
│   └── 003_add_client_server_tracking.sql
└── docs/
    ├── MULTI_TENANT_ARCHITECTURE.md
    ├── SECURITY_IMPROVEMENTS.md
    └── TASK_6_COMPLETION_REPORT.md
```

---

## API Endpoints

### Base URL
```
https://agtrmerkezi.com/api/anticheat
```

### Authentication
All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

---

### 1. Get Server Scans
```http
GET /api/anticheat/servers/{server_id}/scans
```

**Query Parameters:**
- `limit` (int, default: 50) - Number of scans to return
- `offset` (int, default: 0) - Pagination offset
- `passed` (bool, optional) - Filter by pass status (true=clean, false=suspicious)

**Response:**
```json
{
  "server_id": 1,
  "scans": [
    {
      "id": 14185,
      "hwid": "687475512CB60EAA4445534B",
      "server_id": 1,
      "passed": true,
      "sus_count": 0,
      "hash_count": 15,
      "player_name": "zzorn",
      "player_steamid": "STEAM_0:0:431466575",
      "scan_time": "2026-01-24 22:16:58",
      "version": "12.4",
      "current_name": "zzorn",
      "current_steamid": "STEAM_0:0:431466575",
      "player_ip": "185.171.25.138"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

**Access Control:**
- Server owner: ✅ Can access
- Superadmin: ✅ Can access
- Other users: ❌ 403 Forbidden

---

### 2. Get Scan Detail
```http
GET /api/anticheat/servers/{server_id}/scans/{scan_id}
```

**Response:**
```json
{
  "id": 14185,
  "hwid": "687475512CB60EAA4445534B",
  "passed": true,
  "sus_count": 0,
  "scan_time": "2026-01-24 22:16:58",
  "processes": [
    {
      "name": "chrome.exe",
      "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
      "pid": 1234,
      "is_suspicious": false
    }
  ],
  "modules": [
    {
      "name": "kernel32.dll",
      "path": "C:\\Windows\\System32\\kernel32.dll",
      "hash": "abc123...",
      "size": 1048576
    }
  ],
  "windows": [
    {
      "title": "Google Chrome",
      "class_name": "Chrome_WidgetWin_1",
      "is_suspicious": false
    }
  ],
  "hashes": [
    {
      "filename": "file1.dll",
      "hash": "def456..."
    }
  ]
}
```

---

### 3. Get Server Stats
```http
GET /api/anticheat/servers/{server_id}/stats?days=7
```

**Query Parameters:**
- `days` (int, default: 7, max: 90) - Number of days to include

**Response:**
```json
{
  "total_scans": 1250,
  "clean_scans": 1200,
  "suspicious_scans": 50,
  "flagged_scans": 75,
  "unique_players": 150,
  "unique_steamids": 145,
  "last_scan": "2026-01-24 22:16:58",
  "daily_trend": [
    {
      "date": "2026-01-24",
      "total": 180,
      "suspicious": 5
    },
    {
      "date": "2026-01-23",
      "total": 165,
      "suspicious": 8
    }
  ]
}
```

---

### 4. Get Server Players
```http
GET /api/anticheat/servers/{server_id}/players
```

**Query Parameters:**
- `limit` (int, default: 50)
- `offset` (int, default: 0)
- `search` (string, optional) - Search by name or SteamID

**Response:**
```json
{
  "server_id": 1,
  "players": [
    {
      "hwid": "687475512CB60EAA4445534B",
      "name": "Player1",
      "steamid": "STEAM_0:0:123456",
      "ip": "185.171.25.138",
      "last_seen": "2026-01-24 22:16:58",
      "scan_count": 25,
      "failed_scans": 2
    }
  ],
  "limit": 50,
  "offset": 0
}
```

---

### 5. Get Player Detail
```http
GET /api/anticheat/servers/{server_id}/players/{hwid}
```

**Response:**
```json
{
  "hwid": "687475512CB60EAA4445534B",
  "name": "Player1",
  "steamid": "STEAM_0:0:123456",
  "ip": "185.171.25.138",
  "last_seen": "2026-01-24 22:16:58",
  "scans": [
    {
      "id": 14185,
      "scan_time": "2026-01-24 22:16:58",
      "passed": true,
      "sus_count": 0,
      "version": "12.4"
    }
  ],
  "bans": [
    {
      "id": 5,
      "hwid": "687475512CB60EAA4445534B",
      "reason": "Cheat detected",
      "server_id": 1,
      "is_active": true,
      "created_at": "2026-01-20 15:30:00",
      "expires_at": null,
      "banned_by": "admin159"
    }
  ]
}
```

---

### 6. Get Server Bans
```http
GET /api/anticheat/servers/{server_id}/bans
```

**Response:**
```json
{
  "server_bans": [
    {
      "id": 5,
      "hwid": "abc123...",
      "reason": "Aimbot detected",
      "server_id": 1,
      "is_active": true,
      "created_at": "2026-01-20 15:30:00",
      "expires_at": null,
      "banned_by": "admin159"
    }
  ],
  "global_bans": [
    {
      "id": 10,
      "hwid": "def456...",
      "reason": "Multiple cheat detections",
      "server_id": null,
      "is_active": true,
      "created_at": "2026-01-15 10:00:00",
      "expires_at": null,
      "banned_by": "glforce"
    }
  ]
}
```

**Note:** `global_bans` only returned for superadmins.

---

### 7. Create Server Ban
```http
POST /api/anticheat/servers/{server_id}/bans
```

**Request Body:**
```json
{
  "hwid": "687475512CB60EAA4445534B",
  "reason": "Aimbot detected",
  "duration_days": 30
}
```

**Response:**
```json
{
  "status": "success",
  "message": "HWID 687475512CB60EAA4445534B banned on server 1",
  "expires_at": "2026-02-23 22:30:00"
}
```

**Access Control:**
- Server owner: ✅ Can ban on their server only
- Superadmin: ✅ Can ban on any server

---

### 8. Delete Server Ban
```http
DELETE /api/anticheat/servers/{server_id}/bans/{ban_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Ban removed"
}
```

---

### 9. Get Dashboard
```http
GET /api/anticheat/dashboard
```

**Response:**
```json
{
  "servers": [
    {
      "server_id": 1,
      "server_name": "AG #1",
      "unique_code": "AG#1",
      "total_scans": 1250,
      "suspicious_scans": 50,
      "last_scan": "2026-01-24 22:16:58",
      "unique_players": 150
    },
    {
      "server_id": 2,
      "server_name": "AG #2",
      "unique_code": "AG#2",
      "total_scans": 980,
      "suspicious_scans": 35,
      "last_scan": "2026-01-24 21:45:12",
      "unique_players": 120
    }
  ],
  "total_scans": 2230,
  "total_suspicious": 85,
  "period_days": 7
}
```

**Access Control:**
- Regular user: Shows only their owned servers
- Superadmin: Shows all servers

---

## RBAC Implementation

### Helper Functions

**1. `get_user_server_ids(user, db) -> List[int] | None`**
- Returns list of server IDs owned by user
- Returns `None` for superadmins (= all servers)

**2. `verify_server_access(user, server_id, db) -> bool`**
- Verifies user owns the server or is superadmin
- Raises HTTPException 403 if denied

**3. `check_anticheat_subscription(server_id, db) -> bool`**
- Checks if server has active anti-cheat subscription
- Currently returns `True` (future: check actual subscription)

### Access Control Matrix

| Endpoint | Server Owner | Superadmin | Other Users |
|----------|-------------|------------|-------------|
| GET /servers/{id}/scans | ✅ Own server only | ✅ All servers | ❌ 403 |
| GET /servers/{id}/stats | ✅ Own server only | ✅ All servers | ❌ 403 |
| GET /servers/{id}/players | ✅ Own server only | ✅ All servers | ❌ 403 |
| GET /servers/{id}/bans | ✅ Own + global* | ✅ All + global | ❌ 403 |
| POST /servers/{id}/bans | ✅ Own server only | ✅ All servers | ❌ 403 |
| DELETE /servers/{id}/bans | ✅ Own server only | ✅ All servers | ❌ 403 |
| GET /dashboard | ✅ Own servers | ✅ All servers | ❌ Empty |

*Server owners see global bans (read-only) but can only create/delete server-specific bans.

---

## Database Connections

### Primary Database (`agtrmerkezi`)
```python
from app.models.connection import get_db

# Contains:
- users (user accounts, roles)
- game_servers (server ownership)
```

### Anti-Cheat Database (`halflife`)
```python
from app.models.connection import get_halflife_db

# Contains:
- agtr_scans (scan data with server_id)
- agtr_player_info (player data)
- agtr_hwid_bans (server-specific + global)
- agtr_server_mapping (server IP:port → server_id)
- agtr_client_server_tracking (client IP tracking)
```

### Connection Configuration
```python
# /var/www/agtrmerkezi/app/models/connection.py

halflife_url = "mysql+pymysql://root:sedatim@localhost:3306/halflife?charset=utf8mb4"

halflife_engine = create_engine(
    halflife_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

---

## Testing

### 1. Check API Documentation
```bash
curl https://agtrmerkezi.com/api/docs
# Should show "Anti-Cheat" tag with all endpoints
```

### 2. Test Dashboard (Superadmin)
```bash
# Get access token
TOKEN="..."

curl -X GET "http://localhost:8000/api/anticheat/dashboard" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Test Server Scans
```bash
curl -X GET "http://localhost:8000/api/anticheat/servers/1/scans?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Test Access Control (Should fail for non-owner)
```bash
# User who doesn't own server_id=1
curl -X GET "http://localhost:8000/api/anticheat/servers/1/scans" \
  -H "Authorization: Bearer $TOKEN"

# Expected: HTTP 403 Forbidden
```

---

## Next Steps (Not Implemented Yet)

### 1. Vue.js Frontend Integration
**File:** `/var/www/agtrmerkezi/frontend/src/views/ServerManagement.vue`

Add "Anti-Cheat" tab to server management page:
```vue
<template>
  <v-tabs>
    <v-tab>Overview</v-tab>
    <v-tab>Console</v-tab>
    <v-tab>Anti-Cheat</v-tab>  <!-- NEW -->
  </v-tabs>

  <v-tab-item>
    <!-- Anti-cheat dashboard -->
    <AntiCheatDashboard :server-id="serverId" />
  </v-tab-item>
</template>
```

### 2. Anti-Cheat Dashboard Component
**File:** `/var/www/agtrmerkezi/frontend/src/components/AntiCheatDashboard.vue`

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { anticheatApi } from '@/api/anticheat'

const props = defineProps(['serverId'])
const scans = ref([])
const stats = ref({})

onMounted(async () => {
  stats.value = await anticheatApi.getServerStats(props.serverId)
  scans.value = await anticheatApi.getServerScans(props.serverId, { limit: 50 })
})
</script>

<template>
  <div>
    <v-row>
      <v-col cols="3">
        <v-card>
          <v-card-title>Total Scans</v-card-title>
          <v-card-text>{{ stats.total_scans }}</v-card-text>
        </v-card>
      </v-col>
      <v-col cols="3">
        <v-card color="success">
          <v-card-title>Clean</v-card-title>
          <v-card-text>{{ stats.clean_scans }}</v-card-text>
        </v-card>
      </v-col>
      <v-col cols="3">
        <v-card color="error">
          <v-card-title>Suspicious</v-card-title>
          <v-card-text>{{ stats.suspicious_scans }}</v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-data-table
      :items="scans.scans"
      :headers="headers"
      @click:row="showScanDetail"
    />
  </div>
</template>
```

### 3. API Client
**File:** `/var/www/agtrmerkezi/frontend/src/api/anticheat.js`

```javascript
import axios from 'axios'

export const anticheatApi = {
  async getServerScans(serverId, params) {
    const { data } = await axios.get(`/api/anticheat/servers/${serverId}/scans`, { params })
    return data
  },

  async getServerStats(serverId, days = 7) {
    const { data } = await axios.get(`/api/anticheat/servers/${serverId}/stats`, {
      params: { days }
    })
    return data
  },

  async getServerPlayers(serverId, params) {
    const { data } = await axios.get(`/api/anticheat/servers/${serverId}/players`, { params })
    return data
  },

  async createBan(serverId, banData) {
    const { data } = await axios.post(`/api/anticheat/servers/${serverId}/bans`, banData)
    return data
  },

  async deleteBan(serverId, banId) {
    const { data } = await axios.delete(`/api/anticheat/servers/${serverId}/bans/${banId}`)
    return data
  },

  async getDashboard() {
    const { data } = await axios.get('/api/anticheat/dashboard')
    return data
  }
}
```

### 4. Subscription Model
**File:** `/var/www/agtrmerkezi/app/models/database.py`

Add column to GameServer model:
```python
class GameServer(Base):
    __tablename__ = "game_servers"

    # Existing columns...
    anticheat_enabled = Column(Boolean, default=False)
    anticheat_expires_at = Column(DateTime, nullable=True)
```

**Migration:**
```sql
ALTER TABLE game_servers
ADD COLUMN anticheat_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN anticheat_expires_at DATETIME NULL;
```

**Update `check_anticheat_subscription()`:**
```python
def check_anticheat_subscription(server_id: int, db: Session) -> bool:
    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        return False

    if not server.anticheat_enabled:
        return False

    if server.anticheat_expires_at and server.anticheat_expires_at < datetime.now():
        return False

    return True
```

---

## Subscription Pricing

**Price:** 20 TL/month (already in config: `PRICE_ANTICHEAT = 20.0`)

**Features by Plan:**

### Basic (Free)
- View scan history (last 7 days)
- Basic statistics
- Read-only ban list

### Premium (20 TL/month)
- ✅ Full scan history
- ✅ Advanced analytics (90 days)
- ✅ Real-time scan notifications
- ✅ HWID ban management
- ✅ Custom whitelist
- ✅ Export reports

### Implementation in Payment System
```python
# /var/www/agtrmerkezi/app/api/payments.py

@router.post("/purchase/anticheat/{server_id}")
async def purchase_anticheat(
    server_id: int,
    months: int = 1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify server ownership
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Calculate price
    price = PRICE_ANTICHEAT * months

    # Check user balance
    if current_user.balance < price:
        raise HTTPException(status_code=402, detail="Insufficient balance")

    # Deduct from balance
    current_user.balance -= price

    # Activate anti-cheat
    if server.anticheat_expires_at and server.anticheat_expires_at > datetime.now():
        # Extend existing subscription
        server.anticheat_expires_at += timedelta(days=30 * months)
    else:
        # New subscription
        server.anticheat_enabled = True
        server.anticheat_expires_at = datetime.now() + timedelta(days=30 * months)

    db.commit()

    return {
        "status": "success",
        "message": f"Anti-cheat activated for {months} month(s)",
        "expires_at": server.anticheat_expires_at
    }
```

---

## Performance Considerations

### Query Optimization
- All queries use indexes (created in migration 002)
- Server-specific queries use `idx_scans_server_time`
- Player queries use `idx_scans_server_steamid`
- Ban queries use `idx_hwid_ban_server` and `idx_hwid_ban_global`

### Caching (Future)
```python
from app.models.connection import redis_get, redis_set

@router.get("/servers/{server_id}/stats")
async def get_server_anticheat_stats(...):
    cache_key = f"anticheat:stats:{server_id}:{days}"

    # Check cache
    cached = redis_get(cache_key)
    if cached:
        return json.loads(cached)

    # Query database
    stats = ...

    # Cache for 5 minutes
    redis_set(cache_key, json.dumps(stats), expire=300)

    return stats
```

---

## Security

### SQL Injection Prevention
- All queries use SQLAlchemy text() with bound parameters
- No string concatenation in SQL

### Access Control
- Every endpoint verifies server ownership
- Superadmin bypass for admin features
- JWT authentication required

### Rate Limiting (Future)
```python
from app.middleware.rate_limit import rate_limit

@router.get("/servers/{server_id}/scans")
@rate_limit(max_requests=100, window_seconds=60)
async def get_server_scans(...):
    ...
```

---

## Monitoring

### Logging
```python
logger.info(f"Server ban created: {hwid} on server {server_id} by {current_user.username}")
logger.warning(f"Unauthorized access attempt: user {current_user.id} tried to access server {server_id}")
```

### Metrics (Future)
- Total API calls per endpoint
- Average response time
- Most active servers
- Ban creation rate

---

## Completion Checklist

- ✅ Anti-cheat API endpoints created
- ✅ RBAC middleware implemented
- ✅ Server ownership verification
- ✅ Halflife database connection
- ✅ Multi-tenant queries (with server_id)
- ✅ FastAPI router registration
- ✅ Service restarted successfully
- ✅ Endpoints accessible in /api/docs
- ⏳ Vue.js frontend integration (next)
- ⏳ Subscription model activation (next)
- ⏳ Payment system integration (next)

---

## Summary

Task #8 başarıyla tamamlandı! Anti-cheat verileri artık FastAPI üzerinden RBAC ile sunuluyor:

**Server Sahipleri:**
- Sadece kendi serverlarının scan, player ve ban verilerini görebilir
- Kendi serverlarında ban oluşturup kaldırabilir
- Global ban listesini görebilir (read-only)

**Superadminler:**
- Tüm serverlerin verilerini görebilir
- Global ban oluşturup yönetebilir
- Tüm serverlerde ban yetkisi var

**Sonraki Adım:**
Vue.js frontend'e "Anti-Cheat" tab'i ekleyip, server yönetim sayfasından kullanıcıların kendi serverlarının anti-cheat verilerini görüntülemesini sağlamak.
