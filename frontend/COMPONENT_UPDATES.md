# Component Güncellemeleri

## ServerCard.vue Güncellemeleri

Mevcut ServerCard component'ine şu eklemeler yapılmalı:

### 1. Import ekle:
```javascript
import { useSubscriptionStore } from '@/stores/subscriptions'
```

### 2. Setup içinde:
```javascript
const subscriptionStore = useSubscriptionStore()
const subscription = computed(() => subscriptionStore.getByServerId(props.server.id))

const expiryStatus = computed(() => {
  if (!props.server.expires_at) return null

  const now = new Date()
  const expiry = new Date(props.server.expires_at)
  const days = Math.floor((expiry - now) / (1000 * 60 * 60 * 24))

  if (days < 0) return { text: 'Süresi Doldu', color: 'red' }
  if (days <= 1) return { text: `${days} Gün`, color: 'red' }
  if (days <= 3) return { text: `${days} Gün`, color: 'orange' }
  if (days <= 7) return { text: `${days} Gün`, color: 'yellow' }
  return { text: `${days} Gün`, color: 'green' }
})
```

### 3. Template'e ekle (card header):
```vue
<div class="expiry-badge" :class="expiryStatus?.color" v-if="expiryStatus">
  ⏰ {{ expiryStatus.text }}
</div>

<div class="auto-renew-badge" v-if="subscription?.auto_renew_enabled">
  🔄 Otomatik
</div>
```

### 4. CSS ekle:
```css
.expiry-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}
.expiry-badge.green { background: #28a745; color: white; }
.expiry-badge.yellow { background: #ffc107; color: #000; }
.expiry-badge.orange { background: #fd7e14; color: white; }
.expiry-badge.red { background: #dc3545; color: white; }
```

---

## NotificationPanel.vue Güncellemeleri

### Yeni bildirim tipleri ekle:

```javascript
const notificationConfig = {
  // ... mevcut tipler

  server_expiring_7days: { icon: '⏰', color: '#17a2b8' },
  server_expiring_3days: { icon: '⚠️', color: '#ffc107' },
  server_expiring_1day: { icon: '🔴', color: '#fd7e14' },
  renewal_success: { icon: '✅', color: '#28a745' },
  renewal_failed: { icon: '❌', color: '#dc3545' },
  grace_period_started: { icon: '⏳', color: '#ffc107' },
  server_suspended: { icon: '⛔', color: '#dc3545' }
}
```

---

Bu güncellemeler mevcut component'lere yapılmalı.
