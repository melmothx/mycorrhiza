import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import EntryView from '../views/EntryView.vue'
import ExclusionView from '../views/ExclusionView.vue'
import DashboardView from '../views/DashboardView.vue'
import PasswordResetView from '../views/PasswordResetView.vue'
import LibraryEditView from '../views/LibraryEditView.vue'
import LibraryView from '../views/LibraryView.vue'
import LibraryOverView from '../views/LibraryOverView.vue'
const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
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
            path: '/library-admin/:id',
            name: 'library_edit',
            component: LibraryEditView,
        },
        {
            path: '/library/:id/entries',
            redirect: to => {
                return { name: 'search', query: { filter_library: to.params.id } }
            },
        },
        {
            path: '/libraries/:id',
            name: 'library_view',
            component: LibraryView,
        },
        {
            path: '/libraries',
            name: 'library_overview',
            component: LibraryOverView,
        },
    ]
})

export default router

