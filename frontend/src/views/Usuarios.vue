<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

const usuarios = ref([])
const loading = ref(false)
const showDialog = ref(false)
const error = ref('')
const saving = ref(false)

const form = ref({
  nome: '',
  email: '',
  senha: '',
  cargo: 'usuario'
})

const cargos = [
  { label: 'Administrador', value: 'admin' },
  { label: 'Usuário', value: 'usuario' }
]

const fetchUsuarios = async () => {
  loading.value = true
  try {
    const response = await api.get('/usuarios/')
    usuarios.value = response.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  saving.value = true
  error.value = ''
  try {
    await api.post('/usuarios/cadastrar', form.value)
    showDialog.value = false
    fetchUsuarios()
    form.value = { nome: '', email: '', senha: '', cargo: 'usuario' }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erro ao cadastrar usuário'
  } finally {
    saving.value = false
  }
}

onMounted(fetchUsuarios)
</script>

<template>
  <div class="p-6 space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold">Gerenciar Usuários</h1>
      <Button label="Novo Usuário" icon="pi pi-plus" @click="showDialog = true" />
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <DataTable :value="usuarios" :loading="loading" paginator :rows="10">
        <Column field="nome" header="Nome" sortable></Column>
        <Column field="email" header="E-mail" sortable></Column>
        <Column field="cargo" header="Cargo">
          <template #body="slotProps">
            <Tag :value="slotProps.data.cargo" :severity="slotProps.data.cargo === 'admin' ? 'danger' : 'info'" />
          </template>
        </Column>
        <Column field="ativo" header="Status">
          <template #body="slotProps">
            <i class="pi" :class="slotProps.data.ativo ? 'pi-check-circle text-green-500' : 'pi-times-circle text-red-500'"></i>
          </template>
        </Column>
      </DataTable>
    </div>

    <Dialog v-model:visible="showDialog" header="Cadastrar Usuário" modal class="w-full max-w-md">
      <form @submit.prevent="handleSave" class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-semibold">Nome Completo</label>
          <InputText v-model="form.nome" required />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-semibold">E-mail</label>
          <InputText v-model="form.email" type="email" required />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-semibold">Senha Inicial</label>
          <InputText v-model="form.senha" type="password" required />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-semibold">Cargo</label>
          <Select v-model="form.cargo" :options="cargos" optionLabel="label" optionValue="value" required />
        </div>
        
        <Message v-if="error" severity="error" variant="simple">{{ error }}</Message>

        <div class="flex justify-end gap-2 mt-4">
          <Button label="Cancelar" text severity="secondary" @click="showDialog = false" />
          <Button type="submit" label="Cadastrar" :loading="saving" />
        </div>
      </form>
    </Dialog>
  </div>
</template>
