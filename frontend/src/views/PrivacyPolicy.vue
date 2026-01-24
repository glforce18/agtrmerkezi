<template>
  <div class="privacy-policy-page">
    <div class="container">
      <!-- Header -->
      <div class="page-header">
        <h1>Gizlilik Politikasi ve Cerez Kullanimi</h1>
        <p class="subtitle">Son guncelleme: Ocak 2026</p>
      </div>

      <!-- Content -->
      <div class="policy-content">
        <!-- Giris -->
        <section class="policy-section">
          <h2>1. Giris</h2>
          <p>
            AGTR Merkezi olarak gizliliginize onem veriyoruz. Bu gizlilik politikasi,
            web sitemizi ziyaret ettiginizde hangi bilgileri topladigimizi, bu bilgileri
            nasil kullandigimizi ve korudugumuzu aciklamaktadir.
          </p>
          <p>
            Sitemizi kullanarak bu politikayi kabul etmis sayilirsiniz.
          </p>
        </section>

        <!-- Toplanan Bilgiler -->
        <section class="policy-section">
          <h2>2. Toplanan Bilgiler</h2>

          <h3>2.1 Otomatik Toplanan Bilgiler</h3>
          <ul>
            <li>IP adresi</li>
            <li>Tarayici turu ve surumu</li>
            <li>Isletim sistemi</li>
            <li>Ziyaret edilen sayfalar ve sureler</li>
            <li>Referans URL'ler</li>
          </ul>

          <h3>2.2 Kullanici Tarafindan Saglanan Bilgiler</h3>
          <ul>
            <li>Kullanici adi</li>
            <li>E-posta adresi</li>
            <li>Steam ID (Steam ile giris yapildiginda)</li>
            <li>Profil bilgileri (avatar, biyografi vb.)</li>
          </ul>
        </section>

        <!-- Cerez Politikasi -->
        <section class="policy-section">
          <h2>3. Cerez (Cookie) Politikasi</h2>
          <p>
            Cerezler, web sitelerinin tarayiciniza kaydettigi kucuk metin dosyalaridir.
            Sitemiz asagidaki cerez turlerini kullanmaktadir:
          </p>

          <div class="cookie-table">
            <table>
              <thead>
                <tr>
                  <th>Cerez Adi</th>
                  <th>Amaci</th>
                  <th>Suresi</th>
                  <th>Turu</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>csrf_token</code></td>
                  <td>CSRF saldirilarini onleme</td>
                  <td>24 saat</td>
                  <td>Zorunlu</td>
                </tr>
                <tr>
                  <td><code>session_token</code></td>
                  <td>Oturum yonetimi</td>
                  <td>7 gun</td>
                  <td>Zorunlu</td>
                </tr>
                <tr>
                  <td><code>agtr_cookie_consent</code></td>
                  <td>Cerez tercihlerinizi hatirlamak</td>
                  <td>1 yil</td>
                  <td>Zorunlu</td>
                </tr>
                <tr>
                  <td><code>agtr_theme</code></td>
                  <td>Tema tercihi (karanlik/acik)</td>
                  <td>1 yil</td>
                  <td>Tercih</td>
                </tr>
                <tr>
                  <td><code>agtr_language</code></td>
                  <td>Dil tercihi</td>
                  <td>1 yil</td>
                  <td>Tercih</td>
                </tr>
                <tr>
                  <td><code>agtr_last_server</code></td>
                  <td>Son goruntuledginiz sunucu</td>
                  <td>30 gun</td>
                  <td>Tercih</td>
                </tr>
                <tr>
                  <td><code>agtr_volume</code></td>
                  <td>Ses seviyesi tercihi</td>
                  <td>1 yil</td>
                  <td>Tercih</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3>3.1 Cerez Kategorileri</h3>

          <div class="cookie-category">
            <h4>Zorunlu Cerezler</h4>
            <p>
              Bu cerezler sitenin duzgun calismasi icin gereklidir ve devre disi birakilamaz.
              Oturum yonetimi, guvenlik ve temel site islevleri icin kullanilir.
            </p>
          </div>

          <div class="cookie-category">
            <h4>Tercih Cerezleri</h4>
            <p>
              Bu cerezler tema, dil ve diger kisisel tercihlerinizi hatirlamak icin kullanilir.
              Devre disi birakirsaniz tercihleriniz her ziyarette sifirlanir.
            </p>
          </div>

          <div class="cookie-category">
            <h4>Analitik Cerezleri</h4>
            <p>
              Bu cerezler ziyaretci istatistiklerini toplamak ve site performansini olcmek
              icin kullanilir. Kisisel bilgi icermez, anonim veriler toplar.
            </p>
          </div>

          <div class="cookie-category">
            <h4>Pazarlama Cerezleri</h4>
            <p>
              Bu cerezler ilgi alanlariniza gore kisisellestirilmis icerik gostermek
              icin kullanilabilir. Su an aktif olarak kullanilmamaktadir.
            </p>
          </div>
        </section>

        <!-- Cerez Yonetimi -->
        <section class="policy-section">
          <h2>4. Cerez Tercihlerinizi Yonetme</h2>
          <p>
            Cerez tercihlerinizi istediginiz zaman degistirebilirsiniz:
          </p>
          <ul>
            <li>
              <strong>Site uzerinden:</strong> Asagidaki butonu kullanarak cerez
              ayarlarinizi yeniden yapilandirabilirsiniz.
            </li>
            <li>
              <strong>Tarayici ayarlarindan:</strong> Cogu modern tarayici cerezleri
              engelleme veya silme secenegi sunar.
            </li>
          </ul>

          <button class="btn btn-primary" @click="resetCookieConsent">
            Cerez Tercihlerimi Duzenle
          </button>
        </section>

        <!-- Veri Guvenligi -->
        <section class="policy-section">
          <h2>5. Veri Guvenligi</h2>
          <p>
            Verilerinizi korumak icin asagidaki onlemleri aliyoruz:
          </p>
          <ul>
            <li>SSL/TLS sifreleme ile guvenli veri iletimi</li>
            <li>Sifrelenmis veritabani depolama</li>
            <li>Duzenli guvenlik denetimleri</li>
            <li>CSRF ve XSS korumasi</li>
            <li>Rate limiting ile brute-force korumasi</li>
          </ul>
        </section>

        <!-- KVKK Haklari -->
        <section class="policy-section">
          <h2>6. KVKK Kapsamindaki Haklariniz</h2>
          <p>
            6698 sayili Kisisel Verilerin Korunmasi Kanunu kapsaminda asagidaki haklara
            sahipsiniz:
          </p>
          <ul>
            <li>Kisisel verilerinizin islenip islenmedigini ogrenme</li>
            <li>Islenmisse buna iliskin bilgi talep etme</li>
            <li>Islenme amacini ve bunlarin amacina uygun kullanilip kullanilmadigini ogrenme</li>
            <li>Yurt icinde veya yurt disinda aktarildigu ucuncu kisileri bilme</li>
            <li>Eksik veya yanlis islenmisse duzeltilmesini isteme</li>
            <li>KVKK'nin 7. maddesinde ongoerulen sartlar cercevesinde silinmesini isteme</li>
            <li>Islenen verilerin munhasiran otomatik sistemler vasitasiyla analiz edilmesi
                suretiyle aleyhinize bir sonucun ortaya cikmasina itiraz etme</li>
          </ul>
        </section>

        <!-- Iletisim -->
        <section class="policy-section">
          <h2>7. Iletisim</h2>
          <p>
            Gizlilik politikamiz veya kisisel verileriniz hakkinda sorulariniz icin
            bizimle iletisime gecebilirsiniz:
          </p>
          <ul>
            <li>E-posta: <a href="mailto:destek@agtr.com">destek@agtr.com</a></li>
            <li>Discord: <a href="https://discord.gg/agtr" target="_blank">discord.gg/agtr</a></li>
          </ul>
        </section>

        <!-- Degisiklikler -->
        <section class="policy-section">
          <h2>8. Politika Degisiklikleri</h2>
          <p>
            Bu gizlilik politikasini zaman zaman guncelleyebiliriz. Onemli degisiklikler
            yapildiginda sizi bilgilendirecegiz. Bu sayfayi duzenli olarak kontrol
            etmenizi oneririz.
          </p>
        </section>
      </div>

      <!-- Back Button -->
      <div class="back-section">
        <router-link to="/" class="back-link">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="19" y1="12" x2="5" y2="12"/>
            <polyline points="12 19 5 12 12 5"/>
          </svg>
          Ana Sayfaya Don
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCookies } from '@/composables/useCookies'

const { resetConsent } = useCookies()

function resetCookieConsent() {
  resetConsent()
  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.privacy-policy-page {
  min-height: 100vh;
  padding: 40px 20px 80px;
  background: var(--bg-primary, #0f0f1a);
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 800;
  color: var(--text-primary, #fff);
  margin: 0 0 12px 0;
}

.subtitle {
  color: var(--text-secondary, #9ca3af);
  font-size: 14px;
  margin: 0;
}

.policy-content {
  background: var(--card-bg, rgba(255, 255, 255, 0.03));
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.08));
  border-radius: 20px;
  padding: 40px;
}

.policy-section {
  margin-bottom: 40px;
}

.policy-section:last-child {
  margin-bottom: 0;
}

.policy-section h2 {
  font-size: 22px;
  font-weight: 700;
  color: #f97316;
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(249, 115, 22, 0.2);
}

.policy-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #fff);
  margin: 24px 0 12px 0;
}

.policy-section h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #fff);
  margin: 0 0 8px 0;
}

.policy-section p {
  font-size: 15px;
  color: var(--text-secondary, #9ca3af);
  line-height: 1.7;
  margin: 0 0 16px 0;
}

.policy-section ul {
  list-style: none;
  padding: 0;
  margin: 0 0 16px 0;
}

.policy-section ul li {
  position: relative;
  padding-left: 24px;
  margin-bottom: 10px;
  font-size: 15px;
  color: var(--text-secondary, #9ca3af);
  line-height: 1.6;
}

.policy-section ul li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 10px;
  width: 6px;
  height: 6px;
  background: #f97316;
  border-radius: 50%;
}

.policy-section a {
  color: #f97316;
  text-decoration: none;
}

.policy-section a:hover {
  text-decoration: underline;
}

/* Cookie Table */
.cookie-table {
  overflow-x: auto;
  margin: 20px 0;
}

.cookie-table table {
  width: 100%;
  border-collapse: collapse;
}

.cookie-table th,
.cookie-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.08));
}

.cookie-table th {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
  font-weight: 600;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.cookie-table td {
  font-size: 14px;
  color: var(--text-secondary, #9ca3af);
}

.cookie-table code {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  color: #fb923c;
}

/* Cookie Category */
.cookie-category {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.06));
  border-radius: 12px;
  padding: 16px 20px;
  margin: 12px 0;
}

.cookie-category h4 {
  color: #f97316;
}

.cookie-category p {
  margin: 0;
}

/* Button */
.btn {
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: #fff;
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #fb923c, #f97316);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(249, 115, 22, 0.3);
}

/* Back Section */
.back-section {
  margin-top: 40px;
  text-align: center;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary, #9ca3af);
  text-decoration: none;
  font-size: 14px;
  padding: 12px 24px;
  border-radius: 10px;
  transition: all 0.2s ease;
}

.back-link:hover {
  color: #f97316;
  background: rgba(249, 115, 22, 0.1);
}

/* Responsive */
@media (max-width: 640px) {
  .privacy-policy-page {
    padding: 24px 16px 60px;
  }

  .page-header h1 {
    font-size: 24px;
  }

  .policy-content {
    padding: 24px 20px;
  }

  .policy-section h2 {
    font-size: 18px;
  }

  .cookie-table th,
  .cookie-table td {
    padding: 8px 12px;
    font-size: 12px;
  }
}
</style>
