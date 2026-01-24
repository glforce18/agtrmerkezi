# Caching System Documentation

## Overview
Redis-based caching layer for AGTR Merkezi with decorators, helpers, and specialized functions.

## Architecture

### Core Components
```
app/core/cache.py
├── Cache Decorator (@cache)
├── Cache Helpers (get/set/delete)
├── Invalidation Functions
├── Specialized Cache Functions
└── Cache Statistics
```

## Cache Decorator Usage

### Basic Usage
```python
from app.core.cache import cache

@cache(ttl=300)  # Cache for 5 minutes
async def get_user(user_id: int):
    return db.query(User).get(user_id)
```

### Custom Key Prefix
```python
@cache(ttl=60, key_prefix="forum:topic")
async def get_topic(topic_id: int):
    return db.query(Topic).get(topic_id)
```

### Custom Key Builder
```python
def topic_cache_key(topic_id: int, include_replies: bool = False):
    return f"forum:topic:{topic_id}:replies={include_replies}"

@cache(ttl=300, key_builder=topic_cache_key)
async def get_topic_with_replies(topic_id: int, include_replies: bool = False):
    # ...
```

## Helper Functions

### Get/Set/Delete
```python
from app.core.cache import get_cached, set_cached, delete_cached

# Get from cache
user = await get_cached("user:123", default=None)

# Set in cache
await set_cached("user:123", user_data, ttl=300)

# Delete from cache
await delete_cached("user:123")
```

### Bulk Operations
```python
from app.core.cache import cache_multiple, get_multiple

# Cache multiple items
items = {
    "user:1": {"name": "Alice"},
    "user:2": {"name": "Bob"},
}
cached_count = await cache_multiple(items, ttl=300)

# Get multiple items
keys = ["user:1", "user:2", "user:3"]
results = await get_multiple(keys)  # {key: value}
```

## Specialized Cache Functions

### Leaderboard
```python
from app.core.cache import cache_leaderboard, get_cached_leaderboard

# Cache leaderboard
await cache_leaderboard("weekly", limit=10, data=leaderboard_data, ttl=300)

# Get cached leaderboard
leaderboard = await get_cached_leaderboard("weekly", limit=10)
```

### Popular Topics
```python
from app.core.cache import cache_popular_topics, get_cached_popular_topics

# Cache popular topics
await cache_popular_topics(category_id=1, limit=20, data=topics, ttl=60)

# Get cached popular topics
topics = await get_cached_popular_topics(category_id=1, limit=20)
```

### Trending Topics
```python
from app.core.cache import cache_trending_topics, get_cached_trending_topics

# Cache trending topics
await cache_trending_topics(hours=24, limit=10, data=topics, ttl=300)

# Get cached trending topics
topics = await get_cached_trending_topics(hours=24, limit=10)
```

### Category Stats
```python
from app.core.cache import cache_category_stats, get_cached_category_stats

# Cache category stats
await cache_category_stats(category_id=1, data=stats, ttl=300)

# Get cached stats
stats = await get_cached_category_stats(category_id=1)
```

## Cache Invalidation

### Pattern-Based Invalidation
```python
from app.core.cache import invalidate_cache

# Delete all topic caches
await invalidate_cache("forum:topic:*")

# Delete all caches for category 1
await invalidate_cache("forum:category:1:*")
```

### Specific Key Invalidation
```python
# Delete specific topic cache
await invalidate_cache("forum:topic", topic_id=123)

# With multiple params
await invalidate_cache("forum:topic", topic_id=123, include_replies=True)
```

### Forum-Wide Invalidation
```python
from app.core.cache import invalidate_forum_cache

# Invalidate all forum caches
deleted_count = await invalidate_forum_cache()

# Invalidate only category 1 caches
deleted_count = await invalidate_forum_cache(category_id=1)
```

## Cache Keys Structure

### Naming Convention
```
{namespace}:{resource}:{identifier}:{params}
```

### Examples
```
forum:topic:123                      # Topic 123
forum:topic:123:replies=true         # Topic 123 with replies
forum:category:1:stats               # Category 1 stats
forum:leaderboard:weekly:10          # Weekly top 10
forum:popular:all:20                 # Popular 20 topics (all categories)
forum:trending:24:10                 # Trending topics (24h, top 10)
user:session:abc123                  # User session
server:status:456                    # Server 456 status
```

## Cache Statistics

```python
from app.core.cache import get_cache_stats

stats = await get_cache_stats()
# {
#     "total_keys": 1234,
#     "memory_used": "15.2M",
#     "hit_rate": "95.3%",
#     "connected_clients": 5,
#     "keys_by_namespace": {
#         "forum": 800,
#         "user": 300,
#         "server": 134
#     }
# }
```

## TTL Guidelines

| Data Type | TTL | Reason |
|-----------|-----|--------|
| Leaderboard (all/weekly) | 5 min (300s) | Updates infrequently |
| Leaderboard (monthly) | 1 min (60s) | More dynamic |
| Popular Topics | 1 min (60s) | Needs to be fresh |
| Trending Topics | 5 min (300s) | Algorithm-based, stable |
| Category Stats | 5 min (300s) | Infrequent changes |
| User Session | 30 min (1800s) | Auth tokens |
| API Rate Limits | 1 hour (3600s) | Counter resets |

## Best Practices

### 1. Always Use Try-Catch for Cache Operations
```python
# ✅ Good
try:
    cached = await redis_manager.get(key)
    if cached:
        return json.loads(cached)
except Exception as e:
    logger.warning(f"Cache error: {e}")
    # Continue without cache

# ❌ Bad - Will crash app if Redis is down
cached = await redis_manager.get(key)
return json.loads(cached)
```

### 2. Set Appropriate TTL
```python
# ✅ Good - Based on data update frequency
@cache(ttl=60)  # 1 minute for dynamic data
async def get_online_users():
    ...

@cache(ttl=3600)  # 1 hour for static data
async def get_game_assets():
    ...

# ❌ Bad - Too long for dynamic data
@cache(ttl=86400)  # 24 hours for online users!
```

### 3. Invalidate Cache on Updates
```python
# ✅ Good
async def create_topic(topic_data):
    topic = db.add(Topic(**topic_data))
    db.commit()

    # Invalidate related caches
    await invalidate_forum_cache(category_id=topic.category_id)

# ❌ Bad - Stale cache
async def create_topic(topic_data):
    topic = db.add(Topic(**topic_data))
    db.commit()
    # Cache not invalidated!
```

### 4. Use Specialized Functions
```python
# ✅ Good - Type-safe, consistent keys
from app.core.cache import cache_leaderboard
await cache_leaderboard("weekly", 10, data, ttl=300)

# ❌ Bad - Manual key construction prone to errors
await set_cached(f"forum:leaderboard:weekly:10", data, ttl=300)
```

### 5. Monitor Cache Performance
```python
# Add cache hit/miss tracking
@cache(ttl=300)
async def expensive_query():
    logger.info("Cache miss - executing expensive query")
    return db.query(...).all()
```

## Integration Examples

### API Endpoint with Cache
```python
from app.core.cache import get_cached_leaderboard, cache_leaderboard

@router.get("/leaderboard")
async def get_leaderboard(timeframe: str, limit: int = 10):
    # Try cache first
    cached = await get_cached_leaderboard(timeframe, limit)
    if cached:
        return {"leaderboard": cached, "cached": True}

    # Cache miss - query database
    data = db.query(...).all()

    # Cache result
    await cache_leaderboard(timeframe, limit, data, ttl=300)

    return {"leaderboard": data, "cached": False}
```

### Service with Auto-Invalidation
```python
class ForumService:
    async def create_topic(self, topic_data):
        topic = Topic(**topic_data)
        db.add(topic)
        db.commit()

        # Invalidate caches
        await invalidate_forum_cache(category_id=topic.category_id)

        return topic
```

## Performance Impact

### Before Caching
```
GET /api/leaderboard
- Query: 250ms
- Total: 250ms
```

### After Caching
```
GET /api/leaderboard (cache hit)
- Cache: 2ms
- Total: 2ms (125x faster!)

GET /api/leaderboard (cache miss)
- Query: 250ms
- Cache write: 1ms
- Total: 251ms
```

## Troubleshooting

### Cache Not Working
1. Check Redis connection: `redis-cli ping`
2. Check logs for cache errors
3. Verify TTL is set (not 0 or negative)
4. Ensure key format is consistent

### Stale Data
1. Check TTL is appropriate
2. Verify cache invalidation is called
3. Use pattern matching to find related keys: `KEYS forum:topic:*`

### Memory Issues
1. Monitor cache stats: `await get_cache_stats()`
2. Reduce TTL for large objects
3. Implement LRU eviction policy
4. Use cache key expiration

## Configuration

### Redis Settings
```python
# app/core/config.py
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
REDIS_MAX_CONNECTIONS = 50
```

### Cache TTL Defaults
```python
# app/core/cache.py
DEFAULT_TTL = 300  # 5 minutes
LEADERBOARD_TTL = 300  # 5 minutes
POPULAR_TTL = 60  # 1 minute
TRENDING_TTL = 300  # 5 minutes
CATEGORY_TTL = 300  # 5 minutes
```

## Future Enhancements

1. **Cache Warmup**: Pre-populate cache on startup
2. **Cache Tagging**: Group related cache keys
3. **Cache Compression**: Compress large objects
4. **Multi-Level Cache**: Memory + Redis
5. **Cache Metrics**: Prometheus/Grafana integration
