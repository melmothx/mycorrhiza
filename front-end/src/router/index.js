import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import EntryView from '../views/EntryView.vue'
import ExclusionView from '../views/ExclusionView.vue'
import DashboardView from '../views/DashboardView.vue'
const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView,
        },
        {
            path: '/entry/:id',
            name: 'entry',
            component: EntryView,
        },
        {
            path: '/exclusions',
            name: 'exclusions',
            component: ExclusionView,
        },
        {
            path: '/dashboard/:type',
            name: 'dashboard',
            component: DashboardView,
        },
    ]
})

export default router

