# AGTR Merkezi v6.0 - API Reference

## Base URL
```
Production: https://agtrmerkezi.com/api/v2
Development: http://localhost:8000/api/v2
```

## Authentication
All endpoints require JWT Bearer token authentication unless specified otherwise.

```http
Authorization: Bearer {your_jwt_token}
```

---

## 1. Auto Admin System

### Sync Owner as Admin
Manually synchronize server owner as admin.

**Endpoint:** `POST /servers/{server_id}/admins/sync-owner`

**Parameters:**
- `server_id` (path, required): Server ID

**Response:**
```json
{
  "success": true,
  "message": "Sahip otomatik olarak admin eklendi"
}
```

**Errors:**
- `403`: Not authorized (not server owner)
- `404`: Server or user not found
- `400`: Steam ID not found

**Example:**
```bash
curl -X POST \
  https://agtrmerkezi.com/api/v2/servers/123/admins/sync-owner \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 2. Scheduler - Zamanlanmış Görevler

### List Scheduled Tasks
Get all scheduled tasks for a server.

**Endpoint:** `GET /servers/{server_id}/scheduler/tasks`

**Response:**
```json
[
  {
    "id": 1,
    "server_id": 123,
    "task_name": "Günlük Restart",
    "task_type": "restart",
    "schedule_type": "cron",
    "cron_minute": "0",
    "cron_hour": "6",
    "cron_day": "*",
    "cron_month": "*",
    "cron_day_of_week": "*",
    "task_config": {},
    "is_enabled": true,
    "created_at": "2025-01-25T10:00:00",
    "created_by": 1,
    "last_run": "2025-01-25T06:00:00",
    "next_run": "2025-01-26T06:00:00",
    "apscheduler_job_id": "server_123_task_1"
  }
]
```

---

### Create Scheduled Task
Create a new scheduled task.

**Endpoint:** `POST /servers/{server_id}/scheduler/tasks`

**Request Body:**
```json
{
  "task_name": "Daily Restart",
  "task_type": "restart",
  "schedule_type": "cron",
  "cron_minute": "0",
  "cron_hour": "6",
  "cron_day": "*",
  "cron_month": "*",
  "cron_day_of_week": "*",
  "task_config": {},
  "is_enabled": true
}
```

**Task Types:**
- `restart` - Server restart
- `map_change` - Change map
- `backup` - Create backup
- `announcement` - Send announcement
- `rcon_command` - Execute RCON command

**Schedule Types:**
- `cron` - Cron-based scheduling
- `interval` - Interval-based scheduling
- `one_time` - One-time execution

**Interval Task Example:**
```json
{
  "task_name": "Restart Every 6 Hours",
  "task_type": "restart",
  "schedule_type": "interval",
  "interval_value": 6,
  "interval_unit": "hours",
  "is_enabled": true
}
```

**Map Change Example:**
```json
{
  "task_name": "Evening Map Change",
  "task_type": "map_change",
  "schedule_type": "cron",
  "cron_minute": "0",
  "cron_hour": "20",
  "task_config": {
    "map": "de_dust2"
  },
  "is_enabled": true
}
```

**Response:**
```json
{
  "id": 1,
  "server_id": 123,
  "task_name": "Daily Restart",
  ...
}
```

---

### Update Scheduled Task
Update an existing scheduled task.

**Endpoint:** `PUT /servers/{server_id}/scheduler/tasks/{task_id}`

**Request Body:** (Same as create, partial updates supported)

**Response:**
```json
{
  "id": 1,
  "task_name": "Updated Task Name",
  ...
}
```

---

### Delete Scheduled Task
Delete a scheduled task.

**Endpoint:** `DELETE /servers/{server_id}/scheduler/tasks/{task_id}`

**Response:**
```json
{
  "success": true
}
```

---

### Get Task Execution History
Get execution history for a task.

**Endpoint:** `GET /servers/{server_id}/scheduler/tasks/{task_id}/executions`

**Query Parameters:**
- `limit` (optional): Maximum number of executions to return (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "task_id": 1,
    "executed_at": "2025-01-25T06:00:00",
    "status": "success",
    "result_message": "Server restarted",
    "execution_time_ms": 3500
  },
  {
    "id": 2,
    "task_id": 1,
    "executed_at": "2025-01-24T06:00:00",
    "status": "failed",
    "result_message": "Server not online",
    "execution_time_ms": 150
  }
]
```

**Status Values:**
- `success` - Task executed successfully
- `failed` - Task execution failed
- `skipped` - Task was skipped (e.g., server offline)

---

## 3. Advanced Statistics

### Get Hourly Stats
Get hourly player statistics.

**Endpoint:** `GET /servers/{server_id}/stats/hourly`

**Query Parameters:**
- `hours` (optional): Number of hours to retrieve (default: 24)

**Response:**
```json
[
  {
    "timestamp": "2025-01-25T14:00:00",
    "avg_players": 12.5,
    "max_players": 28,
    "unique_players": 35,
    "map": "de_dust2"
  }
]
```

---

### Get Daily Stats
Get daily player statistics.

**Endpoint:** `GET /servers/{server_id}/stats/daily`

**Query Parameters:**
- `days` (optional): Number of days to retrieve (default: 30)

**Response:**
```json
[
  {
    "date": "2025-01-25",
    "total_players": 245,
    "unique_players": 189,
    "avg_players": 12.5,
    "max_players": 28,
    "peak_hour": 20,
    "most_played_map": "de_dust2"
  }
]
```

---

### Get Peak Hours Heatmap
Get 24x7 player activity heatmap.

**Endpoint:** `GET /servers/{server_id}/stats/heatmap`

**Query Parameters:**
- `days` (optional): Number of days to analyze (default: 30)

**Response:**
```json
{
  "hours": [0, 1, 2, ..., 23],
  "days": ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"],
  "data": [
    [2.5, 1.8, 2.0, 3.2, 4.5, 6.8, 5.2],  // Hour 0
    [1.2, 0.8, 1.1, 1.5, 2.3, 4.2, 3.8],  // Hour 1
    ...
    [8.5, 7.2, 8.9, 9.5, 12.3, 15.8, 14.2] // Hour 23
  ]
}
```

**Usage:**
```javascript
// data[hour][day_of_week] = avg_players
const avgPlayersAt20OnFriday = data[20][4]; // 12.3
```

---

### Get Retention Rate
Get player retention metrics.

**Endpoint:** `GET /servers/{server_id}/stats/retention`

**Query Parameters:**
- `days` (optional): Period to calculate (default: 7)

**Response:**
```json
{
  "total_players": 245,
  "returning_players": 168,
  "retention_rate": 68.57
}
```

**Calculation:**
```
retention_rate = (returning_players / total_players) * 100
returning_players = players who joined on 2+ different days
```

---

### Get Map Distribution
Get map playtime distribution.

**Endpoint:** `GET /servers/{server_id}/stats/maps`

**Query Parameters:**
- `days` (optional): Period to analyze (default: 7)

**Response:**
```json
{
  "labels": ["de_dust2", "de_inferno", "de_nuke", "de_mirage", "cs_office"],
  "data": [450, 320, 280, 195, 120]
}
```

**Note:** Data values are in minutes.

---

### Export Stats to CSV
Export statistics to CSV file.

**Endpoint:** `GET /servers/{server_id}/stats/export`

**Query Parameters:**
- `date_from` (required): Start date (YYYY-MM-DD)
- `date_to` (required): End date (YYYY-MM-DD)

**Response:** CSV file download

**CSV Format:**
```csv
Tarih,Toplam Oyuncu,Benzersiz Oyuncu,Ortalama Oyuncu,Max Oyuncu,En Çok Oynanan Harita
2025-01-25,245,189,12.5,28,de_dust2
2025-01-24,223,201,11.8,25,de_inferno
```

**Example:**
```bash
curl -X GET \
  "https://agtrmerkezi.com/api/v2/servers/123/stats/export?date_from=2025-01-01&date_to=2025-01-25" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o stats.csv
```

---

## 4. File Manager

### Browse Directory
List files and directories.

**Endpoint:** `GET /servers/{server_id}/files/browse`

**Query Parameters:**
- `path` (optional): Directory path relative to server root (default: "")

**Response:**
```json
{
  "current_path": "cstrike",
  "items": [
    {
      "name": "addons",
      "type": "directory",
      "size": 0,
      "modified": "2025-01-25T10:30:00",
      "path": "cstrike/addons"
    },
    {
      "name": "server.cfg",
      "type": "file",
      "size": 2048,
      "modified": "2025-01-25T14:20:00",
      "path": "cstrike/server.cfg"
    }
  ]
}
```

---

### Read File
Read file contents.

**Endpoint:** `GET /servers/{server_id}/files/read`

**Query Parameters:**
- `path` (required): File path relative to server root

**Response:**
```json
{
  "content": "hostname \"My Server\"\nrcon_password \"secret\"\n...",
  "language": "ini",
  "size": 2048,
  "modified": "2025-01-25T14:20:00"
}
```

**Language Detection:**
| Extension | Language |
|-----------|----------|
| .cfg, .ini | ini |
| .sma, .inc | cpp |
| .json | json |
| .sh | shell |
| .md | markdown |
| .txt, .log | plaintext |

**Errors:**
- `400`: Not a file / File too large (> 5MB)
- `403`: Path traversal attempt
- `404`: File not found

---

### Write File
Write file contents.

**Endpoint:** `POST /servers/{server_id}/files/write`

**Query Parameters:**
- `path` (required): File path relative to server root

**Request Body:**
```json
{
  "content": "hostname \"Updated Server Name\"\n..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "File saved successfully"
}
```

**Note:** Automatic backup is created before writing (filename.backup.YYYYMMDD_HHMMSS)

---

### Upload File
Upload file to server.

**Endpoint:** `POST /servers/{server_id}/files/upload`

**Query Parameters:**
- `directory` (required): Target directory path

**Request:** multipart/form-data
```
Content-Type: multipart/form-data
file: [binary data]
```

**Response:**
```json
{
  "success": true,
  "filename": "uploaded_file.cfg",
  "size": 2048
}
```

**Limits:**
- Max size: 50MB
- Allowed extensions: .cfg, .ini, .txt, .log, .sma, .amxx, .inc, .json, .md, .wav, .mp3, .bmp, .tga, .mdl, .spr

**Example:**
```bash
curl -X POST \
  "https://agtrmerkezi.com/api/v2/servers/123/files/upload?directory=cstrike" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@myfile.cfg"
```

---

### Delete File/Directory
Delete file or directory.

**Endpoint:** `DELETE /servers/{server_id}/files/delete`

**Query Parameters:**
- `path` (required): File/directory path

**Response:**
```json
{
  "success": true,
  "message": "File deleted (backup created)"
}
```

**Protected Files:**
- hlds_linux
- hlds_run
- steamclient.so

---

### Create Directory
Create new directory.

**Endpoint:** `POST /servers/{server_id}/files/mkdir`

**Query Parameters:**
- `parent_path` (required): Parent directory path

**Request Body:**
```json
{
  "name": "new_folder"
}
```

**Response:**
```json
{
  "success": true,
  "path": "cstrike/new_folder"
}
```

---

## 5. Plugin Manager

### List Plugins
List installed AMXModX plugins.

**Endpoint:** `GET /servers/{server_id}/plugins/list`

**Response:**
```json
[
  {
    "filename": "admincmd.amxx",
    "name": "Admin Commands",
    "version": "1.8.2",
    "author": "AMXX Dev Team",
    "size": 45678,
    "modified": "2025-01-25T10:00:00",
    "enabled": true
  },
  {
    "filename": "myplugin.amxx",
    "name": "myplugin",
    "version": "Unknown",
    "author": "Unknown",
    "size": 12345,
    "modified": "2025-01-24T15:30:00",
    "enabled": false
  }
]
```

**Note:** Plugin metadata is extracted from .amxx binary (heuristic-based).

---

### Enable Plugin
Enable a plugin by adding it to plugins.ini.

**Endpoint:** `POST /servers/{server_id}/plugins/{filename}/enable`

**Parameters:**
- `filename` (path, required): Plugin filename (e.g., "myplugin.amxx")

**Response:**
```json
{
  "success": true,
  "message": "Plugin enabled"
}
```

**Effect:**
```ini
# plugins.ini before:
adminvote.amxx
; myplugin.amxx

# plugins.ini after:
adminvote.amxx
myplugin.amxx
```

---

### Disable Plugin
Disable a plugin by commenting it in plugins.ini.

**Endpoint:** `POST /servers/{server_id}/plugins/{filename}/disable`

**Response:**
```json
{
  "success": true,
  "message": "Plugin disabled"
}
```

**Effect:**
```ini
# plugins.ini before:
adminvote.amxx
myplugin.amxx

# plugins.ini after:
adminvote.amxx
; myplugin.amxx
```

---

### Upload Plugin
Upload .amxx plugin file.

**Endpoint:** `POST /servers/{server_id}/plugins/upload`

**Request:** multipart/form-data
```
Content-Type: multipart/form-data
file: [binary .amxx file]
```

**Response:**
```json
{
  "success": true,
  "message": "Plugin uploaded successfully"
}
```

**Limits:**
- Max size: 10MB
- Extension: .amxx only

**Note:** If plugin already exists, backup is created before overwriting.

---

### Delete Plugin
Delete plugin file.

**Endpoint:** `DELETE /servers/{server_id}/plugins/{filename}`

**Response:**
```json
{
  "success": true,
  "message": "Plugin deleted"
}
```

**Behavior:**
1. If plugin is enabled, it's automatically disabled first
2. Backup is created in .backups/{timestamp}/
3. Plugin file is deleted

---

### Compile Plugin
Compile .sma source file to .amxx.

**Endpoint:** `POST /servers/{server_id}/plugins/compile/{sma_filename}`

**Parameters:**
- `sma_filename` (path, required): Source filename (e.g., "myplugin.sma")

**Response:**
```json
{
  "success": true,
  "message": "Plugin compiled: myplugin.amxx"
}
```

**Process:**
1. Locate .sma file in scripting/ directory
2. Run amxxpc compiler
3. Move compiled .amxx to plugins/ directory

**Errors:**
```json
{
  "success": false,
  "message": "Compilation failed: error line 42: expected ';'"
}
```

**Timeout:** 30 seconds

---

### Get Marketplace Plugins
Get curated list of popular plugins.

**Endpoint:** `GET /servers/{server_id}/plugins/marketplace`

**Response:**
```json
[
  {
    "name": "Admin Commands",
    "filename": "admincmd.amxx",
    "description": "Essential admin commands",
    "category": "Admin Tools",
    "download_url": "https://example.com/admincmd.amxx"
  },
  {
    "name": "Map Manager",
    "filename": "mapmanager.amxx",
    "description": "Advanced map voting and rotation",
    "category": "Server Management",
    "download_url": "https://example.com/mapmanager.amxx"
  }
]
```

**Categories:**
- Admin Tools
- Server Management
- Gameplay
- Fun

---

## Error Responses

All endpoints return consistent error format:

```json
{
  "detail": "Error message"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (no/invalid token) |
| 403 | Forbidden (not server owner) |
| 404 | Not Found (server/resource not found) |
| 500 | Internal Server Error |

### Common Errors

**Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**Forbidden:**
```json
{
  "detail": "Not authorized to access this server"
}
```

**Not Found:**
```json
{
  "detail": "Server not found"
}
```

**Validation Error:**
```json
{
  "detail": "Only .amxx files allowed"
}
```

---

## Rate Limits

- General API: 1000 requests/minute
- File uploads: 50 requests/minute
- Compilation: 10 requests/minute

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1706180400
```

---

## Pagination

Currently not implemented. All list endpoints return full results.

Future implementation:
```
?page=1&limit=50
```

---

## Filtering & Sorting

Currently not implemented.

Future implementation:
```
?filter[status]=enabled&sort=-created_at
```

---

## WebSocket (Future)

Real-time updates via WebSocket:

```javascript
// Connect
const ws = new WebSocket('wss://agtrmerkezi.com/ws/servers/123');

// Subscribe to stats
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'stats'
}));

// Receive updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // { type: 'stats_update', avg_players: 12.5, ... }
};
```

---

## Swagger/OpenAPI

Interactive API documentation available at:
```
https://agtrmerkezi.com/api/docs
```

---

## SDK/Client Libraries

### JavaScript/TypeScript
```javascript
import { AGTRClient } from '@agtr/client';

const client = new AGTRClient({
  baseURL: 'https://agtrmerkezi.com/api/v2',
  token: 'YOUR_JWT_TOKEN'
});

// List plugins
const plugins = await client.plugins.list(123);

// Create scheduled task
const task = await client.scheduler.create(123, {
  task_name: 'Daily Restart',
  task_type: 'restart',
  schedule_type: 'cron',
  cron_hour: '6'
});
```

### Python
```python
from agtr_client import AGTRClient

client = AGTRClient(
    base_url='https://agtrmerkezi.com/api/v2',
    token='YOUR_JWT_TOKEN'
)

# List plugins
plugins = client.plugins.list(server_id=123)

# Enable plugin
client.plugins.enable(server_id=123, filename='myplugin.amxx')
```

---

## Changelog

- **v6.0.0** (2025-01-25): 5 advanced features added
  - Auto Admin System
  - Scheduler
  - Advanced Statistics
  - File Manager
  - Plugin Manager

---

## Support

- Documentation: `/docs`
- API Status: `https://status.agtrmerkezi.com`
- Support: support@agtrmerkezi.com
