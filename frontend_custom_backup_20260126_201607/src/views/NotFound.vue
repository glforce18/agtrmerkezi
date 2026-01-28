<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="text-center">
      <div class="text-9xl font-lambda font-bold neon-orange mb-4">404</div>
      <h1 class="text-3xl font-lambda font-bold text-text-primary mb-4">
        SAYFA BULUNAMADI
      </h1>
      <p class="text-text-secondary mb-8">
        Aradığınız sayfa mevcut değil veya taşınmış olabilir.
      </p>
      <router-link
        to="/"
        class="inline-block px-8 py-3 bg-lambda-gradient text-cyber-black font-lambda font-bold rounded hover:shadow-neon-orange transition-all duration-300"
      >
        ANA SAYFAYA DÖN
      </router-link>
    </div>
  </div>
</template>
