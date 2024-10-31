import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import EntryView from '../views/EntryView.vue'
import ExclusionView from '../views/ExclusionView.vue'
import DashboardView from '../views/DashboardView.vue'
import PasswordResetView from '../views/PasswordResetView.vue'
import LibraryEditView from '../views/LibraryEditView.vue'
import LibraryView from '../views/LibraryView.vue'
import LibraryOverView from '../views/LibraryOverView.vue'
import AgentOverView from '../views/AgentOverView.vue'
import PageView from '../views/PageView.vue'
const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    scrollBehavior(to, from, savedPosition) {
        if (to.hash) {
            return new Promise((resolve, reject) => {
                setTimeout(() => {
                    resolve({ el: to.hash })
                }, 500)
            })
        }
    },
    routes: [
        {
            name: 'home',
            path:  '/',
            redirect: { name: 'search' },
        },
        {
            path: '/search',
            name: 'search',
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
        {
            path: '/reset-password/:username/:token',
            name: 'reset_password',
            component: PasswordResetView,
        },
        {
            path: '/library/admin/:id',
            name: 'library_edit',
            component: LibraryEditView,
        },
        {
            path: '/library/entries/:id',
            redirect: to => {
                return { name: 'search', query: { filter_library: to.params.id } }
            },
        },
        {
            path: '/library/author/:id',
            redirect: to => {
                return { name: 'search', query: { filter_creator: to.params.id } }
            },
        },
        {
            path: '/library/details/:id',
            name: 'library_view',
            component: LibraryView,
        },
        {
            path: '/library',
            name: 'library_overview',
            component: LibraryOverView,
        },
        {
            path: '/agent',
            name: 'agent_overview',
            component: AgentOverView,
        },
        {
            path: '/page/:id',
            name: 'page_view',
            component: PageView,
        },
    ]
})

export default router

