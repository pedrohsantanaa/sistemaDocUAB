<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Button from 'primevue/button'
import logoUrl from '../assets/logo.png'

const auth = useAuthStore()
const router = useRouter()

const menuItems = [
  { label: 'Dashboard', icon: 'pi pi-home', to: '/' },
  { label: 'Relatórios', icon: 'pi pi-chart-bar', to: '/relatorios', admin: true },
  { label: 'Configurações', icon: 'pi pi-cog', to: '/configuracoes', admin: true },
  { label: 'Usuários', icon: 'pi pi-users', to: '/usuarios', admin: true },
]

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Sidebar -->
    <aside class="w-[280px] bg-primary-900 shadow-xl flex flex-col fixed h-screen z-[1000] border-r border-primary-800">
      <div class="p-8 text-center border-b border-primary-800">
        <img :src="logoUrl" alt="Fomento TO" class="h-16 mx-auto mb-4 brightness-0 invert" />
        <h1 class="text-xs font-bold text-white uppercase tracking-widest opacity-80">
          Gestão Documental
        </h1>
      </div>
      
      <nav class="flex-1 px-4 py-6 space-y-2">
        <template v-for="item in menuItems" :key="item.to">
          <router-link 
            v-if="!item.admin || auth.isAdmin"
            :to="item.to" 
            class="flex items-center gap-3 py-3 px-4 rounded-lg transition-all text-white/60 hover:text-white hover:bg-white/10"
            active-class="bg-white/10 text-white font-semibold border-l-4 border-accent-500 rounded-l-none"
          >
            <i :class="item.icon" class="w-5 text-center" />
            <span>{{ item.label }}</span>
          </router-link>
        </template>
      </nav>

      <div class="p-4 border-t border-white/10">
        <Button label="Sair do Sistema" icon="pi pi-sign-out" severity="danger" text class="w-full justify-start text-white/70 hover:text-white" @click="handleLogout" />
      </div>
    </aside>

    <!-- Main Content Wrapper -->
    <div class="flex-1 ml-[280px] flex flex-col min-h-screen">
      <!-- Topbar -->
      <header class="h-[70px] bg-white shadow-sm flex items-center justify-between px-8 sticky top-0 z-[999] border-b border-gray-100">
        <div class="flex items-center gap-4">
          <div class="bg-accent-500 w-1.5 h-8 rounded-full"></div>
          <div class="text-primary-900 font-bold uppercase tracking-tight text-lg">
            Agência de Fomento do Tocantins
          </div>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-right">
            <p class="text-sm font-bold text-gray-800">{{ auth.user?.nome }}</p>
            <p class="text-xs text-primary-600 font-bold uppercase">{{ auth.user?.cargo }}</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-900 font-bold border border-primary-200">
            {{ auth.user?.nome?.charAt(0) }}
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="p-8 flex-1">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Transição suave para os links */
.router-link-active {
  position: relative;
}
</style>
