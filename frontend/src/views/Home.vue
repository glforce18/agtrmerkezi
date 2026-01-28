<template>
  <div class="min-h-screen">
    <!-- Hero Section -->
    <section class="relative pt-20 pb-32">
      <div class="container mx-auto px-4">
        <div class="text-center max-w-4xl mx-auto">
          <!-- Logo -->
          <div class="mb-8">
            <div class="inline-block w-24 h-24 bg-primary rounded-2xl flex items-center justify-center shadow-elevated mx-auto hover:scale-105 transition-transform">
              <span class="text-5xl font-bold text-white">λ</span>
            </div>
          </div>

          <!-- Main Heading -->
          <h1 class="text-5xl md:text-6xl font-bold text-text-primary mb-6">
            AGTR Merkezi
          </h1>

          <p class="text-xl md:text-2xl text-text-secondary mb-12 max-w-2xl mx-auto">
            Profesyonel <span class="text-primary font-semibold">Counter-Strike 1.6</span> sunucu hosting platformu
          </p>

          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <router-link to="/servers/rent" class="btn btn-primary text-lg px-8 py-4 w-full sm:w-auto">
              🚀 Sunucu Kirala
            </router-link>
            <router-link to="/servers" class="btn btn-secondary text-lg px-8 py-4 w-full sm:w-auto">
              🎮 Sunucu Listesi
            </router-link>
          </div>

          <!-- Live Stats -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
            <div class="stat-card">
              <div class="text-4xl font-bold text-primary mb-2">150+</div>
              <div class="text-text-secondary">Aktif Sunucu</div>
            </div>

            <div class="stat-card">
              <div class="text-4xl font-bold text-primary mb-2">5,000+</div>
              <div class="text-text-secondary">Oyuncu</div>
            </div>

            <div class="stat-card">
              <div class="text-4xl font-bold text-primary mb-2">24/7</div>
              <div class="text-text-secondary">Destek</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-20">
      <div class="container mx-auto px-4">
        <!-- Section Header -->
        <div class="text-center mb-16">
          <h2 class="text-4xl md:text-5xl font-bold text-text-primary mb-4">
            Neden <span class="text-primary">AGTR Merkezi</span>?
          </h2>
          <div class="divider w-24 mx-auto mb-6"></div>
          <p class="text-text-secondary text-lg max-w-2xl mx-auto">
            Profesyonel gaming deneyimi için ihtiyacınız olan her şey
          </p>
        </div>

        <!-- Feature Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <!-- Feature 1 -->
          <div class="card p-8 group">
            <div class="mb-6">
              <div class="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <span class="text-4xl">⚡</span>
              </div>
            </div>
            <h3 class="text-2xl font-bold text-text-primary mb-3">Yüksek Performans</h3>
            <p class="text-text-secondary leading-relaxed">
              Son teknoloji donanım ve optimize edilmiş altyapı ile lag-free oyun deneyimi
            </p>
          </div>

          <!-- Feature 2 -->
          <div class="card p-8 group">
            <div class="mb-6">
              <div class="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <span class="text-4xl">🔧</span>
              </div>
            </div>
            <h3 class="text-2xl font-bold text-text-primary mb-3">Tam Kontrol</h3>
            <p class="text-text-secondary leading-relaxed">
              RCON konsolu, FTP erişimi ve detaylı yönetim paneli ile tam yetki
            </p>
          </div>

          <!-- Feature 3 -->
          <div class="card p-8 group">
            <div class="mb-6">
              <div class="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <span class="text-4xl">🛡️</span>
              </div>
            </div>
            <h3 class="text-2xl font-bold text-text-primary mb-3">DDoS Koruması</h3>
            <p class="text-text-secondary leading-relaxed">
              Enterprise seviye güvenlik ile sunucunuz her zaman çevrimiçi
            </p>
          </div>

          <!-- Feature 4 -->
          <div class="card p-8 group">
            <div class="mb-6">
              <div class="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <span class="text-4xl">🌐</span>
              </div>
            </div>
            <h3 class="text-2xl font-bold text-text-primary mb-3">FastDL Desteği</h3>
            <p class="text-text-secondary leading-relaxed">
              Oyuncularınız map ve mod'ları anında indirebilir
            </p>
          </div>

          <!-- Feature 5 -->
          <div class="card p-8 group">
            <div class="mb-6">
              <div class="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <span class="text-4xl">💬</span>
              </div>
            </div>
            <h3 class="text-2xl font-bold text-text-primary mb-3">Aktif Topluluk</h3>
            <p class="text-text-secondary leading-relaxed">
              Forum, Discord ve sosyal medya üzerinden güçlü topluluk desteği
            </p>
          </div>

          <!-- Feature 6 -->
          <div class="card p-8 group">
            <div class="mb-6">
              <div class="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <span class="text-4xl">💰</span>
              </div>
            </div>
            <h3 class="text-2xl font-bold text-text-primary mb-3">Uygun Fiyat</h3>
            <p class="text-text-secondary leading-relaxed">
              Rekabetçi fiyatlar ve esnek ödeme seçenekleri
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Forum CTA Section -->
    <section class="py-20">
      <div class="container mx-auto px-4">
        <div class="card p-12 text-center max-w-3xl mx-auto">
          <h2 class="text-3xl md:text-4xl font-bold text-text-primary mb-4">
            Topluluğa Katıl
          </h2>
          <p class="text-text-secondary text-lg mb-8 max-w-xl mx-auto">
            Binlerce CS 1.6 oyuncusuyla tanış, deneyimlerini paylaş ve yardım al
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link to="/forum" class="btn btn-primary text-lg px-8 py-4">
              Foruma Git
            </router-link>
            <router-link to="/register" class="btn btn-secondary text-lg px-8 py-4">
              Üye Ol
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Popular Servers Section -->
    <section class="py-20 bg-dark-card/50">
      <div class="container mx-auto px-4">
        <div class="text-center mb-12">
          <h2 class="text-3xl md:text-4xl font-bold text-text-primary mb-4">
            Popüler Sunucular
          </h2>
          <p class="text-text-secondary">En çok tercih edilen sunucular</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          <!-- Server cards would be dynamically loaded here -->
          <div v-for="i in 6" :key="i" class="card p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-text-primary">CS 1.6 Server #{{ i }}</h3>
              <span class="badge badge-success">Online</span>
            </div>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between text-text-secondary">
                <span>IP:</span>
                <span class="text-text-primary font-mono">192.168.1.{{ i }}:27015</span>
              </div>
              <div class="flex justify-between text-text-secondary">
                <span>Oyuncular:</span>
                <span class="text-primary font-semibold">{{ 10 + i }}/32</span>
              </div>
              <div class="flex justify-between text-text-secondary">
                <span>Map:</span>
                <span class="text-text-primary">de_dust2</span>
              </div>
            </div>
          </div>
        </div>

        <div class="text-center mt-12">
          <router-link to="/servers" class="btn btn-secondary px-8 py-3">
            Tüm Sunucular
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
// No complex logic needed for home page
</script>
