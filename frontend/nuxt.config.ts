export default defineNuxtConfig({
  modules: ['@nuxt/ui', '@pinia/nuxt', 'pinia-plugin-persistedstate/nuxt', '@nuxt/eslint'],
  devtools: { enabled: true },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '/auth',
      s3Base: process.env.NUXT_PUBLIC_S3_BASE || '/s3'
    }
  },
  dir: {
    public: '../public'
  },

  srcDir: 'app/',
  compatibilityDate: '2024-09-22',

  nitro: {
    routeRules: {
      '/auth/**': { proxy: 'http://auth_service:8000/**' }
    }
  },

  telemetry: false,

  eslint: {
    config: {
      stylistic: true
    }
  }
})
