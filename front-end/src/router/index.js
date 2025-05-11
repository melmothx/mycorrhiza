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
import BookBuilderView from '../views/BookBuilderView.vue'
import CoverBuilderView from '../views/CoverBuilderView.vue'
const MapView = () => import('../views/MapView.vue')

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
            name: 'map',
            path: '/map',
            component: MapView,
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
                return { name: 'search',
                         query: {
                             query: "library:" + to.params.id,
                             filter_library: to.params.id,
                             sort_by: "title_asc",
                         }
                       }
            },
        },
        {
            path: '/library/author/:id',
            redirect: to => {
                return { name: 'search',
                         query: {
                             query: "creator:" + to.params.id,
                             // filter_creator: to.params.id,
                             sort_by: "title_asc",
                         }
                       }
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
        {
            path: '/bookbuilder',
            name: 'bookbuilder',
            component: BookBuilderView,
        },
        {
            path: '/coverbuilder',
            name: 'coverbuilder',
            component: CoverBuilderView,
        },

    ]
})

export default router

