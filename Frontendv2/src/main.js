import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'

createApp(App).mount('#app')
createApp(App).use(router).mount('#app')
createApp(App).use(createPinia()).mount('#app')