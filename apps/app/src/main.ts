import { createApp } from 'vue'

import './styles/main.css'

import App from './app/App.vue'
import router from './app/core/routes.ts'

import ui from '@nuxt/ui/vue-plugin'
import { VueQueryPlugin } from '@tanstack/vue-query'

const app = createApp(App)

app.use(router)
app.use(VueQueryPlugin)
app.use(ui)
app.mount('#app')
