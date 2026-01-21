<template>
  <div class="min-h-screen py-12">
    <div class="container-custom">
      <h1 class="text-4xl font-display font-bold mb-8 text-center">
        <span class="text-gradient-orange">Destek Merkezi</span>
      </h1>

      <!-- Search -->
      <div class="max-w-2xl mx-auto mb-12">
        <div class="glass-card p-4">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Yardim konusu arayın..."
            class="input input-bordered bg-base-200 w-full"
          />
        </div>
      </div>

      <!-- Quick Links -->
      <div class="grid md:grid-cols-3 gap-6 mb-12">
        <div class="glass-card p-6 text-center hover:border-primary/50 transition-colors cursor-pointer">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/20 flex items-center justify-center">
            <svg class="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
            </svg>
          </div>
          <h3 class="font-bold text-lg mb-2">Sunucu Yardimi</h3>
          <p class="opacity-60 text-sm">Sunucu kurulumu, ayarları ve yönetimi</p>
        </div>

        <div class="glass-card p-6 text-center hover:border-secondary/50 transition-colors cursor-pointer">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-secondary/20 flex items-center justify-center">
            <svg class="w-8 h-8 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
          </div>
          <h3 class="font-bold text-lg mb-2">Ödeme & Fatura</h3>
          <p class="opacity-60 text-sm">Ödeme yontemleri, faturalar ve iadeler</p>
        </div>

        <div class="glass-card p-6 text-center hover:border-accent/50 transition-colors cursor-pointer">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-accent/20 flex items-center justify-center">
            <svg class="w-8 h-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h3 class="font-bold text-lg mb-2">Hesap Yardimi</h3>
          <p class="opacity-60 text-sm">Hesap ayarları, güvenlik ve profil</p>
        </div>
      </div>

      <!-- FAQ -->
      <div class="max-w-3xl mx-auto">
        <h2 class="text-2xl font-bold mb-6">Sik Sorulan Sorular</h2>

        <div class="space-y-4">
          <div v-for="(faq, index) in filteredFAQs" :key="index" class="glass-card overflow-hidden">
            <button
              @click="toggleFAQ(index)"
              class="w-full p-4 text-left flex items-center justify-between hover:bg-base-200/50 transition-colors"
            >
              <span class="font-semibold">{{ faq.question }}</span>
              <svg
                class="w-5 h-5 transition-transform"
                :class="{ 'rotate-180': openFAQ === index }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div v-show="openFAQ === index" class="px-4 pb-4 opacity-70">
              {{ faq.answer }}
            </div>
          </div>
        </div>

        <!-- Contact CTA -->
        <div class="mt-12 text-center">
          <p class="opacity-60 mb-4">Aradiginizi bulamadınız mı?</p>
          <router-link to="/contact">
            <button class="btn-gaming">
              Bize Ulasin
            </button>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const searchQuery = ref('')
const openFAQ = ref(null)

const faqs = [
  {
    question: 'Sunucu nasıl kiralarim?',
    answer: 'Mağaza sayfasından uygun paketi seçip ödeme yaparak sunucunuzu anında aktif edebilirsiniz. Sunucu panelinden tüm ayarları yapabilirsiniz.'
  },
  {
    question: 'Hangi ödeme yontemlerini kabul ediyorsunuz?',
    answer: 'Kredi karti, banka karti, havale/EFT ve papara ile ödeme yapabilirsiniz.'
  },
  {
    question: 'Sunucuma eklenti nasıl yüklerim?',
    answer: 'Sunucu panelindeki "Eklentiler" sekmesinden popüler eklentileri tek tıkla yükleyebilir veya kendi eklentilerinizi FTP ile yükleyebilirsiniz.'
  },
  {
    question: 'Sunucu IP adresimi nasıl öğrenirim?',
    answer: 'Sunucu panelinin ust kisminda IP adresiniz görüntülenir. Ayrica "IP Kopyala" butonu ile panoya kopyalayabilirsiniz.'
  },
  {
    question: 'RCON şifremi unuttum ne yapmalıyım?',
    answer: 'Sunucu panelindeki "Ayarlar" sekmesinden RCON şifrenizi değiştirebilirsiniz.'
  },
  {
    question: 'Iade politikaniz nedir?',
    answer: 'İlk 7 gun içinde kullanılmamış hizmetler için tam iade yapılır. Aktif kullanılan sunucular için iade yapılmaz.'
  }
]

const filteredFAQs = computed(() => {
  if (!searchQuery.value) return faqs
  const query = searchQuery.value.toLowerCase()
  return faqs.filter(faq =>
    faq.question.toLowerCase().includes(query) ||
    faq.answer.toLowerCase().includes(query)
  )
})

const toggleFAQ = (index) => {
  openFAQ.value = openFAQ.value === index ? null : index
}
</script>
