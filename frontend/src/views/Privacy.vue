<template>
  <div class="min-h-screen py-12">
    <div class="container-custom">
      <div class="max-w-4xl mx-auto">
        <h1 class="text-4xl font-display font-bold mb-8">
          <span class="text-gradient-orange">Gizlilik Politikasi</span>
        </h1>

        <div class="glass-card p-8 prose prose-invert max-w-none">
          <p class="lead opacity-80">
            AGTR Merkezi olarak gizliliginize onem veriyoruz.
          </p>

          <h2>Toplanan Veriler</h2>
          <ul>
            <li>Hesap bilgileri (kullanici adi, e-posta, sifre hash)</li>
            <li>Oyun istatistikleri ve aktivite kayitlari</li>
            <li>IP adresi ve tarayici bilgileri</li>
            <li>Cerez verileri</li>
          </ul>

          <h2>Veri Kullanimi</h2>
          <p>Toplanan veriler su amaclarla kullanilir:</p>
          <ul>
            <li>Hesap yonetimi ve guvenlik</li>
            <li>Oyun istatistiklerinin hesaplanmasi</li>
            <li>Platform iyilestirmeleri</li>
            <li>Destek hizmetleri</li>
          </ul>

          <h2>Veri Paylasimi</h2>
          <p>
            Kisisel verileriniz ucuncu taraflarla paylasilmaz. Sadece yasal zorunluluk durumunda
            yetkili makamlarla paylasim yapilabilir.
          </p>

          <h2>Cerezler</h2>
          <p>
            Sitemiz oturum yonetimi ve kullanici tercihlerini hatirlamak icin cerez kullanir.
            Tarayici ayarlarindan cerezleri devre disi birakabilirsiniz.
          </p>

          <h2>Veri Guvenligi</h2>
          <p>
            Verileriniz sifrelenmis olarak saklanir. Duzenli guvenlik taramalari yapilir.
          </p>

          <h2>Haklariniz</h2>
          <ul>
            <li>Verilerinize erisim talep edebilirsiniz</li>
            <li>Verilerinizin silinmesini isteyebilirsiniz</li>
            <li>Veri tasinabilirligi talebinde bulunabilirsiniz</li>
          </ul>

          <h2>Iletisim</h2>
          <p>
            Gizlilik ile ilgili sorulariniz icin <router-link to="/contact" class="link link-primary">iletisim sayfamizi</router-link> kullanabilirsiniz.
          </p>

          <p class="text-sm opacity-60 mt-8">
            Son guncelleme: 17 Ocak 2026
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
