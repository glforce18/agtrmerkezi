# AGTR Merkezi

Counter-Strike 1.6 Game Server Management Panel with Vue.js SPA frontend and FastAPI backend.

## 🎮 Features

### Forum System
- ✅ Create topics and replies
- ✅ Like system for topics and replies
- ✅ Bookmark topics
- ✅ Best answer marking
- ✅ Nested replies (threaded discussions)
- ✅ Category-based organization
- ✅ Real-time statistics
- ✅ Trending topics
- ✅ XSS protection with DOMPurify
- ✅ Modern responsive UI

### Server Management
- Game server rental
- Server control panel
- Auto-update system
- Template management
- Resource monitoring

### User System
- Steam OpenID authentication
- Role-based access control
- User profiles with statistics
- Wallet system
- Activity tracking

## 🛠️ Tech Stack

**Frontend:**
- Vue.js 3 (Composition API)
- Vite
- Tailwind CSS
- DOMPurify (XSS protection)
- Pinia (state management)

**Backend:**
- Python 3.13
- FastAPI
- SQLAlchemy ORM
- MySQL
- Redis (caching)
- Uvicorn (ASGI server)

## 📊 Recent Updates (Latest Commit)

### Bug Fixes & Improvements (22 issues resolved)

**Critical Fixes:**
- Fixed NULL pointer errors in reply count operations
- Added NOT NULL database constraints

**High Priority:**
- Fixed author_id vs user_id inconsistency
- Improved best answer sorting
- Added authentication checks to interactive buttons
- Standardized field naming (reply_count)

**UX Improvements:**
- ESC key support for all modals
- Custom styled confirmation dialogs
- Safe pagination access
- Error notifications with toast system

**Security:**
- Integrated DOMPurify for XSS protection
- Enhanced HTML content sanitization

## 🚀 Installation

### Requirements
- Python 3.13+
- Node.js 18+
- MySQL 8.0+
- Redis 6.0+

### Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python -m app.models.database

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Development
npm run dev

# Production build
npm run build
```

## 📝 Database Schema

### Forum Tables
- `forum_categories` - Forum categories
- `forum_topics` - Discussion topics
- `forum_replies` - Topic replies (with threading support)
- `forum_topic_likes` - Topic likes
- `forum_reply_likes` - Reply likes
- `forum_bookmarks` - User bookmarks

### Constraints
- All count columns: NOT NULL DEFAULT 0
- Foreign keys with CASCADE delete
- Unique constraints on like/bookmark combinations

## 🔒 Security

- Steam OpenID authentication
- JWT token-based sessions
- Rate limiting (Redis-backed)
- XSS protection (DOMPurify)
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- Input validation (Pydantic)

## 📈 Performance

- Redis caching for frequently accessed data
- Database query optimization with indexes
- Lazy loading for relationships
- Frontend code splitting
- Asset compression (gzip)
- Pagination for large datasets

## 🤝 Contributing

This is a private project. Contact the maintainer for collaboration opportunities.

## 📄 License

Proprietary - All rights reserved

## 👥 Authors

- **glforce** - Project Lead & Development

## 🙏 Acknowledgments

- FastAPI framework
- Vue.js ecosystem
- Tailwind CSS
- DOMPurify security library

---

**Live Site:** https://agtrmerkezi.com
**Repository:** https://github.com/glforce18/agtrmerkezi
