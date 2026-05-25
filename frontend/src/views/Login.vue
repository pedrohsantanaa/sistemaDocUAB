<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import logoUrl from '../assets/logo.png'

const email = ref('')
const senha = ref('')
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const success = await auth.login(email.value, senha.value)
    if (success) {
      router.push('/')
    } else {
      error.value = 'E-mail ou senha incorretos'
    }
  } catch (err) {
    error.value = 'Erro ao conectar com o servidor'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-primary-950 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]">
    <div class="w-full max-w-md p-10 bg-white rounded-2xl shadow-2xl border-t-8 border-accent-500">
      <div class="text-center mb-10">
        <img :src="logoUrl" alt="Fomento Tocantins" class="h-20 mx-auto mb-6" />
        <h1 class="text-2xl font-bold text-primary-800 uppercase tracking-wider">Sistema de Gestão Documental</h1>
        <p class="text-gray-500 mt-2 font-medium">Agência de Fomento do Estado do Tocantins</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div class="flex flex-col gap-2">
          <label for="email" class="font-bold text-primary-900 text-sm uppercase">E-mail Institucional</label>
          <InputText id="email" v-model="email" type="email" placeholder="usuario@fomento.to.gov.br" required class="w-full p-3 border-gray-300 focus:border-primary-500" />
        </div>

        <div class="flex flex-col gap-2">
          <label for="senha" class="font-bold text-primary-900 text-sm uppercase">Senha de Acesso</label>
          <Password id="senha" v-model="senha" :feedback="false" toggleMask required class="w-full" :inputStyle="{ width: '100%', padding: '0.75rem' }" />
        </div>

        <Message v-if="error" severity="error" class="mb-4">{{ error }}</Message>

        <Button type="submit" label="ACESSAR SISTEMA" :loading="loading" class="w-full py-4 font-bold text-lg bg-primary-700 hover:bg-primary-800 border-none shadow-lg transition-all" />
      </form>
      
      <div class="mt-8 text-center">
        <p class="text-xs text-gray-400 uppercase tracking-widest font-semibold">© 2026 Agência de Fomento - TO</p>
      </div>
    </div>
  </div>
</template>
