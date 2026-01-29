# ✅ Admin Approval System - DEPLOYED

**Tarih:** 2026-01-29 22:09
**Durum:** Backend hazır, frontend UI bekleniyor

---

## Yapılanlar

### 1. Database Enum Güncellemesi ✅

ServerStatus enum'a 3 yeni durum eklendi:

```python
class ServerStatus(enum.Enum):
    PENDING = "pending"        # Beklemede
    CREATING = "creating"      # Oluşturuluyor
    INSTALLING = "installing"  # 🆕 Kurulum yapılıyor
    RUNNING = "running"        # Çalışıyor
    STOPPED = "stopped"        # Durduruldu
    SUSPENDED = "suspended"    # Askıya alındı
    EXPIRED = "expired"        # Süresi doldu
    DELETED = "deleted"        # Silindi
    CANCELLED = "cancelled"    # İptal edildi
    REJECTED = "rejected"      # 🆕 Admin tarafından reddedildi
    ERROR = "error"            # 🆕 Kurulum hatası
```

**Dosya:** `/var/www/agtrmerkezi/app/models/database.py`

---

### 2. Admin Approval API ✅

Yeni endpoint'ler oluşturuldu:

#### GET `/api/admin/server-approval/pending-servers`
Onay bekleyen sunucuları listeler.

**Response:**
```json
{
  "servers": [
    {
      "id": 1,
      "name": "Test Server",
      "owner_id": 6,
      "game_type": "cs16",
      "ip": "192.168.1.1",
      "port": 27015,
      "slots": 32,
      "monthly_price": 460.0,
      "created_at": "2026-01-29T19:00:00",
      "package_id": 3
    }
  ],
  "total": 1
}
```

#### POST `/api/admin/server-approval/approve`
Sunucuyu onayla veya reddet.

**Request:**
```json
{
  "server_id": 1,
  "approved": true,
  "reason": "Optional rejection reason"
}
```

**Onay Akışı (approved: true):**
1. Server status → INSTALLING
2. ServerInstallationService başlatılır
3. Installation kaydı oluşturulur
4. Background task ile kurulum çalıştırılır
5. Python installation script'leri otomatik çalışır
6. Başarılı ise status → RUNNING
7. Hata varsa status → ERROR

**Red Akışı (approved: false):**
1. Server status → REJECTED
2. Kullanıcıya bildirim gönderilir (TODO)
3. Para iadesi yapılır (TODO)

**Response (Success):**
```json
{
  "success": true,
  "message": "Sunucu onaylandı ve kurulum başlatıldı",
  "server_id": 1,
  "installation_id": 42,
  "status": "installing"
}
```

**Dosya:** `/var/www/agtrmerkezi/app/api/admin/server_approval.py`

---

### 3. Backend Restart ✅

```bash
systemctl restart agtrmerkezi
systemctl status agtrmerkezi
# ✅ Tüm kontroller başarılı
# 🚀 Sistem hazır!
```

---

## Mevcut Durum

### Database'de Bekleyen Server

```
ID: 1
Name: Test Server
Game Type: cs16  ⚠️ (Kullanıcı Half-Life seçmişti)
Owner: User #6
Status: PENDING (onay bekliyor)
```

**Sorun:** Kullanıcı Half-Life seçmiş ama CS 1.6 olarak kaydedilmiş.
**Neden:** Package selection → server creation mapping hatası (araştırılmalı)

---

## Yapılması Gerekenler

### 1. Admin Frontend Panel (ÖNCELİKLİ)

Admin için onay paneli oluşturulmalı:

**Konum:** `/var/www/agtrmerkezi/frontend/src/views/admin/ServerApproval.vue`

**Özellikler:**
- [ ] Pending sunucuları listele (tablo)
- [ ] Her satırda:
  - Server adı, game type, owner username
  - IP, port, slots
  - Oluşturma tarihi
  - Onay/Reddet butonları
- [ ] Onay butonu:
  - Confirm dialog göster
  - POST `/api/admin/server-approval/approve` çağır
  - Success toast göster
  - Listeyi yenile
- [ ] Reddet butonu:
  - Reason input modal aç
  - POST `/api/admin/server-approval/approve` (approved: false)
  - Success toast göster
  - Listeyi yenile

**API Client:**
```javascript
// frontend/src/api/admin.js
export const adminAPI = {
  async getPendingServers() {
    return api.get('/api/admin/server-approval/pending-servers')
  },

  async approveServer(serverId, approved, reason = null) {
    return api.post('/api/admin/server-approval/approve', {
      server_id: serverId,
      approved,
      reason
    })
  }
}
```

---

### 2. Game Type Mapping Hatası (ÖNCELİKLİ)

**Sorun:** User package ID 3 seçti → Half-Life AG olmalı ama CS16 oldu

**Kontrol Edilmeli:**
- [ ] `/api/servers/order/package-wallet` endpoint
- [ ] Package ID → game_type mapping
- [ ] Frontend button'ları doğru package_id gönderiyor mu?

**Olası Çözüm:**
```python
# servers.py order endpoint
package = db.query(ServerPackage).filter(
    ServerPackage.id == data.package_id,
    ServerPackage.is_active == True
).first()

if not package:
    raise HTTPException(404, "Paket bulunamadı")

# Doğru game_type'ı package'dan al
server = GameServer(
    owner_id=current_user.id,
    name=data.server_name,
    game_type=package.game_type,  # ✓ Package'dan al
    # ...
)
```

---

### 3. User Panel İyileştirmeleri

**Konum:** `/var/www/agtrmerkezi/frontend/src/views/user/MyServers.vue`

**Değişiklikler:**
- [ ] Server card'larda status badge göster:
  - PENDING → 🟡 "Onay Bekleniyor"
  - INSTALLING → 🔵 "Kuruluyor..." (progress bar)
  - RUNNING → 🟢 "Çalışıyor"
  - ERROR → 🔴 "Kurulum Başarısız"
  - REJECTED → ⚫ "Reddedildi"

- [ ] PENDING/INSTALLING durumunda:
  - RCON controls devre dışı
  - "Kurulum tamamlandığında erişebilirsiniz" mesajı

- [ ] RUNNING durumunda:
  - Normal panel kontrollerini göster

---

### 4. WebSocket Installation Progress (İSTEĞE BAĞLI)

Real-time kurulum ilerlemesi göstermek için:

**Backend:**
```python
# server_approval.py - run_installation_background fonksiyonu
async def run_installation_background(...):
    # Her adımda WebSocket emit
    await websocket_manager.emit_to_user(
        server.owner_id,
        "installation_progress",
        {"server_id": server.id, "progress": 25, "message": "SteamCMD indiriliyor..."}
    )
```

**Frontend:**
```javascript
// WebSocket listener
socket.on('installation_progress', (data) => {
  // Progress bar güncelle
  installationProgress.value = data.progress
  installationMessage.value = data.message
})
```

---

### 5. Para İadesi Sistemi (TODO)

Red edilen sunucular için otomatik refund:

```python
# server_approval.py - approve_server endpoint
if not data.approved:
    server.status = ServerStatus.REJECTED

    # Para iadesini yap
    refund_amount = server.monthly_price
    wallet_service.add_balance(
        user_id=server.owner_id,
        amount=refund_amount,
        currency='TL',
        description=f"Sunucu reddedildi: {server.name}"
    )

    # Transaction kaydı oluştur
    transaction = Transaction(
        user_id=server.owner_id,
        type='refund',
        amount=refund_amount,
        description=f"Server #{server.id} rejection refund"
    )
    db.add(transaction)
    db.commit()
```

---

## Test Senaryosu

### Senaryo 1: Başarılı Onay
1. Admin panele gir
2. Pending server listesini gör
3. "Onayla" butonuna bas
4. Confirm dialog'da "Evet" de
5. Backend:
   - Status → INSTALLING
   - Installation başlatılır
   - Python script'ler çalışır
   - Status → RUNNING
6. User panelinde server RUNNING olarak görünür
7. User RCON ile kontrol edebilir

### Senaryo 2: Red
1. Admin "Reddet" butonuna bas
2. Reason input aç: "Geçersiz sunucu adı"
3. Backend:
   - Status → REJECTED
   - Para iadesi yapılır
4. User bildirim alır
5. Bakiyesi artar

---

## Sonraki Adımlar

### Bugün Yapılacak:
1. ✅ Admin approval API (TAMAMLANDI)
2. ⏳ Admin frontend panel oluştur
3. ⏳ Game type mapping hatasını düzelt
4. ⏳ Test server'ı onayla ve kurulumu test et

### Yarın Yapılacak:
1. User panel status badge'leri
2. WebSocket installation progress
3. Para iadesi sistemi
4. Email notifications (onay/red)

---

## API Endpoints Özet

| Method | Endpoint | Auth | Açıklama |
|--------|----------|------|----------|
| GET | `/api/admin/server-approval/pending-servers` | Admin | Bekleyen sunucuları listele |
| POST | `/api/admin/server-approval/approve` | Admin | Sunucuyu onayla/reddet |

---

## Log Dosyaları

Backend logları:
```bash
# Genel backend logs
journalctl -u agtrmerkezi -f

# Scheduler logs
tail -f /var/log/agtrmerkezi/scheduler.log

# Installation logs (server kurulumu sırasında)
tail -f /var/log/agtrmerkezi/installation.log
```

---

**Durum:** Backend hazır, admin frontend UI bekleniyor
**Sonraki Görev:** Admin approval panel oluştur
**Test Server:** ID 1 (PENDING durumunda, onay bekliyor)
