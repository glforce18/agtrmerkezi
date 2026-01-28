# AGTR Merkezi v6.0 - Implementation Notes

## 📋 Implementation Summary

This document contains technical implementation details, architectural decisions, and development notes for the 5 advanced features added in v6.0.

---

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Vue 3)                     │
│  ┌──────────┬──────────┬──────────┬──────────────────┐  │
│  │Scheduler │  Stats   │  Files   │     Plugins      │  │
│  │ Manager  │Dashboard │ Manager  │     Manager      │  │
│  └──────────┴──────────┴──────────┴──────────────────┘  │
│                         │ HTTP/REST                      │
└─────────────────────────┼──────────────────────────────┘
                          │
┌─────────────────────────┼──────────────────────────────┐
│                     Backend (FastAPI)                    │
│  ┌──────────┬──────────┬──────────┬──────────────────┐  │
│  │Scheduler │  Stats   │  File    │     Plugin       │  │
│  │  API     │   API    │ Manager  │     Manager      │  │
│  │          │          │   API    │      API         │  │
│  └──────────┴──────────┴──────────┴──────────────────┘  │
│                         │                                │
│  ┌──────────┬──────────┬──────────┬──────────────────┐  │
│  │Scheduler │  Stats   │  File    │     Plugin       │  │
│  │ Service  │ Service  │ Service  │     Service      │  │
│  │(APSched) │(Aggreg.) │(Security)│   (Compiler)     │  │
│  └──────────┴──────────┴──────────┴──────────────────┘  │
│                         │                                │
└─────────────────────────┼──────────────────────────────┘
                          │
┌─────────────────────────┼──────────────────────────────┐
│                   Database (MySQL)                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  • server_scheduled_tasks                        │   │
│  │  • scheduled_task_executions                     │   │
│  │  • server_stats_daily                            │   │
│  │  • server_stats_weekly                           │   │
│  │  • player_sessions                               │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│               File System                                 │
│  /home/gameservers/servers/server_X/                     │
│  ├── cstrike/                                            │
│  │   ├── addons/amxmodx/                                │
│  │   │   ├── configs/plugins.ini                        │
│  │   │   ├── plugins/*.amxx                             │
│  │   │   └── scripting/                                 │
│  │   │       ├── *.sma                                  │
│  │   │       └── amxxpc (compiler)                      │
│  │   └── *.cfg                                          │
│  └── .backups/                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 1. Auto Admin System

### Implementation Details

**Location:** `/app/services/amxx_admin.py:267`

**Flow:**
```python
def add_owner_as_admin(server_id, owner_id):
    1. Query server and user from database
    2. Validate Steam ID exists
    3. Check for existing admin entry (prevent duplicates)
    4. Create ServerAdminEntry with full flags
    5. Sync to users.ini file
    6. Log operation
    7. Return (success, message)
```

**Integration Point:**
```python
# ServerInstallationService.run_installation()
# After AMXModX setup (line 614)
amxx_service.add_owner_as_admin(server_id, server.owner_id)
```

**Database Schema:**
```python
# Existing model - no changes needed
class ServerAdminEntry(Base):
    steam_id = Column(String(50))
    flags = Column(String(50))  # "abcdefghijklmnopqrstu"
    auth_type = Column(Enum(AdminAuthType))  # STEAM
    ...
```

**File Sync:**
```python
def _sync_admins_to_file(server):
    # Format: "STEAM_ID" "password" "flags" "auth_type"
    '"STEAM_0:1:12345" "" "abcdefghijklmnopqrstu" "ce"'
```

### Design Decisions

**Why not auto-enable on every login?**
- Single automatic setup simplifies user experience
- Manual sync endpoint allows re-sync if users.ini corrupted
- Prevents unnecessary file writes

**Why full flags?**
- Server owner should have complete control
- Prevents permission issues
- Standard practice in AMXModX

---

## 2. Scheduler Service

### Implementation Details

**APScheduler Integration:**
```python
class ServerSchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        self.scheduler.start()
        self.load_all_tasks()  # Load from database

    def _add_job_to_scheduler(self, task):
        # Create APScheduler job
        # Store job_id in database
        # Link to database record
```

**Task Execution:**
```python
async def _execute_task(task_id):
    1. Load task from database
    2. Check server status (skip if offline)
    3. Execute based on task_type:
       - RESTART: ServerControlService.restart_server()
       - MAP_CHANGE: RCONService.send_command("changelevel ...")
       - BACKUP: ServerConfigService.create_full_backup()
       - ANNOUNCEMENT: RCONService.send_command("say ...")
       - RCON_COMMAND: RCONService.send_command(...)
    4. Log execution to ScheduledTaskExecution
    5. Update task.last_run
```

**Persistence:**
```python
# Tasks stored in database
ServerScheduledTask:
    - task_config (JSON)
    - apscheduler_job_id (for tracking)
    - last_run, next_run (for display)

# Jobs recreated on startup
def load_all_tasks():
    tasks = query(ServerScheduledTask).filter(is_enabled=True).all()
    for task in tasks:
        _add_job_to_scheduler(task)
```

### Design Decisions

**Why APScheduler instead of Celery?**
- Simpler setup (no broker required)
- Async/await support
- Lightweight for this use case
- Database-backed persistence

**Why store next_run in database?**
- Fast UI display without scheduler query
- Audit trail
- Backup/restore capability

**Cron vs Interval trade-offs:**
- Cron: Predictable (always at 06:00)
- Interval: Relative (6 hours from last run)
- Both supported for flexibility

---

## 3. Statistics Service

### Data Flow

```
1. Server Monitoring → Hourly Stats (existing)
                          ↓
2. Daily Aggregation (00:05) → ServerStatsDaily
                                     ↓
3. Weekly Aggregation (Monday) → ServerStatsWeekly
```

**Aggregation Logic:**
```python
def aggregate_daily_stats(server_id, target_date):
    # Get all hourly stats for the day
    hourly_stats = query(ServerStatsHourly).filter(
        date >= day_start,
        date < day_end
    ).all()

    # Calculate aggregates
    total_players = sum(s.unique_players)
    avg_players = mean(s.avg_players)
    max_players = max(s.max_players)

    # Find peak hour
    peak_hour_stat = max(hourly_stats, key=lambda s: s.avg_players)
    peak_hour = peak_hour_stat.hour_timestamp.hour

    # Map playtime
    map_counts = Counter(s.most_played_map for s in hourly_stats)
    most_played_map = map_counts.most_common(1)[0][0]

    # Upsert to ServerStatsDaily
```

**Heatmap Calculation:**
```python
def get_peak_hours_heatmap(days=30):
    # Initialize 24x7 grid
    heatmap = [[0] * 7 for _ in range(24)]

    # Sum player counts by hour/day
    for stat in hourly_stats:
        hour = stat.hour_timestamp.hour  # 0-23
        day = stat.hour_timestamp.weekday()  # 0-6
        heatmap[hour][day] += stat.avg_players

    # Average by number of weeks
    weeks = days / 7
    for h in range(24):
        for d in range(7):
            heatmap[h][d] /= weeks

    return heatmap
```

**Retention Rate:**
```python
def calculate_retention_rate(days=7):
    # Get all player sessions
    sessions = query(PlayerSession).filter(
        join_time >= cutoff
    ).all()

    # Group by steam_id → days played
    player_days = defaultdict(set)
    for session in sessions:
        day = session.join_time.date()
        player_days[session.steam_id].add(day)

    # Count players who returned
    total = len(player_days)
    returning = sum(1 for days in player_days.values() if len(days) > 1)

    retention_rate = (returning / total) * 100
```

### Design Decisions

**Why pre-aggregate instead of real-time?**
- Fast query response (no complex calculations)
- Reduced database load
- Consistent results

**Why 24x7 heatmap format?**
- Industry standard (GitHub, Discord)
- Easy to visualize
- Shows patterns clearly

**CSV Export format:**
- Simple, universal
- Excel/Google Sheets compatible
- Easy to analyze externally

---

## 4. File Manager

### Security Architecture

**Path Validation (3 Layers):**
```python
def validate_path(server_id, requested_path):
    # Layer 1: Construct server root
    server_root = Path(SERVERS_BASE) / f"server_{server_id}"

    # Layer 2: Resolve full path
    full_path = (server_root / requested_path).resolve()

    # Layer 3: Verify within server root
    if not str(full_path).startswith(str(server_root.resolve())):
        raise HTTPException(403, "Path traversal blocked")

    return full_path
```

**Attack Prevention:**
```python
# Blocked attempts:
requested_path = "../../../etc/passwd"  → 403
requested_path = "/etc/passwd"          → 403
requested_path = "../../server_999/"    → 403

# Allowed:
requested_path = "cstrike/server.cfg"   → OK
requested_path = "./cstrike/../cstrike/server.cfg" → OK (resolves to cstrike/server.cfg)
```

**Backup Strategy:**
```python
def write_file(file_path, content):
    # Create timestamped backup
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    backup_path = file_path.with_suffix(f'{suffix}.backup.{timestamp}')

    if file_path.exists():
        shutil.copy2(file_path, backup_path)

    # Write new content
    file_path.write_text(content)
```

**Monaco Editor Integration:**
```javascript
// Language auto-detection
const getLanguage = (filename) => {
  const ext = filename.split('.').pop().toLowerCase();
  const map = {
    'cfg': 'ini',
    'sma': 'cpp',
    'json': 'json',
    'sh': 'shell'
  };
  return map[ext] || 'plaintext';
};

// Editor configuration
monaco.editor.create(container, {
  value: fileContent,
  language: getLanguage(filename),
  theme: 'vs-dark',
  automaticLayout: true,  // Responsive
  wordWrap: 'on',         // No horizontal scroll
  minimap: { enabled: true }
});
```

### Design Decisions

**Why Monaco Editor instead of CodeMirror?**
- Better TypeScript support
- VSCode-like UX (familiar to developers)
- Built-in IntelliSense
- Better syntax highlighting

**Why limit file size for editing?**
- Browser memory constraints
- Editor performance
- Large files should be edited locally

**Whitelist vs Blacklist for extensions:**
- Whitelist (current): Safer, explicit control
- Blacklist: Risky, easy to miss dangerous types
- Trade-off: Whitelist requires maintenance for new types

---

## 5. Plugin Manager

### AMXModX Plugin System

**File Structure:**
```
cstrike/addons/amxmodx/
├── configs/
│   └── plugins.ini         # Plugin registry
├── plugins/
│   ├── admincmd.amxx       # Compiled plugins
│   ├── myplugin.amxx
│   └── ...
└── scripting/
    ├── admincmd.sma        # Source files
    ├── myplugin.sma
    ├── include/            # Header files
    │   └── amxmodx.inc
    └── amxxpc              # Compiler binary
```

**plugins.ini Format:**
```ini
; Comment or disabled plugin
adminvote.amxx
adminchat.amxx
; myplugin.amxx
nextmap.amxx
```

**Enable/Disable Implementation:**
```python
def enable_plugin(filename):
    # Read plugins.ini
    lines = ini_path.read_text().splitlines()

    # Check if already enabled
    if filename in [l.strip() for l in lines if not l.startswith(';')]:
        return "Already enabled"

    # Add to end
    lines.append(filename)
    ini_path.write_text('\n'.join(lines) + '\n')

def disable_plugin(filename):
    # Comment out line
    new_lines = []
    for line in lines:
        if line.strip() == filename:
            new_lines.append(f"; {line}")
        else:
            new_lines.append(line)

    ini_path.write_text('\n'.join(new_lines) + '\n')
```

**Compilation Process:**
```python
def compile_plugin(sma_filename):
    # Locate compiler
    compiler = scripting_dir / "amxxpc"

    # Run compilation
    result = subprocess.run(
        [str(compiler), str(sma_file)],
        cwd=scripting_dir,
        capture_output=True,
        timeout=30  # Prevent hanging
    )

    # Check result
    if result.returncode != 0:
        error = result.stderr.decode('utf-8')
        return (False, f"Compilation failed: {error}")

    # Move to plugins directory
    amxx_file = scripting_dir / f"{sma_file.stem}.amxx"
    shutil.move(amxx_file, plugins_dir / amxx_file.name)

    return (True, f"Compiled: {amxx_file.name}")
```

**Metadata Extraction:**
```python
def _extract_plugin_info(plugin_file):
    # Read first 4KB of binary
    data = plugin_file.read(4096)
    text = data.decode('utf-8', errors='ignore')

    # Split by null bytes
    parts = text.split('\x00')

    # Heuristic search
    info = {}
    for part in parts:
        if 'version' in part.lower() and len(part) < 50:
            info['version'] = part.strip()
        if 'author' in part.lower() and len(part) < 50:
            info['author'] = part.strip()

    return info
```

### Design Decisions

**Why not use amxxpc REST API?**
- No official REST API exists
- Direct subprocess more reliable
- Simpler error handling

**Binary metadata extraction limitations:**
- .amxx format is proprietary
- No official parsing library
- Heuristic approach works for most plugins
- Fallback to "Unknown" acceptable

**Marketplace architecture:**
- Static list for MVP
- Future: Database-driven marketplace
- Future: Plugin ratings and reviews
- Future: Auto-update checking

---

## 🔒 Security Considerations

### Input Validation

**Path Traversal Prevention:**
```python
# All user-provided paths validated
full_path = validate_path(server_id, requested_path)

# Blocked patterns:
- ../
- ./../../
- Absolute paths (/etc/)
- Cross-server access (server_123 → server_456)
```

**File Upload Security:**
```python
# Extension whitelist
ALLOWED_EXTENSIONS = {
    '.cfg', '.ini', '.txt', '.sma', '.amxx',
    '.json', '.md', '.log'
}

# Size limits
MAX_EDIT_SIZE = 5 * 1024 * 1024   # 5MB
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
MAX_PLUGIN_SIZE = 10 * 1024 * 1024  # 10MB

# Filename sanitization
if '..' in filename or '/' in filename:
    raise HTTPException(400, "Invalid filename")
```

**RCON Command Safety:**
```python
# Timeout protection
subprocess.run(..., timeout=30)

# Validated task types (enum)
task_type in [RESTART, MAP_CHANGE, BACKUP, ...]

# Server ownership verification
verify_server_ownership(server_id, current_user)
```

### Backup Strategy

**When backups are created:**
1. Before editing any file
2. Before plugin delete
3. Before plugins.ini modification
4. Before config changes

**Backup format:**
```
{filename}.backup.{YYYYMMDD_HHMMSS}

Examples:
server.cfg.backup.20250125_140530
plugins.ini.backup.20250125_093015
myplugin.amxx.backup.20250124_153000
```

**Backup retention:**
- Auto-cleanup not implemented (future)
- Manual cleanup recommended
- Consider: Keep last 10 backups per file

### Authentication & Authorization

**JWT Token Verification:**
```python
@router.get("/servers/{server_id}/...")
async def endpoint(
    server_id: int,
    current_user: User = Depends(get_current_user_required)
):
    # Verify server ownership
    server = await verify_server_ownership(server_id, current_user, db)
    ...
```

**Server Ownership Check:**
```python
async def verify_server_ownership(server_id, user, db):
    server = db.query(GameServer).filter(
        GameServer.id == server_id
    ).first()

    if not server:
        raise HTTPException(404, "Server not found")

    if server.owner_id != user.id:
        raise HTTPException(403, "Not authorized")

    return server
```

---

## ⚡ Performance Optimizations

### Database Indexing

```sql
-- Scheduler
CREATE INDEX idx_server_enabled ON server_scheduled_tasks(server_id, is_enabled);
CREATE UNIQUE INDEX idx_apscheduler_job_id ON server_scheduled_tasks(apscheduler_job_id);

-- Stats
CREATE UNIQUE INDEX idx_server_date ON server_stats_daily(server_id, date);
CREATE INDEX idx_session_time ON player_sessions(server_id, join_time);
CREATE INDEX idx_steam_id ON player_sessions(steam_id);
```

### Query Optimization

**Bad (N+1 queries):**
```python
tasks = db.query(ServerScheduledTask).all()
for task in tasks:
    server = db.query(GameServer).filter(id=task.server_id).first()
```

**Good (JOIN):**
```python
tasks = db.query(ServerScheduledTask).options(
    joinedload(ServerScheduledTask.server)
).all()
```

### Caching Strategy

**Redis cache (future):**
```python
@cache(ttl=60)  # 1 minute
def get_hourly_stats(server_id, hours=24):
    # Expensive database query
    ...
```

**Browser cache:**
```http
Cache-Control: max-age=60  # Stats API
Cache-Control: no-cache    # File read API
```

### Frontend Optimization

**Code Splitting:**
```javascript
// Lazy load heavy components
const PluginManager = () => import('@/views/PluginManager.vue');
const MonacoEditor = () => import('@/components/filemanager/MonacoEditor.vue');
```

**Chart.js Decimation:**
```javascript
{
  plugins: {
    decimation: {
      enabled: true,
      algorithm: 'lttb',
      samples: 100
    }
  }
}
```

---

## 🧪 Testing Strategy

### Unit Tests

**Example:**
```python
# tests/test_file_manager.py
def test_path_traversal_blocked():
    service = FileManagerService()
    with pytest.raises(HTTPException) as exc:
        service.validate_path(123, "../../../etc/passwd")
    assert exc.value.status_code == 403

def test_valid_path():
    service = FileManagerService()
    path = service.validate_path(123, "cstrike/server.cfg")
    assert "server_123/cstrike/server.cfg" in str(path)
```

### Integration Tests

```python
# tests/test_scheduler_integration.py
async def test_create_and_execute_task():
    # Create task
    task = await scheduler_service.create_task({
        "task_type": "restart",
        "schedule_type": "cron",
        "cron_minute": "*/1"
    })

    # Wait for execution
    await asyncio.sleep(65)

    # Check execution log
    executions = db.query(ScheduledTaskExecution).filter(
        task_id=task.id
    ).all()
    assert len(executions) >= 1
    assert executions[0].status == "success"
```

### E2E Tests (Cypress)

```javascript
// cypress/e2e/plugin_manager.cy.js
describe('Plugin Manager', () => {
  it('should upload and enable plugin', () => {
    cy.visit('/servers/123/panel');
    cy.contains('Plugin Yöneticisi').click();

    // Upload
    cy.get('input[type=file]').attachFile('test_plugin.amxx');
    cy.contains('Plugin yüklendi').should('be.visible');

    // Enable
    cy.contains('test_plugin.amxx')
      .parent()
      .find('.n-switch')
      .click();

    cy.contains('Plugin aktif edildi').should('be.visible');
  });
});
```

---

## 📊 Monitoring & Logging

### Application Logs

```python
# Structured logging
logger.info(
    "User uploaded plugin",
    extra={
        "user_id": user.id,
        "server_id": server_id,
        "filename": filename,
        "size": file_size
    }
)
```

### Metrics (Prometheus - future)

```python
# Counter
plugin_uploads_total.inc()

# Histogram
task_execution_duration.observe(execution_time)

# Gauge
active_scheduled_tasks.set(count)
```

### Error Tracking (Sentry - future)

```python
sentry_sdk.init(
    dsn="...",
    traces_sample_rate=0.1
)

# Auto-capture exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    sentry_sdk.capture_exception(exc)
    ...
```

---

## 🔄 Deployment Process

### CI/CD Pipeline (GitLab CI - future)

```yaml
stages:
  - test
  - build
  - deploy

test:
  script:
    - pytest tests/
    - npm run test

build:
  script:
    - cd frontend && npm run build
    - docker build -t agtr-backend:latest .

deploy:
  script:
    - alembic upgrade head
    - systemctl restart agtr-backend
    - systemctl restart nginx
```

### Database Migration

```bash
# Generate migration
alembic revision --autogenerate -m "add_scheduler_tables"

# Review migration
cat alembic/versions/004_*.py

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Zero-Downtime Deployment

```bash
# 1. Deploy new code
git pull origin main

# 2. Run migrations
alembic upgrade head

# 3. Build frontend
cd frontend && npm run build

# 4. Reload backend (graceful)
kill -HUP $(cat /var/run/agtr-backend.pid)

# 5. Nginx (optional)
nginx -s reload
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue: Scheduler tasks not running**
```bash
# Check logs
tail -f /var/www/agtrmerkezi/logs/app.log | grep scheduler

# Verify scheduler started
grep "Server scheduler başlatıldı" logs/app.log

# Check database jobs
SELECT * FROM server_scheduled_tasks WHERE is_enabled = 1;

# Restart backend
kill -HUP $(pidof python)
```

**Issue: Monaco Editor not loading**
```bash
# Check frontend build
ls -lh /var/www/agtrmerkezi/static/dist/assets/ | grep monaco

# Check browser console
# Should show: monaco-editor loaded

# Rebuild if missing
cd frontend && npm install && npm run build
```

**Issue: File upload fails with 403**
```bash
# Check file permissions
ls -la /home/gameservers/servers/server_123/

# Fix permissions
chown -R www-data:www-data /home/gameservers/servers/server_123/

# Check path traversal logs
grep "Path traversal" /var/www/agtrmerkezi/logs/app.log
```

---

## 📚 References

### External Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue 3 Documentation](https://vuejs.org/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [Monaco Editor API](https://microsoft.github.io/monaco-editor/api/)
- [AMXModX Documentation](https://www.amxmodx.org/doc/)

### Internal Documentation

- API Reference: `/docs/API_REFERENCE.md`
- Features Guide: `/docs/FEATURES.md`
- Changelog: `/docs/CHANGELOG_v6.0.md`
- Database Schema: `/docs/DATABASE_SCHEMA.md`

---

## 🤝 Contributing

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Max line length: 120
- Docstrings for public functions

**JavaScript/Vue:**
- Follow Vue Style Guide
- Use Composition API
- Use `<script setup>`
- Prefer const over let

### Commit Messages

```
feat: add plugin marketplace endpoint
fix: resolve path traversal in file manager
docs: update API reference for scheduler
refactor: extract common validation logic
test: add unit tests for stats service
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type
- [ ] Feature
- [ ] Bug Fix
- [ ] Documentation
- [ ] Refactor

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Database migration included (if needed)
```

---

## 📝 TODO / Future Enhancements

### Short Term (v6.1)

- [ ] Marketplace plugin download
- [ ] WebSocket real-time stats updates
- [ ] Plugin dependency resolver
- [ ] File diff viewer
- [ ] Backup auto-cleanup

### Medium Term (v6.2)

- [ ] Scheduled task templates
- [ ] Advanced analytics (churn, forecasting)
- [ ] Multi-language support
- [ ] Mobile app (React Native)

### Long Term (v7.0)

- [ ] Kubernetes deployment
- [ ] Multi-region support
- [ ] Plugin CDN
- [ ] AI-powered server optimization
- [ ] Blockchain integration (?)

---

## 🎓 Lessons Learned

### What Went Well

1. **Modular Architecture**: Services are independent and testable
2. **Security First**: Path validation prevented vulnerabilities
3. **User Experience**: Monaco Editor provides professional feel
4. **Documentation**: Comprehensive docs reduce support burden

### What Could Be Improved

1. **Testing Coverage**: Need more unit/integration tests
2. **Performance**: Some queries could be optimized
3. **Error Handling**: More specific error messages needed
4. **Monitoring**: Add metrics and alerting

### Best Practices Established

1. **Always validate user input** (path, filename, size)
2. **Create backups before modifications**
3. **Log all user actions** (audit trail)
4. **Verify server ownership** on every endpoint
5. **Use enums for finite sets** (task types, status)
6. **Prefer whitelist over blacklist** (extensions, commands)

---

## 📞 Contact

- Technical Lead: [Name]
- Email: dev@agtrmerkezi.com
- Discord: AGTR Merkezi Server
- GitHub: github.com/agtrmerkezi

---

*Last Updated: 2025-01-25*
*Document Version: 1.0.0*
