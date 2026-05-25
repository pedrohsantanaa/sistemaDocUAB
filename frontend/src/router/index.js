import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/Dashboard.vue')
    },
    {
      path: '/processos/cadastrar',
      name: 'processos-cadastrar',
      component: () => import('../views/ProcessoForm.vue')
    },
    {
      path: '/processos/:id/historico',
      name: 'processos-historico',
      component: () => import('../views/ProcessoHistorico.vue')
    },
    {
      path: '/relatorios',
      name: 'relatorios',
      component: () => import('../views/Relatorios.vue'),
      meta: { admin: true }
    },
    {
      path: '/configuracoes',
      name: 'configuracoes',
      component: () => import('../views/Configuracoes.vue'),
      meta: { admin: true }
    },
    {
      path: '/usuarios',
      name: 'usuarios',
      component: () => import('../views/Usuarios.vue'),
      meta: { admin: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  
  if (!to.meta.public && !auth.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.meta.admin && auth.user?.cargo !== 'admin') {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
