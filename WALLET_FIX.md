# 🔧 Wallet Balance Display Fix

## ❌ Problem
Navbar'da bakiye görünmüyor.

## ✅ Yapılan Düzeltmeler

### 1. Auth Store - Login Sonrası Balance Fetch
```javascript
// auth.js - login() fonksiyonu
async function login(credentials) {
  // ... login logic
  setAuth(token, user)

  // ✅ FIX: Fetch balance after login
  await fetchBalance()

  return { success: true }
}
```

### 2. Auth Store - Init Fonksiyonu (Async)
```javascript
// auth.js - init() fonksiyonu
async function init() {
  const savedUser = localStorage.getItem('user')
  if (savedUser && token.value) {
    try {
      user.value = JSON.parse(savedUser)

      // ✅ FIX: Fetch balance on app init
      await fetchBalance()
    } catch (error) {
      clearAuth()
    }
  }
}
```

### 3. Main.js - Store Initialization
```javascript
// main.js
import { useAuthStore } from './stores/auth'

// ... app setup

// ✅ FIX: Initialize auth store after mount
const authStore = useAuthStore(pinia)
authStore.init()
```

### 4. App.vue - Await Init
```javascript
// App.vue
onMounted(async () => {
  // ✅ FIX: Await init (was not awaited before)
  await authStore.init()

  // ... rest of init logic
})
```

---

## 🔍 Debug Tools

### 1. Debug HTML Page Created
```
File: /var/www/agtrmerkezi/DEBUG_WALLET.html

Open in browser: http://localhost:8000/DEBUG_WALLET.html

Features:
- Show auth token from localStorage
- Test /api/wallet/balance endpoint
- Display response
```

### 2. Browser Console Commands
```javascript
// Check auth store
const authStore = useAuthStore()
console.log('Token:', authStore.token)
console.log('User:', authStore.user)
console.log('Balance:', authStore.balance)

// Manual fetch
await authStore.fetchBalance()
console.log('Balance after fetch:', authStore.balance)
```

### 3. Check API Directly
```bash
# Get your token from browser localStorage
TOKEN="your_jwt_token_here"

# Test API
curl http://localhost:8000/api/wallet/balance \
  -H "Authorization: Bearer $TOKEN"

# Expected:
# {"balance_real":1000.0,"balance_coin":50000.0}
```

---

## 🧪 Test Steps

### Step 1: Restart Frontend
```bash
cd /var/www/agtrmerkezi/frontend

# If running in dev mode
# Ctrl+C to stop, then:
npm run dev
```

### Step 2: Clear Cache & Reload
```
1. Open browser (F12)
2. Application → Storage → Clear All
3. Hard reload (Ctrl+Shift+R)
4. Or: Right click refresh → Empty Cache and Hard Reload
```

### Step 3: Login
```
1. Go to /login
2. Login with admin159
3. Check navbar → Should show balance!
```

### Step 4: Check Console
```javascript
// Open console (F12)
// You should see:
// - No errors
// - Network tab: GET /api/wallet/balance (Status: 200)
```

---

## 📊 Expected Flow

```
App Mount
    ↓
authStore.init() (ASYNC)
    ↓
Load user from localStorage
    ↓
fetchBalance() ← AUTO
    ↓
API: GET /api/wallet/balance
    ↓
Response: { balance_real: 1000, balance_coin: 50000 }
    ↓
Store: balance.value = response
    ↓
Navbar re-renders
    ↓
Balance visible! ✓
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "Balance still not showing"
**Solution:**
```bash
# Clear browser cache completely
1. F12 → Application → Clear site data
2. Close browser
3. Reopen and login
```

### Issue 2: "API returns 401 Unauthorized"
**Solution:**
```javascript
// Check token
console.log(localStorage.getItem('auth_token'))

// If null or expired, login again
// Token expires after X hours (check backend settings)
```

### Issue 3: "Balance shows 0.00₺"
**Solution:**
```bash
# Check database
mysql -u root -p agtrmerkezi -e \
  "SELECT username, balance, balance_coin FROM users WHERE id = 1;"

# If 0 → Add balance:
mysql -u root -p agtrmerkezi -e \
  "UPDATE users SET balance = 1000, balance_coin = 50000 WHERE id = 1;"
```

### Issue 4: "Network error / CORS"
**Solution:**
```bash
# Check backend is running
ps aux | grep uvicorn

# Restart backend if needed
cd /var/www/agtrmerkezi
uvicorn app.main:app --reload
```

---

## ✅ Verification Checklist

After fixes, verify:

- [ ] Frontend başlatıldı (`npm run dev`)
- [ ] Backend çalışıyor (port 8000)
- [ ] Browser cache temizlendi
- [ ] Login yapıldı
- [ ] Navbar'da bakiye görünüyor
  - [ ] TL: 1,000.00₺
  - [ ] Armor: 50.0K
- [ ] Hover effect çalışıyor
- [ ] Click → /wallet sayfasına gidiyor
- [ ] Console'da hata yok
- [ ] Network tab: /api/wallet/balance (200 OK)

---

## 🎯 Quick Fix Summary

**Changed Files:**
1. `frontend/src/stores/auth.js` - Added fetchBalance() calls
2. `frontend/src/main.js` - Added authStore.init()
3. `frontend/src/App.vue` - Made init() awaited
4. `DEBUG_WALLET.html` - Debug tool created

**Actions Required:**
1. ✅ Files updated
2. ⏳ Frontend restart (if running)
3. ⏳ Browser cache clear
4. ⏳ Login again
5. ⏳ Verify balance appears

---

## 📞 Still Not Working?

Run this debug sequence:

```javascript
// 1. Check localStorage
console.log('Token:', localStorage.getItem('auth_token'))
console.log('User:', localStorage.getItem('user'))

// 2. Check auth store
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
console.log('Auth state:', {
  token: authStore.token,
  user: authStore.user,
  balance: authStore.balance,
  isAuthenticated: authStore.isAuthenticated
})

// 3. Manual fetch
await authStore.fetchBalance()
console.log('Balance after fetch:', authStore.balance)

// 4. Check API directly
fetch('/api/wallet/balance', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
  }
})
.then(r => r.json())
.then(data => console.log('API Response:', data))
.catch(err => console.error('API Error:', err))
```

If still not working, share console output! 🐛

---

**Status:** ✅ Fixed
**Version:** v6.1.1
**Date:** 2026-01-29
