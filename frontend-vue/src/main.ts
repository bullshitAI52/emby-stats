import './assets/theme.css'
import './assets/page-styles.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import vuetify from './plugins/vuetify'

import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(vuetify)

// 初始化主题
const savedTheme = localStorage.getItem('theme')
if (savedTheme && (savedTheme === 'dark' || savedTheme === 'light')) {
  vuetify.theme.global.name.value = savedTheme
}

app.mount('#app')
