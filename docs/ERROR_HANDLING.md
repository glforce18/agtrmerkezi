# Error Handling Documentation

## Overview
AGTR Merkezi custom exception hierarchy for consistent, structured error responses.

## Architecture

### Exception Hierarchy
```
AGTRException (base)
├── ForumException
│   ├── TopicNotFoundException
│   ├── CategoryNotFoundException
│   ├── ReplyNotFoundException
│   ├── TopicLockedException
│   ├── InsufficientPermissionsException
│   ├── RateLimitExceededException
│   ├── ContentValidationException
│   ├── SpamDetectedException
│   └── DuplicateContentException
├── PollException
│   ├── PollNotFoundException
│   ├── PollExpiredException
│   ├── PollAlreadyExistsException
│   ├── InvalidPollOptionsException
│   └── AlreadyVotedException
├── DraftException
│   ├── DraftNotFoundException
│   └── DraftSaveException
├── AuthenticationException
│   ├── SteamRequiredException
│   └── EmailVerificationRequiredException
├── DatabaseException
│   ├── DatabaseConnectionException
│   └── DatabaseQueryException
├── CacheException
│   └── CacheConnectionException
└── ValidationException
    └── InvalidInputException
```

## Exception Properties

Each exception has:
- **message**: User-friendly Turkish error message
- **error_code**: Unique error code (e.g., "TOPIC_NOT_FOUND")
- **status_code**: HTTP status code (400, 403, 404, 409, 429, 500)
- **details**: Optional dict with additional context

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "TOPIC_NOT_FOUND",
    "message": "Konu bulunamadi",
    "details": {
      "topic_id": 123
    }
  }
}
```

## Usage Examples

### In API Endpoints
```python
from app.core.exceptions import TopicNotFoundException, RateLimitExceededException

@router.get("/topics/{topic_id}")
async def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(ForumTopic).filter_by(id=topic_id).first()
    if not topic:
        raise TopicNotFoundException(topic_id=topic_id)

    return {"success": True, "topic": topic}

@router.post("/topics")
async def create_topic(user: User = Depends(get_current_user)):
    allowed, retry_after = await check_rate_limit(user.id, "topic_create")
    if not allowed:
        raise RateLimitExceededException(action="konu olusturma", retry_after=retry_after)

    # ... create topic
```

### In Services
```python
from app.core.exceptions import PollExpiredException, InvalidPollOptionsException

class PollService:
    def vote(self, poll_id: int, user_id: int):
        poll = self.db.query(Poll).get(poll_id)
        if not poll:
            raise PollNotFoundException(poll_id=poll_id)

        if poll.ends_at and poll.ends_at < datetime.utcnow():
            raise PollExpiredException()

        # ... process vote
```

## Middleware Integration

The exception handler middleware automatically catches all exceptions:

```python
# app/middleware/exception_handler.py
async def agtr_exception_handler(request: Request, call_next: Callable):
    try:
        response = await call_next(request)
        return response
    except AGTRException as e:
        # Custom exceptions - already formatted
        return JSONResponse(status_code=e.status_code, content=e.to_dict())
    except IntegrityError as e:
        # Database constraint violations
        return JSONResponse(status_code=409, content={...})
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={...})
```

## Error Codes Reference

### Forum Errors (400-404)
| Code | HTTP | Description |
|------|------|-------------|
| TOPIC_NOT_FOUND | 404 | Topic doesn't exist |
| CATEGORY_NOT_FOUND | 404 | Category doesn't exist |
| REPLY_NOT_FOUND | 404 | Reply doesn't exist |
| TOPIC_LOCKED | 403 | Topic is locked, can't reply |
| INSUFFICIENT_PERMISSIONS | 403 | User lacks permission |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| CONTENT_VALIDATION_ERROR | 400 | Invalid content |
| SPAM_DETECTED | 403 | Content flagged as spam |
| DUPLICATE_CONTENT | 409 | Content already exists |

### Poll Errors (400-410)
| Code | HTTP | Description |
|------|------|-------------|
| POLL_NOT_FOUND | 404 | Poll doesn't exist |
| POLL_EXPIRED | 410 | Poll voting period ended |
| POLL_ALREADY_EXISTS | 409 | Topic already has a poll |
| INVALID_POLL_OPTIONS | 400 | Invalid poll configuration |
| ALREADY_VOTED | 409 | User already voted |

### Authentication Errors (401-403)
| Code | HTTP | Description |
|------|------|-------------|
| STEAM_REQUIRED | 403 | Steam account needed |
| EMAIL_VERIFICATION_REQUIRED | 403 | Email verification needed |

### System Errors (500-503)
| Code | HTTP | Description |
|------|------|-------------|
| DATABASE_ERROR | 500 | Database query failed |
| DATABASE_UNAVAILABLE | 503 | Can't connect to database |
| CACHE_ERROR | 500 | Cache operation failed |
| INTERNAL_SERVER_ERROR | 500 | Unexpected error |

## Best Practices

### 1. Use Specific Exceptions
```python
# ❌ Bad
raise HTTPException(status_code=404, detail="Not found")

# ✅ Good
raise TopicNotFoundException(topic_id=topic_id)
```

### 2. Include Context in Details
```python
# ❌ Bad
raise RateLimitExceededException("rate limit", None)

# ✅ Good
raise RateLimitExceededException(action="konu olusturma", retry_after=3600)
```

### 3. Log Before Raising
```python
# ✅ Good
logger.warning(f"User {user_id} exceeded rate limit for topic creation")
raise RateLimitExceededException(action="konu olusturma", retry_after=retry_after)
```

### 4. Don't Catch AGTRException in Endpoints
```python
# ❌ Bad - middleware handles it
try:
    topic = get_topic(id)
except TopicNotFoundException as e:
    return {"error": str(e)}

# ✅ Good - let middleware catch it
topic = get_topic(id)  # Raises TopicNotFoundException if not found
return {"topic": topic}
```

### 5. Use HTTPException Only for FastAPI-Specific Errors
```python
# ✅ Good - OAuth callback handling
if not code:
    raise HTTPException(status_code=400, detail="Missing code parameter")
```

## Migration Guide

### Before (HTTPException)
```python
if not topic:
    raise HTTPException(status_code=404, detail="Konu bulunamadi")
```

### After (Custom Exception)
```python
if not topic:
    raise TopicNotFoundException(topic_id=topic_id)
```

### Benefits
- Consistent error structure
- Better error tracking and logging
- Client-friendly error codes
- Type-safe exception handling
- Automatic HTTP status code mapping

## Testing

```python
import pytest
from app.core.exceptions import TopicNotFoundException

def test_topic_not_found_exception():
    exc = TopicNotFoundException(topic_id=123)

    assert exc.status_code == 404
    assert exc.error_code == "TOPIC_NOT_FOUND"
    assert exc.message == "Konu bulunamadi"
    assert exc.details == {"topic_id": 123}

    response_dict = exc.to_dict()
    assert response_dict["success"] == False
    assert response_dict["error"]["code"] == "TOPIC_NOT_FOUND"
```

## Performance Impact

- **Minimal overhead**: Exception creation is fast (<1ms)
- **No database queries**: All exceptions are in-memory
- **Logging overhead**: Only when exceptions are raised (rare)

## Future Enhancements

1. **I18n Support**: Multi-language error messages
2. **Error Tracking**: Integration with Sentry/Rollbar
3. **Error Analytics**: Dashboard for error trends
4. **Recovery Suggestions**: Include fix hints in responses
