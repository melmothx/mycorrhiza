// import './assets/main.css'
import "./style.css"
import { createApp } from 'vue'
import i18nPlugin from './plugins/i18n'
import translations from "./i18n/translations.json";

import Collector from './Collector.vue'
import router from './router'

const app = createApp(Collector)

app.use(router)
app.use(i18nPlugin, {
    translations: translations,
})

app.mount('#app')
