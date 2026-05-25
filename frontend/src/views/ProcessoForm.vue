<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Select from 'primevue/select'
import Message from 'primevue/message'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const tipos = ref([])
const setores = ref([])

const form = ref({
  nome_cliente: '',
  cpf_cnpj: '',
  numero_contrato: '',
  tipo_processo: '',
  setor_responsavel: '',
  status: 'Disponível'
})

const fetchConfig = async () => {
  try {
    const [tiposRes, setoresRes] = await Promise.all([
      api.get('/processos/tipos'),
      api.get('/processos/setores')
    ])
    tipos.value = tiposRes.data
    setores.value = setoresRes.data
  } catch (err) {
    console.error('Erro ao buscar configurações', err)
  }
}

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  try {
    await api.post('/processos/cadastrar', form.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erro ao cadastrar processo'
  } finally {
    loading.value = false
  }
}

onMounted(fetchConfig)
</script>

<template>
  <div class="p-6 max-w-2xl mx-auto">
    <div class="mb-6 flex items-center gap-4">
      <Button icon="pi pi-arrow-left" rounded text @click="router.back()" />
      <h1 class="text-2xl font-bold">Cadastrar Novo Processo</h1>
    </div>

    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
      <form @submit.prevent="handleSubmit" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="flex flex-col gap-2 md:col-span-2">
          <label for="nome_cliente" class="font-semibold">Nome do Cliente</label>
          <InputText id="nome_cliente" v-model="form.nome_cliente" required />
        </div>

        <div class="flex flex-col gap-2">
          <label for="cpf_cnpj" class="font-semibold">CPF/CNPJ</label>
          <InputText id="cpf_cnpj" v-model="form.cpf_cnpj" required />
        </div>

        <div class="flex flex-col gap-2">
          <label for="numero_contrato" class="font-semibold">Número do Contrato</label>
          <InputText id="numero_contrato" v-model="form.numero_contrato" required />
        </div>

        <div class="flex flex-col gap-2">
          <label for="tipo_processo" class="font-semibold">Tipo de Processo</label>
          <Select id="tipo_processo" v-model="form.tipo_processo" :options="tipos" optionLabel="nome" optionValue="nome" placeholder="Selecione..." required />
        </div>

        <div class="flex flex-col gap-2">
          <label for="setor_responsavel" class="font-semibold">Setor Responsável</label>
          <Select id="setor_responsavel" v-model="form.setor_responsavel" :options="setores" optionLabel="nome" optionValue="nome" placeholder="Selecione..." required />
        </div>

        <div class="md:col-span-2">
          <Message v-if="error" severity="error">{{ error }}</Message>
        </div>

        <div class="md:col-span-2 flex justify-end gap-3 mt-4">
          <Button label="Cancelar" severity="secondary" @click="router.back()" />
          <Button type="submit" label="Salvar Processo" :loading="loading" />
        </div>
      </form>
    </div>
  </div>
</template>
