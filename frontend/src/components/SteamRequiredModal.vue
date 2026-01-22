<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="steam-modal-overlay" @click.self="$emit('close')">
        <div class="steam-modal">
          <div class="modal-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h3>Steam Hesabi Gerekli</h3>
          <p>Bu ozellik icin Steam hesabinizi baglameniz gerekiyor. Steam baglantisi, oyuncu kimliginizi dogrulamak ve topluluk guvenligini saglamak icin kullanilir.</p>
          <div class="modal-features">
            <div class="feature">
              <span class="feature-icon">🎮</span>
              <span>Oyuncu kimligi dogrulama</span>
            </div>
            <div class="feature">
              <span class="feature-icon">🛡️</span>
              <span>Spam ve sahte hesap onleme</span>
            </div>
            <div class="feature">
              <span class="feature-icon">🏆</span>
              <span>Turnuva ve ELO sistemine erisim</span>
            </div>
          </div>
          <div class="modal-actions">
            <button class="btn-steam" @click="$emit('connect')">
              <svg class="steam-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2a10 10 0 0 1 10 10 10 10 0 0 1-10 10c-4.6 0-8.45-3.08-9.64-7.27l3.83 1.58a2.84 2.84 0 0 0 2.78 2.27c1.56 0 2.83-1.27 2.83-2.83v-.13l3.4-2.43h.08c2.08 0 3.77-1.69 3.77-3.77s-1.69-3.77-3.77-3.77-3.77 1.69-3.77 3.77v.05l-2.37 3.46-.16-.01c-.55 0-1.08.16-1.53.45L2 11.54A10 10 0 0 1 12 2z"/>
              </svg>
              Steam ile Baglan
            </button>
            <button class="btn-cancel" @click="$emit('close')">Vazgec</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  show: Boolean
})

defineEmits(['close', 'connect'])
</script>

<style scoped>
.steam-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.steam-modal {
  background: linear-gradient(135deg, #1a1a1f 0%, #252530 100%);
  border: 1px solid #3a3a45;
  border-radius: 20px;
  padding: 32px;
  max-width: 420px;
  width: 90%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #171a21, #1b2838);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.modal-icon svg {
  width: 32px;
  height: 32px;
  color: #66c0f4;
}

h3 {
  color: #fff;
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 12px;
}

p {
  color: #888;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 24px;
}

.modal-features {
  background: rgba(102, 192, 244, 0.05);
  border: 1px solid rgba(102, 192, 244, 0.1);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
}

.feature {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  color: #aaa;
  font-size: 13px;
}

.feature-icon {
  font-size: 18px;
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-steam {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: linear-gradient(135deg, #171a21, #1b2838);
  color: #66c0f4;
  border: 1px solid #66c0f4;
  padding: 14px 24px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-steam:hover {
  background: #66c0f4;
  color: #171a21;
}

.steam-icon {
  width: 20px;
  height: 20px;
}

.btn-cancel {
  background: transparent;
  color: #666;
  border: 1px solid #333;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  border-color: #555;
  color: #888;
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .steam-modal,
.modal-leave-to .steam-modal {
  transform: scale(0.9) translateY(20px);
}
</style>
