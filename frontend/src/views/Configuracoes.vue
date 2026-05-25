<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Message from 'primevue/message'

const tipos = ref([])
const setores = ref([])
const statusLista = ref([])
const loadingTipos = ref(false)
const loadingSetores = ref(false)
const loadingStatus = ref(false)

const showDialogTipo = ref(false)
const showDialogSetor = ref(false)
const showDialogStatus = ref(false)
const editingItem = ref(null)
const itemName = ref('')
const error = ref('')

const fetchAll = async () => {
  loadingTipos.value = true
  loadingSetores.value = true
  loadingStatus.value = true
  try {
    const [t, s, st] = await Promise.all([
      api.get('/configuracoes/tipos'), 
      api.get('/configuracoes/setores'),
      api.get('/configuracoes/status')
    ])
    tipos.value = t.data
    setores.value = s.data
    statusLista.value = st.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingTipos.value = false
    loadingSetores.value = false
    loadingStatus.value = false
  }
}

const saveTipo = async () => {
  error.value = ''
  try {
    if (editingItem.value) {
      await api.put(`/configuracoes/tipos/${editingItem.value.id}`, { nome: itemName.value })
    } else {
      await api.post('/configuracoes/tipos', { nome: itemName.value })
    }
    showDialogTipo.value = false
    fetchAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erro ao salvar'
  }
}

const deleteTipo = async (id) => {
  if (confirm('Tem certeza?')) {
    await api.delete(`/configuracoes/tipos/${id}`)
    fetchAll()
  }
}

const saveSetor = async () => {
  error.value = ''
  try {
    if (editingItem.value) {
      await api.put(`/configuracoes/setores/${editingItem.value.id}`, { nome: itemName.value })
    } else {
      await api.post('/configuracoes/setores', { nome: itemName.value })
    }
    showDialogSetor.value = false
    fetchAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erro ao salvar'
  }
}

const deleteSetor = async (id) => {
  if (confirm('Tem certeza?')) {
    await api.delete(`/configuracoes/setores/${id}`)
    fetchAll()
  }
}

const saveStatus = async () => {
  error.value = ''
  try {
    if (editingItem.value) {
      await api.put(`/configuracoes/status/${editingItem.value.id}`, { nome: itemName.value })
    } else {
      await api.post('/configuracoes/status', { nome: itemName.value })
    }
    showDialogStatus.value = false
    fetchAll()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erro ao salvar'
  }
}

const deleteStatus = async (id) => {
  if (confirm('Tem certeza?')) {
    await api.delete(`/configuracoes/status/${id}`)
    fetchAll()
  }
}

onMounted(fetchAll)
</script>

<template>
  <div class="p-6 space-y-8">
    <h1 class="text-2xl font-bold">Configurações do Sistema</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Tipos de Processo -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow space-y-4">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold">Tipos de Processo</h2>
          <Button icon="pi pi-plus" label="Novo" size="small" @click="editingItem = null; itemName = ''; showDialogTipo = true" />
        </div>
        <DataTable :value="tipos" :loading="loadingTipos" size="small">
          <Column field="nome" header="Nome"></Column>
          <Column header="Ações" class="w-24">
            <template #body="slotProps">
              <div class="flex gap-1">
                <Button icon="pi pi-pencil" text rounded size="small" @click="editingItem = slotProps.data; itemName = slotProps.data.nome; showDialogTipo = true" />
                <Button icon="pi pi-trash" text rounded size="small" severity="danger" @click="deleteTipo(slotProps.data.id)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- Setores -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow space-y-4">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold">Setores</h2>
          <Button icon="pi pi-plus" label="Novo" size="small" @click="editingItem = null; itemName = ''; showDialogSetor = true" />
        </div>
        <DataTable :value="setores" :loading="loadingSetores" size="small">
          <Column field="nome" header="Nome"></Column>
          <Column header="Ações" class="w-24">
            <template #body="slotProps">
              <div class="flex gap-1">
                <Button icon="pi pi-pencil" text rounded size="small" @click="editingItem = slotProps.data; itemName = slotProps.data.nome; showDialogSetor = true" />
                <Button icon="pi pi-trash" text rounded size="small" severity="danger" @click="deleteSetor(slotProps.data.id)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- Status de Processo -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow space-y-4">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold">Status de Processo</h2>
          <Button icon="pi pi-plus" label="Novo" size="small" @click="editingItem = null; itemName = ''; showDialogStatus = true" />
        </div>
        <DataTable :value="statusLista" :loading="loadingStatus" size="small">
          <Column field="nome" header="Nome"></Column>
          <Column header="Ações" class="w-24">
            <template #body="slotProps">
              <div class="flex gap-1">
                <Button icon="pi pi-pencil" text rounded size="small" @click="editingItem = slotProps.data; itemName = slotProps.data.nome; showDialogStatus = true" />
                <Button icon="pi pi-trash" text rounded size="small" severity="danger" @click="deleteStatus(slotProps.data.id)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- Dialog Tipo -->
    <Dialog v-model:visible="showDialogTipo" :header="editingItem ? 'Editar Tipo' : 'Novo Tipo'" modal>
      <div class="flex flex-col gap-4 w-80">
        <div class="flex flex-col gap-2">
          <label for="tipo_nome" class="font-semibold">Nome</label>
          <InputText id="tipo_nome" v-model="itemName" class="w-full" autofocus />
        </div>
        <Message v-if="error" severity="error" variant="simple">{{ error }}</Message>
        <div class="flex justify-end gap-2">
          <Button label="Cancelar" text severity="secondary" @click="showDialogTipo = false" />
          <Button label="Salvar" @click="saveTipo" />
        </div>
      </div>
    </Dialog>

    <!-- Dialog Setor -->
    <Dialog v-model:visible="showDialogSetor" :header="editingItem ? 'Editar Setor' : 'Novo Setor'" modal>
      <div class="flex flex-col gap-4 w-80">
        <div class="flex flex-col gap-2">
          <label for="setor_nome" class="font-semibold">Nome</label>
          <InputText id="setor_nome" v-model="itemName" class="w-full" autofocus />
        </div>
        <Message v-if="error" severity="error" variant="simple">{{ error }}</Message>
        <div class="flex justify-end gap-2">
          <Button label="Cancelar" text severity="secondary" @click="showDialogSetor = false" />
          <Button label="Salvar" @click="saveSetor" />
        </div>
      </div>
    </Dialog>

    <!-- Dialog Status -->
    <Dialog v-model:visible="showDialogStatus" :header="editingItem ? 'Editar Status' : 'Novo Status'" modal>
      <div class="flex flex-col gap-4 w-80">
        <div class="flex flex-col gap-2">
          <label for="status_nome" class="font-semibold">Nome</label>
          <InputText id="status_nome" v-model="itemName" class="w-full" autofocus />
        </div>
        <Message v-if="error" severity="error" variant="simple">{{ error }}</Message>
        <div class="flex justify-end gap-2">
          <Button label="Cancelar" text severity="secondary" @click="showDialogStatus = false" />
          <Button label="Salvar" @click="saveStatus" />
        </div>
      </div>
    </Dialog>
  </div>
</template>
