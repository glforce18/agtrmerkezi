# Veritabanı Şeması

## Entity-Relationship Diyagramı

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER MANAGEMENT                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │      users       │         │   user_sessions  │                      │
│  ├──────────────────┤         ├──────────────────┤                      │
│  │ id (PK)          │◄────────│ user_id (FK)     │                      │
│  │ username         │         │ token            │                      │
│  │ email            │         │ ip_address       │                      │
│  │ password_hash    │         │ user_agent       │                      │
│  │ role (enum)      │         │ created_at       │                      │
│  │ level            │         │ expires_at       │                      │
│  │ xp               │         └──────────────────┘                      │
│  │ coins            │                                                    │
│  │ balance_tl       │         ┌──────────────────┐                      │
│  │ avatar           │◄────────│  user_profiles   │                      │
│  │ steam_id         │         ├──────────────────┤                      │
│  │ is_active        │         │ user_id (FK)     │                      │
│  │ created_at       │         │ bio              │                      │
│  └──────────────────┘         │ location         │                      │
│                               │ website          │                      │
│                               │ social_links     │                      │
│                               └──────────────────┘                      │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              FORUM SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │ forum_categories │         │   forum_topics   │                      │
│  ├──────────────────┤         ├──────────────────┤                      │
│  │ id (PK)          │◄────────│ category_id (FK) │                      │
│  │ name             │         │ id (PK)          │                      │
│  │ slug             │         │ title            │                      │
│  │ description      │         │ slug             │                      │
│  │ icon             │         │ content          │──────┐               │
│  │ color            │         │ author_id (FK) ──┼──────┼──► users      │
│  │ order            │         │ view_count       │      │               │
│  │ is_active        │         │ is_pinned        │      │               │
│  └──────────────────┘         │ is_locked        │      │               │
│                               │ created_at       │      │               │
│                               └──────────────────┘      │               │
│                                        │                │               │
│                                        │                │               │
│                                        ▼                │               │
│                               ┌──────────────────┐      │               │
│                               │  forum_replies   │      │               │
│                               ├──────────────────┤      │               │
│                               │ id (PK)          │      │               │
│                               │ topic_id (FK)    │      │               │
│                               │ author_id (FK) ──┼──────┘               │
│                               │ content          │                      │
│                               │ is_solution      │                      │
│                               │ created_at       │                      │
│                               └──────────────────┘                      │
│                                                                          │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │   forum_likes    │         │ forum_bookmarks  │                      │
│  ├──────────────────┤         ├──────────────────┤                      │
│  │ user_id (FK)     │         │ user_id (FK)     │                      │
│  │ topic_id (FK)    │         │ topic_id (FK)    │                      │
│  │ reply_id (FK)    │         │ created_at       │                      │
│  │ created_at       │         └──────────────────┘                      │
│  └──────────────────┘                                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                            GAME SYSTEM                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │  jackpot_rounds  │         │   jackpot_bets   │                      │
│  ├──────────────────┤         ├──────────────────┤                      │
│  │ id (PK)          │◄────────│ game_id (FK)     │                      │
│  │ round_number     │         │ id (PK)          │                      │
│  │ status (enum)    │         │ user_id (FK) ────┼──────► users         │
│  │ total_pot        │         │ amount           │                      │
│  │ server_seed      │         │ ticket_start     │                      │
│  │ server_seed_hash │         │ ticket_end       │                      │
│  │ client_seed      │         │ win_chance       │                      │
│  │ winner_id (FK)   │         │ created_at       │                      │
│  │ winner_ticket    │         └──────────────────┘                      │
│  │ house_cut        │                                                    │
│  │ created_at       │         ┌──────────────────┐                      │
│  │ finished_at      │         │ jackpot_history  │                      │
│  └──────────────────┘         ├──────────────────┤                      │
│                               │ user_id (FK)     │                      │
│                               │ total_wagered    │                      │
│                               │ total_won        │                      │
│                               │ total_lost       │                      │
│                               │ win_count        │                      │
│                               │ biggest_win      │                      │
│                               └──────────────────┘                      │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           WALLET SYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │   transactions   │         │     wallets      │                      │
│  ├──────────────────┤         ├──────────────────┤                      │
│  │ id (PK)          │         │ user_id (FK)     │                      │
│  │ user_id (FK)     │────────►│ wallet_type      │                      │
│  │ type (enum)      │         │ balance          │                      │
│  │ amount           │         │ is_active        │                      │
│  │ balance_before   │         └──────────────────┘                      │
│  │ balance_after    │                                                    │
│  │ description      │         WalletType Enum:                          │
│  │ reference_id     │         - COIN (Oyun parası)                      │
│  │ created_at       │         - TL (Gerçek para)                        │
│  └──────────────────┘         - BONUS                                   │
│                                                                          │
│  TransactionType Enum:                                                   │
│  - DEPOSIT, WITHDRAW, BET, WIN, TRANSFER, PURCHASE, REFUND              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           SERVER SYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │     servers      │         │  server_rentals  │                      │
│  ├──────────────────┤         ├──────────────────┤                      │
│  │ id (PK)          │◄────────│ server_id (FK)   │                      │
│  │ name             │         │ user_id (FK)     │                      │
│  │ ip               │         │ package_id (FK)  │                      │
│  │ port             │         │ start_date       │                      │
│  │ game_type        │         │ end_date         │                      │
│  │ map              │         │ status           │                      │
│  │ players          │         │ price_paid       │                      │
│  │ max_players      │         └──────────────────┘                      │
│  │ status           │                                                    │
│  │ owner_id (FK)    │         ┌──────────────────┐                      │
│  │ is_official      │         │ server_packages  │                      │
│  └──────────────────┘         ├──────────────────┤                      │
│                               │ id (PK)          │                      │
│                               │ name             │                      │
│                               │ slots            │                      │
│                               │ price_monthly    │                      │
│                               │ features         │                      │
│                               └──────────────────┘                      │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                            CLAN SYSTEM                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │      clans       │         │  clan_members    │                      │
│  ├──────────────────┤         ├──────────────────┤                      │
│  │ id (PK)          │◄────────│ clan_id (FK)     │                      │
│  │ name             │         │ user_id (FK) ────┼──────► users         │
│  │ tag              │         │ role (enum)      │                      │
│  │ description      │         │ joined_at        │                      │
│  │ logo             │         └──────────────────┘                      │
│  │ banner           │                                                    │
│  │ leader_id (FK)   │         ClanRole Enum:                            │
│  │ level            │         - LEADER                                  │
│  │ xp               │         - CO_LEADER                               │
│  │ created_at       │         - OFFICER                                 │
│  └──────────────────┘         - MEMBER                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Enum Tipleri

### UserRole
```python
class UserRole(str, Enum):
    USER = "user"
    VIP = "vip"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
```

### JackpotStatus
```python
class JackpotStatus(str, Enum):
    WAITING = "waiting"      # Bahis bekleniyor
    ACTIVE = "active"        # Aktif tur
    ROLLING = "rolling"      # Çark dönüyor
    COMPLETED = "completed"  # Tamamlandı
```

### TransactionType
```python
class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    BET = "bet"
    WIN = "win"
    TRANSFER = "transfer"
    PURCHASE = "purchase"
    REFUND = "refund"
```

### WalletType
```python
class WalletType(str, Enum):
    COIN = "coin"    # Oyun içi para
    TL = "tl"        # Türk Lirası
    BONUS = "bonus"  # Bonus bakiye
```

---

## İndeksler

```sql
-- Users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_steam_id ON users(steam_id);

-- Forum
CREATE INDEX idx_topics_category ON forum_topics(category_id);
CREATE INDEX idx_topics_author ON forum_topics(author_id);
CREATE INDEX idx_topics_created ON forum_topics(created_at DESC);
CREATE INDEX idx_replies_topic ON forum_replies(topic_id);

-- Transactions
CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_created ON transactions(created_at DESC);

-- Jackpot
CREATE INDEX idx_jackpot_bets_game ON jackpot_bets(game_id);
CREATE INDEX idx_jackpot_bets_user ON jackpot_bets(user_id);
```

---

## Veritabanı İstatistikleri

| Tablo | Kayıt Sayısı | Boyut |
|-------|-------------|-------|
| users | 5 | ~1KB |
| forum_categories | 17 | ~2KB |
| forum_topics | 12 | ~5KB |
| forum_replies | ~50 | ~10KB |
| transactions | ~100 | ~20KB |
