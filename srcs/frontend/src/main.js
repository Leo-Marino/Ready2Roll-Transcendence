import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './vue/App.vue'
import router from './router'
import { t } from './i18n'

const app = createApp(App)
app.config.globalProperties.$t = t
app.use(createPinia())
app.use(router)
app.mount('#app')
