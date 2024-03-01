// import './assets/main.css'
import "./style.css"
import { createApp } from 'vue'
import { createGettext } from "vue3-gettext";
import translations from "./i18n/translations.json";

import Collector from './Collector.vue'
import router from './router'

const app = createApp(Collector)

app.use(router)
app.use(createGettext({
    availableLanguages: {
        en: "English",
        it: "Italiano",
    },
    defaultLanguage: "en",
    translations: translations,
}))

app.mount('#app')
