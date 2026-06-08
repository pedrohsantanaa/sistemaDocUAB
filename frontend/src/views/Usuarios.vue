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
import ToggleSwitch from 'primevue/toggleswitch'

const usuarios = ref([])
const setores = ref([])
const loading = ref(false)
const showDialog = ref(false)
const isEditing = ref(false)
const selectedUserId = ref(null)
const error = ref('')
const saving = ref(false)

const form = ref({
  nome: '',
  email: '',
  senha: '',
  cargo: 'usuario',
  setor: null,
  ativo: true
})

const cargos = [
  { label: 'Administrador', value: 'admin' },
  { label: 'Usuário', value: 'usuario' }
]

const fetchConfig = async () => {
  try {
    const response = await api.get('/configuracoes/setores')
    setores.value = response.data
  } catch (err) {
    console.error('Erro ao buscar setores', err)
  }
}

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

const abrirNovo = () => {
  isEditing.value = false
  selectedUserId.value = null
  form.value = { nome: '', email: '', senha: '', cargo: 'usuario', setor: null, ativo: true }
  showDialog.value = true
}

const abrirEdicao = (usuario) => {
  isEditing.value = true
  selectedUserId.value = usuario.id
  form.value = { 
    nome: usuario.nome, 
    email: usuario.email, 
    senha: '', 
    cargo: usuario.cargo, 
    setor: usuario.setor,
    ativo: usuario.ativo
  }
  showDialog.value = true
}

const handleSave = async () => {
  saving.value = true
  error.value = ''
  try {
    if (isEditing.value) {
      const payload = { ...form.value }
      if (!payload.senha) delete payload.senha
      await api.put(`/usuarios/${selectedUserId.value}`, payload)
    } else {
      await api.post('/usuarios/cadastrar', form.value)
    }
    showDialog.value = false
    fetchUsuarios()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erro ao salvar usuário'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchUsuarios()
  fetchConfig()
})
</script>

<template>
  <div class="p-6 space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold">Gerenciar Usuários</h1>
      <Button label="Novo Usuário" icon="pi pi-plus" @click="abrirNovo" />
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <DataTable :value="usuarios" :loading="loading" paginator :rows="10">
        <Column field="nome" header="Nome" sortable></Column>
        <Column field="email" header="E-mail" sortable></Column>
        <Column field="setor" header="Setor" sortable></Column>
        <Column field="cargo" header="Cargo">
          <template #body="slotProps">
            <Tag :value="slotProps.data.cargo" :severity="slotProps.data.cargo === 'admin' ? 'danger' : 'info'" />
          </template>
        </Column>
        <Column field="ativo" header="Status">
          <template #body="slotProps">
            <Tag :value="slotProps.data.ativo ? 'Ativo' : 'Inativo'" :severity="slotProps.data.ativo ? 'success' : 'warn'" />
          </template>
        </Column>
        <Column header="Ações" class="w-24">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" rounded text severity="secondary" @click="abrirEdicao(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <Dialog v-model:visible="showDialog" :header="isEditing ? 'Editar Usuário' : 'Cadastrar Usuário'" modal class="w-full max-w-md">
      <form @submit.prevent="handleSave" class="flex flex-col gap-4 mt-2">
        <div class="flex flex-col gap-2">
          <label class="font-semibold">Nome Completo</label>
          <InputText v-model="form.nome" required />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-semibold">E-mail</label>
          <InputText v-model="form.email" type="email" required />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-semibold">{{ isEditing ? 'Nova Senha (deixe vazio para manter)' : 'Senha Inicial' }}</label>
          <InputText v-model="form.senha" type="password" :required="!isEditing" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-semibold">Cargo</label>
          <Select v-model="form.cargo" :options="cargos" optionLabel="label" optionValue="value" required />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-semibold">Setor</label>
          <Select v-model="form.setor" :options="setores" optionLabel="nome" optionValue="nome" placeholder="Selecione o setor..." />
        </div>

        <div v-if="isEditing" class="flex items-center gap-3 py-2">
          <label class="font-semibold">Usuário Ativo</label>
          <ToggleSwitch v-model="form.ativo" />
        </div>
        
        <Message v-if="error" severity="error" variant="simple">{{ error }}</Message>

        <div class="flex justify-end gap-2 mt-4">
          <Button label="Cancelar" text severity="secondary" @click="showDialog = false" />
          <Button type="submit" :label="isEditing ? 'Salvar Alterações' : 'Cadastrar'" :loading="saving" />
        </div>
      </form>
    </Dialog>
  </div>
</template>
