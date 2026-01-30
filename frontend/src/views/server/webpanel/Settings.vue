<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-text-primary">Sunucu Ayarları</h2>
        <p class="text-text-muted text-sm mt-1">RCON ve sunucu yapılandırmasını yönetin</p>
      </div>
    </div>

    <!-- Settings Form -->
    <div class="glass-card p-6 fade-in-up">
      <form @submit.prevent="saveSettings" class="space-y-6">
        <!-- Hostname -->
        <div>
          <label class="block text-sm font-medium text-text-primary mb-2">
            Sunucu Adı (Hostname)
          </label>
          <input
            v-model="form.hostname"
            type="text"
            class="input"
            placeholder="Örn: AGTR | Half-Life Server"
            maxlength="128"
          />
          <p class="text-xs text-text-muted mt-1">
            Oyuncuların göreceği sunucu adı (max 128 karakter)
          </p>
        </div>

        <!-- RCON Password -->
        <div>
          <label class="block text-sm font-medium text-text-primary mb-2">
            RCON Şifresi
          </label>
          <div class="relative">
            <input
              v-model="form.rcon_password"
              :type="showRconPassword ? 'text' : 'password'"
              class="input pr-10"
              placeholder="Minimum 8 karakter"
              minlength="8"
              maxlength="32"
            />
            <button
              type="button"
              @click="showRconPassword = !showRconPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary"
            >
              {{ showRconPassword ? '🙈' : '👁️' }}
            </button>
          </div>
          <p class="text-xs text-status-warning mt-1">
            ⚠️ RCON şifresini değiştirmek sunucunun yeniden başlatılmasını gerektirir
          </p>
        </div>

        <!-- SV Password -->
        <div>
          <label class="block text-sm font-medium text-text-primary mb-2">
            Sunucu Şifresi (sv_password)
          </label>
          <div class="relative">
            <input
              v-model="form.sv_password"
              :type="showSvPassword ? 'text' : 'password'"
              class="input pr-10"
              placeholder="Boş bırakın = şifresiz sunucu"
              maxlength="32"
            />
            <button
              type="button"
              @click="showSvPassword = !showSvPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary"
            >
              {{ showSvPassword ? '🙈' : '👁️' }}
            </button>
          </div>
          <p class="text-xs text-text-muted mt-1">
            Sunucuya giriş için şifre. Boş bırakırsanız herkese açık olur.
          </p>
        </div>

        <!-- Max Players -->
        <div>
          <label class="block text-sm font-medium text-text-primary mb-2">
            Maksimum Oyuncu (Max Players)
          </label>
          <input
            v-model.number="form.max_players"
            type="number"
            class="input"
            min="2"
            max="32"
          />
          <p class="text-xs text-status-warning mt-1">
            ⚠️ Slot sayısını değiştirmek sunucunun yeniden başlatılmasını gerektirir
          </p>
        </div>

        <!-- Submit Button -->
        <div class="flex gap-3 pt-4 border-t border-dark-border">
          <button
            type="submit"
            :disabled="saving || !serverStatus?.is_online"
            class="btn btn-primary"
          >
            <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ saving ? 'Kaydediliyor...' : 'Ayarları Kaydet' }}
          </button>
          <button
            type="button"
            @click="resetForm"
            class="btn btn-secondary"
          >
            İptal
          </button>
        </div>

        <!-- Warning for offline server -->
        <div v-if="!serverStatus?.is_online" class="alert alert-warning">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          Sunucu çevrimdışı. Ayarları değiştirmek için sunucuyu başlatın.
        </div>
      </form>
    </div>

    <!-- Info Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- RCON Info -->
      <div class="glass-card p-5 fade-in-up delay-100">
        <h3 class="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-status-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          RCON Nedir?
        </h3>
        <p class="text-xs text-text-muted leading-relaxed">
          RCON (Remote Console), sunucunuzu uzaktan yönetmenizi sağlayan bir araçtır.
          RCON şifresi ile HLSW, ServerDX gibi programlardan sunucunuza bağlanabilirsiniz.
        </p>
      </div>

      <!-- SV Password Info -->
      <div class="glass-card p-5 fade-in-up delay-200">
        <h3 class="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-status-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          Sunucu Şifresi Nedir?
        </h3>
        <p class="text-xs text-text-muted leading-relaxed">
          sv_password ile sunucunuza sadece şifreyi bilen oyuncular girebilir.
          Özel maçlar veya turnuvalar için kullanışlıdır. Boş bırakırsanız herkes girebilir.
        </p>
      </div>
    </div>

    <!-- Success Message -->
    <div
      v-if="successMessage"
      class="glass-card p-4 bg-status-success/10 border-status-success/30 fade-in-up"
    >
      <div class="flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-status-success" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <span class="text-status-success font-medium">{{ successMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import apiClient from '@/api/client'

const props = defineProps({
  serverId: Number,
  serverInfo: Object,
  serverStatus: Object
})

const emit = defineEmits(['refresh'])

const form = ref({
  hostname: '',
  rcon_password: '',
  sv_password: '',
  max_players: 20
})

const saving = ref(false)
const showRconPassword = ref(false)
const showSvPassword = ref(false)
const successMessage = ref('')

// Initialize form with server info
watch(() => props.serverInfo, (newInfo) => {
  if (newInfo) {
    form.value.hostname = newInfo.name || ''
    form.value.rcon_password = newInfo.rcon_password || ''
    form.value.max_players = newInfo.slots || 20
  }
}, { immediate: true })

const saveSettings = async () => {
  if (!props.serverStatus?.is_online) {
    alert('Sunucu çalışmıyor! Ayarları değiştirmek için sunucuyu başlatın.')
    return
  }

  saving.value = true
  successMessage.value = ''

  try {
    // Prepare update data (only send changed fields)
    const updateData = {}

    if (form.value.hostname !== props.serverInfo?.name) {
      updateData.hostname = form.value.hostname
    }
    if (form.value.rcon_password !== props.serverInfo?.rcon_password) {
      updateData.rcon_password = form.value.rcon_password
    }
    if (form.value.sv_password !== '') {
      updateData.sv_password = form.value.sv_password
    }
    if (form.value.max_players !== props.serverInfo?.slots) {
      updateData.max_players = form.value.max_players
    }

    if (Object.keys(updateData).length === 0) {
      alert('Hiçbir değişiklik yapılmadı.')
      return
    }

    const response = await apiClient.patch(
      `/servers/${props.serverId}/webpanel/settings`,
      updateData
    )

    successMessage.value = response.data.message || 'Ayarlar başarıyla kaydedildi!'

    // Show restart warning if needed
    if (response.data.data?.restart_required) {
      setTimeout(() => {
        if (confirm('Bazı ayarlar sunucunun yeniden başlatılmasını gerektiriyor. Şimdi restart yapalım mı?')) {
          restartServer()
        }
      }, 1000)
    }

    // Refresh parent data
    setTimeout(() => {
      emit('refresh')
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    alert('Kaydetme hatası: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  if (props.serverInfo) {
    form.value.hostname = props.serverInfo.name || ''
    form.value.rcon_password = props.serverInfo.rcon_password || ''
    form.value.sv_password = ''
    form.value.max_players = props.serverInfo.slots || 20
  }
}

const restartServer = async () => {
  try {
    await apiClient.post(`/servers/${props.serverId}/restart`)
    alert('Sunucu yeniden başlatılıyor...')
    setTimeout(() => emit('refresh'), 3000)
  } catch (error) {
    alert('Restart hatası: ' + (error.response?.data?.detail || error.message))
  }
}
</script>
