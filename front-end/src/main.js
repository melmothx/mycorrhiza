// import './assets/main.css'
import "./style.css"
import { createApp } from 'vue'

import Collector from './Collector.vue'
import router from './router'

const app = createApp(Collector)
app.use(router)
app.mount('#app')
