# RCON Rate Limiting - Deployment Guide

**Version:** 6.1
**Date:** 2026-01-25
**Purpose:** Prevent abuse of RCON restart, kick, ban commands

---

## Overview

Per-user, per-endpoint rate limiting for RCON operations using Redis (with in-memory fallback).

### Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `rcon_restart` | 10 requests | 1 hour |
| `rcon_kick` | 60 requests | 1 hour |
| `rcon_ban` | 30 requests | 1 hour |
| `rcon_command` | 100 requests | 1 hour |
| `rcon_status` | 300 requests | 1 hour |

---

## Architecture

### Components

1. **`app/services/rcon_rate_limiter.py`** - Core rate limiting logic
2. **`app/api/rcon_limits.py`** - API endpoints for checking usage
3. **Redis** - Distributed counter storage (fallback to memory if unavailable)

### How It Works

1. User makes RCON request → JWT token extracted → `user_id` retrieved
2. Request path classified → Endpoint category determined
3. Redis counter checked → If limit exceeded → HTTP 429 returned
4. If under limit → Counter incremented → Request proceeds

---

## Deployment Steps

### 1. Install Redis (if not already installed)

```bash
sudo apt update
sudo apt install redis-server

# Enable and start
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verify
redis-cli ping
# Expected: PONG
```

### 2. Deploy Code

```bash
cd /var/www/agtrmerkezi

# Pull changes
git pull origin main

# Install dependencies (if any new)
pip install redis

# Restart application
sudo systemctl restart agtrmerkezi
```

### 3. Verify Redis Connection

```bash
# Check logs
tail -f /var/log/agtrmerkezi/api.log | grep "RCON Rate Limiter"

# Expected:
# RCON Rate Limiter using Redis backend
```

### 4. Add Rate Limiting to RCON Endpoints

**Example: Adding to restart endpoint**

```python
# app/api/servers.py or wherever RCON endpoints are defined

from fastapi import Depends
from app.services.rcon_rate_limiter import check_rcon_rate_limit

@router.post(
    "/servers/{server_id}/rcon/restart",
    dependencies=[Depends(check_rcon_rate_limit)]  # Add this line
)
async def restart_server(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Restart server via RCON"""
    # ... existing code
```

**Example: Multiple dependencies**

```python
@router.post(
    "/servers/{server_id}/rcon/kick",
    dependencies=[
        Depends(check_rcon_rate_limit),  # Rate limiting
        Depends(require_admin_or_owner)   # Existing authorization
    ]
)
async def kick_player(...):
    # ... existing code
```

---

## Testing

### Manual Testing

**1. Test restart rate limit (10/hour)**

```bash
# Get JWT token
TOKEN="your_jwt_token_here"

# Make 11 requests
for i in {1..11}; do
  echo "Request $i"
  curl -X POST \
    http://localhost:8000/api/servers/1/rcon/restart \
    -H "Authorization: Bearer $TOKEN"
  sleep 1
done

# Expected:
# Requests 1-10: 200 OK
# Request 11: 429 Too Many Requests
```

**2. Check usage statistics**

```bash
curl http://localhost:8000/api/rcon/limits \
  -H "Authorization: Bearer $TOKEN" | jq

# Expected output:
{
  "user_id": 123,
  "limits": [
    {
      "endpoint": "rcon_restart",
      "limit": 10,
      "current": 10,
      "remaining": 0,
      "window": 3600,
      "reset_in": 3540
    },
    ...
  ]
}
```

### Unit Tests

```bash
cd /var/www/agtrmerkezi

# Run RCON rate limiter tests
pytest tests/test_rcon_rate_limiter.py -v

# Expected:
# test_classify_restart_endpoint PASSED
# test_exceed_limit_raises_exception PASSED
# test_different_users_independent_limits PASSED
# ... (all tests passing)
```

---

## API Documentation

### GET `/api/rcon/limits`

Get all RCON rate limit usage for current user.

**Authentication:** Required (JWT)

**Response:**

```json
{
  "user_id": 123,
  "limits": [
    {
      "endpoint": "rcon_restart",
      "limit": 10,
      "current": 3,
      "remaining": 7,
      "window": 3600,
      "reset_in": 2400
    },
    {
      "endpoint": "rcon_kick",
      "limit": 60,
      "current": 15,
      "remaining": 45,
      "window": 3600,
      "reset_in": 2400
    }
  ]
}
```

### GET `/api/rcon/limits/{endpoint}`

Get rate limit usage for specific endpoint.

**Authentication:** Required (JWT)

**Parameters:**
- `endpoint`: One of `rcon_restart`, `rcon_kick`, `rcon_ban`, `rcon_command`, `rcon_status`

**Response:**

```json
{
  "endpoint": "rcon_restart",
  "limit": 10,
  "current": 3,
  "remaining": 7,
  "window": 3600,
  "reset_in": 2400
}
```

### GET `/api/rcon/limits/info/all`

Get rate limit configuration (no auth required).

**Response:**

```json
{
  "rcon_restart": {
    "limit": 10,
    "window": 3600
  },
  "rcon_kick": {
    "limit": 60,
    "window": 3600
  },
  ...
}
```

---

## Frontend Integration

### Display Rate Limit Info

```javascript
// Fetch user's current limits
async function checkRateLimits() {
  const response = await fetch('/api/rcon/limits', {
    headers: {
      'Authorization': `Bearer ${getJwtToken()}`
    }
  });

  const data = await response.json();

  // Display to user
  data.limits.forEach(limit => {
    console.log(`${limit.endpoint}: ${limit.remaining}/${limit.limit} remaining`);
  });
}
```

### Handle 429 Errors

```javascript
async function restartServer(serverId) {
  try {
    const response = await fetch(`/api/servers/${serverId}/rcon/restart`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getJwtToken()}`
      }
    });

    if (response.status === 429) {
      const error = await response.json();
      alert(`Rate limit exceeded: ${error.detail}`);

      // Show retry time
      const retryAfter = response.headers.get('Retry-After');
      alert(`Try again in ${retryAfter} seconds`);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
}
```

---

## Monitoring

### Redis Metrics

```bash
# Monitor Redis keys
redis-cli --scan --pattern "rcon_limit:*" | wc -l

# Check specific user
redis-cli GET "rcon_limit:123:rcon_restart"
# Output: "5" (5 requests used)

# Check TTL
redis-cli TTL "rcon_limit:123:rcon_restart"
# Output: 2400 (40 minutes remaining)
```

### Application Logs

```bash
# Watch for rate limit events
tail -f /var/log/agtrmerkezi/api.log | grep "Rate limit"

# Expected logs:
# Rate limit exceeded: rcon_limit:123:rcon_restart (10/10)
```

---

## Troubleshooting

### Issue: Redis connection failed

**Symptom:** Logs show "RCON Rate Limiter: Redis unavailable"

**Fix:**

```bash
# Check Redis status
sudo systemctl status redis-server

# Restart if needed
sudo systemctl restart redis-server

# Check connectivity
redis-cli ping
```

**Note:** System will automatically fallback to in-memory counters if Redis is unavailable.

### Issue: Rate limits not enforced

**Cause:** Endpoint not using `check_rcon_rate_limit` dependency

**Fix:** Add dependency to endpoint:

```python
@router.post(
    "/servers/{id}/rcon/restart",
    dependencies=[Depends(check_rcon_rate_limit)]  # Add this
)
```

### Issue: User getting 429 too quickly

**Cause:** Multiple devices/tabs using same account

**Solution:** Explain to user that limits are per-account, not per-device.

**Workaround:** Increase limit in `rcon_rate_limiter.py`:

```python
ENDPOINT_LIMITS = {
    "rcon_restart": {"limit": 20, "window": 3600},  # Increased from 10 to 20
}
```

---

## Security Considerations

1. **JWT Required:** Rate limiting only works for authenticated users
2. **Per-User Limits:** Users cannot bypass by using multiple IPs
3. **Endpoint-Specific:** Different operations have different limits
4. **Redis TTL:** Counters auto-expire after window (no manual cleanup needed)
5. **Memory Fallback:** System remains functional even if Redis fails

---

## Future Enhancements

### Phase 2 (Week 2-3)

- **Daily Command Quotas:** Total commands per day across all endpoints
- **Burst Protection:** Sub-second rate limiting for rapid spam
- **Admin Override:** Allow admins to bypass limits
- **User Notifications:** Email/Discord alerts when limit reached

### Phase 3 (Month 1+)

- **Dynamic Limits:** Adjust based on server plan (VIP users get higher limits)
- **Grafana Dashboard:** Real-time rate limit metrics
- **Auto-ban:** Temporarily ban users who repeatedly hit limits

---

## Endpoints to Update

Apply `check_rcon_rate_limit` dependency to these endpoints:

- [ ] `/api/servers/{id}/rcon/restart`
- [ ] `/api/servers/{id}/rcon/kick`
- [ ] `/api/servers/{id}/rcon/ban`
- [ ] `/api/servers/{id}/rcon/command`
- [ ] `/api/servers/{id}/rcon/status`
- [ ] `/api/servers/{id}/action` (if exists)
- [ ] Any other RCON-related endpoints

---

## Support

If you encounter issues:

1. Check logs: `/var/log/agtrmerkezi/api.log`
2. Verify Redis: `redis-cli ping`
3. Test endpoint: `curl /api/rcon/limits`
4. Review this guide
5. Contact development team

---

**Last Updated:** 2026-01-25
**Maintainer:** AGTR Merkezi Development Team
