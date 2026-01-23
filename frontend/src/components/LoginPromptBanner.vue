<template>
  <div v-if="!isLoggedIn" class="login-prompt-banner">
    <div class="prompt-content">
      <span class="prompt-icon">
        <Lock class="w-5 h-5" />
      </span>
      <span class="prompt-text">{{ message }}</span>
      <n-button size="small" type="primary" @click="goToLogin">
        Giris Yap
      </n-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Lock } from 'lucide-vue-next'

const props = defineProps({
  message: {
    type: String,
    default: 'Tum ozellikleri kullanmak icin giris yapin'
  }
})

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isLoggedIn = computed(() => !!authStore.user)

const goToLogin = () => {
  router.push({ name: 'login', query: { redirect: route.fullPath } })
}
</script>

<style scoped>
.login-prompt-banner {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(234, 88, 12, 0.05));
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.prompt-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.prompt-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(249, 115, 22, 0.2);
  border-radius: 8px;
  color: #f97316;
}

.prompt-text {
  flex: 1;
  color: #f97316;
  font-size: 14px;
}
</style>
