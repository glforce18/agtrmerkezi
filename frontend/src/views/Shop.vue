<template>
  <div class="min-h-screen ">
    <div class="container-custom py-8">
      <!-- Header -->
      <div class="mb-12 text-center animate-slide-down">
        <h1 class="text-5xl font-display font-bold mb-4">
          <span class="neon-text">Premium Paketler</span>
        </h1>
        <p class="text-xl opacity-60 max-w-2xl mx-auto">
          Sunucu yönetiminizi bir üst seviyeye taşıyın. En uygun planı seçin ve avantajlardan yararlanın.
        </p>
      </div>

      <!-- Pricing Toggle -->
      <div class="flex justify-center mb-12 animate-slide-up">
        <div class="tabs tabs-boxed bg-base-200/50 backdrop-blur-sm">
          <a
            class="tab"
            :class="{ 'tab-active': billingPeriod === 'monthly' }"
            @click="billingPeriod = 'monthly'"
          >
            Aylık
          </a>
          <a
            class="tab"
            :class="{ 'tab-active': billingPeriod === 'yearly' }"
            @click="billingPeriod = 'yearly'"
          >
            Yıllık
            <span class="badge badge-success badge-sm ml-2">20% İndirim</span>
          </a>
        </div>
      </div>

      <!-- Pricing Cards -->
      <div class="grid md:grid-cols-3 gap-8 mb-16 animate-slide-up" style="animation-delay: 0.1s">
        <!-- Free Plan -->
        <BaseCard variant="glass" class="card-hover relative">
          <div class="p-8">
            <div class="text-center mb-6">
              <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-base-200 flex items-center justify-center">
                <RocketIcon class="w-8 h-8 opacity-60" />
              </div>
              <h3 class="text-2xl font-bold mb-2">Ücretsiz</h3>
              <p class="opacity-60 text-sm mb-4">Başlamak için ideal</p>
              <div class="text-4xl font-bold mb-2">
                $0
                <span class="text-lg font-normal opacity-60">/ay</span>
              </div>
            </div>

            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">1 Sunucu</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Maksimum 12 slot</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Temel panel erişimi</span>
              </li>
              <li class="flex items-center gap-2">
                <XIcon class="w-5 h-5 text-error flex-shrink-0" />
                <span class="text-sm opacity-50">DDoS koruması</span>
              </li>
              <li class="flex items-center gap-2">
                <XIcon class="w-5 h-5 text-error flex-shrink-0" />
                <span class="text-sm opacity-50">Öncelikli destek</span>
              </li>
            </ul>

            <BaseButton variant="outline" block>
              Mevcut Plan
            </BaseButton>
          </div>
        </BaseCard>

        <!-- Pro Plan -->
        <BaseCard variant="glass" class="card-hover relative border-2 border-primary">
          <div class="absolute -top-4 left-1/2 -translate-x-1/2">
            <span class="badge badge-primary badge-lg">En Popüler</span>
          </div>
          <div class="p-8">
            <div class="text-center mb-6">
              <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <ZapIcon class="w-8 h-8 text-white" />
              </div>
              <h3 class="text-2xl font-bold mb-2">Pro</h3>
              <p class="opacity-60 text-sm mb-4">Profesyoneller için</p>
              <div class="text-4xl font-bold mb-2">
                <span v-if="billingPeriod === 'monthly'">${{ plans.pro.monthly }}</span>
                <span v-else>${{ plans.pro.yearly }}</span>
                <span class="text-lg font-normal opacity-60">/{{ billingPeriod === 'monthly' ? 'ay' : 'yıl' }}</span>
              </div>
              <p v-if="billingPeriod === 'yearly'" class="text-xs text-success">
                Yıllık ${(plans.pro.monthly * 12).toFixed(2)} yerine ${plans.pro.yearly}
              </p>
            </div>

            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">5 Sunucu</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Maksimum 32 slot</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Gelişmiş panel özellikleri</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">DDoS koruması</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Öncelikli destek</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Otomatik yedekleme</span>
              </li>
            </ul>

            <BaseButton variant="gaming" block @click="selectPlan('pro')">
              <ShoppingCartIcon class="w-4 h-4 mr-2" />
              Satın Al
            </BaseButton>
          </div>
        </BaseCard>

        <!-- Enterprise Plan -->
        <BaseCard variant="glass" class="card-hover relative">
          <div class="p-8">
            <div class="text-center mb-6">
              <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-accent to-error flex items-center justify-center">
                <CrownIcon class="w-8 h-8 text-white" />
              </div>
              <h3 class="text-2xl font-bold mb-2">Enterprise</h3>
              <p class="opacity-60 text-sm mb-4">Kurumsal çözümler</p>
              <div class="text-4xl font-bold mb-2">
                <span v-if="billingPeriod === 'monthly'">${{ plans.enterprise.monthly }}</span>
                <span v-else>${{ plans.enterprise.yearly }}</span>
                <span class="text-lg font-normal opacity-60">/{{ billingPeriod === 'monthly' ? 'ay' : 'yıl' }}</span>
              </div>
              <p v-if="billingPeriod === 'yearly'" class="text-xs text-success">
                Yıllık ${(plans.enterprise.monthly * 12).toFixed(2)} yerine ${plans.enterprise.yearly}
              </p>
            </div>

            <ul class="space-y-3 mb-8">
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Sınırsız sunucu</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Sınırsız slot</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Tüm özellikler</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Gelişmiş DDoS koruması</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">7/24 Özel destek</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">Özel entegrasyonlar</span>
              </li>
              <li class="flex items-center gap-2">
                <CheckIcon class="w-5 h-5 text-success flex-shrink-0" />
                <span class="text-sm">SLA garantisi</span>
              </li>
            </ul>

            <BaseButton variant="primary" block @click="selectPlan('enterprise')">
              <ShoppingCartIcon class="w-4 h-4 mr-2" />
              Satın Al
            </BaseButton>
          </div>
        </BaseCard>
      </div>

      <!-- Features Comparison -->
      <div class="mb-16 animate-slide-up" style="animation-delay: 0.2s">
        <h2 class="text-3xl font-display font-bold text-center mb-8">
          <span class="text-gradient-primary">Özellik Karşılaştırması</span>
        </h2>

        <BaseCard variant="glass">
          <div class="overflow-x-auto">
            <table class="table">
              <thead>
                <tr>
                  <th>Özellik</th>
                  <th class="text-center">Ücretsiz</th>
                  <th class="text-center">Pro</th>
                  <th class="text-center">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Sunucu Sayısı</td>
                  <td class="text-center">1</td>
                  <td class="text-center">5</td>
                  <td class="text-center">Sınırsız</td>
                </tr>
                <tr>
                  <td>Maksimum Slot</td>
                  <td class="text-center">12</td>
                  <td class="text-center">32</td>
                  <td class="text-center">Sınırsız</td>
                </tr>
                <tr>
                  <td>DDoS Koruması</td>
                  <td class="text-center"><XIcon class="w-5 h-5 text-error inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                </tr>
                <tr>
                  <td>Otomatik Yedekleme</td>
                  <td class="text-center"><XIcon class="w-5 h-5 text-error inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                </tr>
                <tr>
                  <td>Öncelikli Destek</td>
                  <td class="text-center"><XIcon class="w-5 h-5 text-error inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                </tr>
                <tr>
                  <td>Özel Entegrasyonlar</td>
                  <td class="text-center"><XIcon class="w-5 h-5 text-error inline" /></td>
                  <td class="text-center"><XIcon class="w-5 h-5 text-error inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                </tr>
                <tr>
                  <td>SLA Garantisi</td>
                  <td class="text-center"><XIcon class="w-5 h-5 text-error inline" /></td>
                  <td class="text-center"><XIcon class="w-5 h-5 text-error inline" /></td>
                  <td class="text-center"><CheckIcon class="w-5 h-5 text-success inline" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </BaseCard>
      </div>

      <!-- FAQ Section -->
      <div class="mb-16 animate-slide-up" style="animation-delay: 0.3s">
        <h2 class="text-3xl font-display font-bold text-center mb-8">
          <span class="text-gradient-primary">Sıkça Sorulan Sorular</span>
        </h2>

        <div class="max-w-3xl mx-auto space-y-4">
          <div class="collapse collapse-arrow bg-base-200/50 backdrop-blur-sm">
            <input type="radio" name="faq-accordion" checked="checked" />
            <div class="collapse-title text-xl font-medium">
              Paketimi istediğim zaman değiştirebilir miyim?
            </div>
            <div class="collapse-content">
              <p class="opacity-60">
                Evet, paketinizi istediğiniz zaman yükseltebilir veya düşürebilirsiniz. Ödediğiniz ücret orantılı olarak hesaplanır.
              </p>
            </div>
          </div>

          <div class="collapse collapse-arrow bg-base-200/50 backdrop-blur-sm">
            <input type="radio" name="faq-accordion" />
            <div class="collapse-title text-xl font-medium">
              Hangi ödeme yöntemlerini kabul ediyorsunuz?
            </div>
            <div class="collapse-content">
              <p class="opacity-60">
                Kredi kartı, PayPal, banka havalesi ve kripto para ile ödeme kabul ediyoruz.
              </p>
            </div>
          </div>

          <div class="collapse collapse-arrow bg-base-200/50 backdrop-blur-sm">
            <input type="radio" name="faq-accordion" />
            <div class="collapse-title text-xl font-medium">
              İptal politikanız nedir?
            </div>
            <div class="collapse-content">
              <p class="opacity-60">
                İlk 30 gün içinde memnun kalmazsanız tam para iadesi garantisi sunuyoruz.
              </p>
            </div>
          </div>

          <div class="collapse collapse-arrow bg-base-200/50 backdrop-blur-sm">
            <input type="radio" name="faq-accordion" />
            <div class="collapse-title text-xl font-medium">
              Sunucu konumu seçebilir miyim?
            </div>
            <div class="collapse-content">
              <p class="opacity-60">
                Evet, Avrupa, Amerika ve Asya'da birden fazla veri merkezimiz bulunmaktadır.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- CTA Section -->
      <div class="text-center animate-slide-up" style="animation-delay: 0.4s">
        <BaseCard variant="glass" class="max-w-3xl mx-auto">
          <div class="p-12">
            <h2 class="text-3xl font-display font-bold mb-4">
              <span class="neon-text">Hala Kararsız mısınız?</span>
            </h2>
            <p class="text-xl opacity-60 mb-8">
              Ekibimiz size en uygun planı seçmenizde yardımcı olmaktan mutluluk duyar.
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
              <BaseButton variant="gaming" size="lg">
                <MessageCircleIcon class="w-5 h-5 mr-2" />
                Canlı Destek
              </BaseButton>
              <BaseButton variant="outline" size="lg">
                <MailIcon class="w-5 h-5 mr-2" />
                İletişime Geç
              </BaseButton>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import {
  RocketIcon,
  ZapIcon,
  CrownIcon,
  CheckIcon,
  XIcon,
  ShoppingCartIcon,
  MessageCircleIcon,
  MailIcon
} from 'lucide-vue-next'

const router = useRouter()
const billingPeriod = ref('monthly')

const plans = {
  pro: {
    monthly: 19.99,
    yearly: 191.90 // 20% discount
  },
  enterprise: {
    monthly: 49.99,
    yearly: 479.90 // 20% discount
  }
}

const selectPlan = (planType) => {
  // Plan selected - proceed to checkout
  // Redirect to checkout or payment page
  router.push({
    name: 'checkout',
    query: {
      plan: planType,
      period: billingPeriod.value
    }
  })
}
</script>

<style scoped>
.neon-text {
  @apply text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent;
}

.text-gradient-primary {
  @apply bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-down {
  animation: slideDown 0.6s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out 0.2s backwards;
}
</style>
