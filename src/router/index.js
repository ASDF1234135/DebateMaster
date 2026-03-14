import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Overview',
    component: () => import('../views/OverviewView.vue'),
    meta: { title: 'Overview - Debate Master' },
  },
  {
    path: '/start',
    name: 'GetStarted',
    component: () => import('../views/DebateLabView.vue'),
    meta: { title: 'Get Started - Debate Master' },
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/HistoryView.vue'),
    meta: { title: 'History - Debate Master' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = to.meta.title || 'Debate Master'
})

export default router
