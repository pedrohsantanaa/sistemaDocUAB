<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const email = ref('')
const senha = ref('')
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
  loading.ref = true
  error.value = ''
  const success = await auth.login(email.value, senha.value)
  loading.value = false
  
  if (success) {
    router.push('/')
  } else {
    error.value = 'E-mail ou senha incorretos'
  }
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
    <div class="w-full max-w-md p-8 bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-primary-600">SistemaDocUAB</h1>
        <p class="text-gray-600 dark:text-gray-400">Entre com suas credenciais</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div class="flex flex-col gap-2">
          <label for="email" class="font-semibold">E-mail</label>
          <InputText id="email" v-model="email" type="email" placeholder="seu@email.com" required class="w-full" />
        </div>

        <div class="flex flex-col gap-2">
          <label for="senha" class="font-semibold">Senha</label>
          <Password id="senha" v-model="senha" :feedback="false" toggleMask required class="w-full" :inputStyle="{ width: '100%' }" />
        </div>

        <Message v-if="error" severity="error" variant="simple">{{ error }}</Message>

        <Button type="submit" label="Entrar" :loading="loading" class="w-full" />
      </form>
    </div>
  </div>
</template>
