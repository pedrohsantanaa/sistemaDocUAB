<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import { useRouter } from 'vue-router'

const processos = ref([])
const stats = ref({})
const loading = ref(true)
const busca = ref('')
const statusFiltro = ref(null)
const router = useRouter()

// Modals State
const showRetiradaDialog = ref(false)
const showDevolucaoDialog = ref(false)
const selectedProcesso = ref(null)
const setores = ref([])
const submetendo = ref(false)

const formRetirada = ref({
  setor_destino: '',
  observacoes: ''
})

const formDevolucao = ref({
  novo_status_processo: 'Disponível'
})

const statusOpcoes = [
  { label: 'Disponível', value: 'Disponível' },
  { label: 'Pendente', value: 'Pendente' },
  { label: 'Liquidado', value: 'Liquidado' },
  { label: 'Arquivado', value: 'Arquivado' }
]

const fetchProcessos = async () => {
  loading.value = true
  try {
    const params = {}
    if (busca.value) params.busca = busca.value
    if (statusFiltro.value) params.status = statusFiltro.value
    
    const response = await api.get('/processos/', { params })
    processos.value = response.data.processos
    stats.value = response.data.stats
  } catch (error) {
    console.error('Erro ao buscar processos', error)
  } finally {
    loading.value = false
  }
}

const fetchConfig = async () => {
  try {
    const response = await api.get('/configuracoes/setores')
    setores.value = response.data
  } catch (err) {
    console.error('Erro ao buscar setores', err)
  }
}

const abrirRetirada = (processo) => {
  selectedProcesso.value = processo
  formRetirada.value = { setor_destino: '', observacoes: '' }
  showRetiradaDialog.value = true
}

const abrirDevolucao = (processo) => {
  selectedProcesso.value = processo
  formDevolucao.value = { novo_status_processo: 'Disponível' }
  showDevolucaoDialog.value = true
}

const confirmarRetirada = async () => {
  if (!formRetirada.value.setor_destino) {
    alert('Selecione o setor de destino')
    return
  }
  submetendo.value = true
  try {
    await api.post('/processos/movimentar/retirada', null, {
      params: {
        processo_id: selectedProcesso.value.id,
        setor_destino: formRetirada.value.setor_destino,
        observacoes: formRetirada.value.observacoes
      }
    })
    showRetiradaDialog.value = false
    fetchProcessos()
  } catch (error) {
    alert(error.response?.data?.detail || 'Erro ao registrar retirada')
  } finally {
    submetendo.value = false
  }
}

const confirmarDevolucao = async () => {
  submetendo.value = true
  try {
    // Buscar a movimentação ativa para o processo
    const histRes = await api.get(`/processos/${selectedProcesso.value.id}/historico`)
    const movimentacaoAtiva = histRes.data.historico.find(m => !m.data_devolucao)
    
    if (!movimentacaoAtiva) {
      throw new Error('Não foi encontrada uma movimentação ativa para este processo.')
    }

    await api.post('/processos/movimentar/devolucao', {
      movimentacao_id: movimentacaoAtiva.id,
      novo_status_processo: formDevolucao.value.novo_status_processo
    })
    showDevolucaoDialog.value = false
    fetchProcessos()
  } catch (error) {
    alert(error.response?.data?.detail || error.message || 'Erro ao registrar devolução')
  } finally {
    submetendo.value = false
  }
}

const getStatusClass = (status) => {
  switch (status) {
    case 'Disponível': return 'bg-green-100 text-green-800'
    case 'Em Posse': return 'bg-amber-100 text-amber-800'
    case 'Pendente': return 'bg-red-100 text-red-800'
    default: return 'bg-blue-100 text-blue-800'
  }
}

onMounted(() => {
  fetchProcessos()
  fetchConfig()
})
</script>

<template>
  <div class="space-y-8">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Processos Cadastrados</h1>
      <Button label="Cadastrar Processo" icon="pi pi-plus" class="p-button-primary shadow-md" @click="router.push('/processos/cadastrar')" />
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
        <div class="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600 text-xl">
          <i class="pi pi-file"></i>
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-800">{{ stats.total || 0 }}</p>
          <p class="text-xs text-gray-500 uppercase font-semibold">Total Geral</p>
        </div>
      </div>
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
        <div class="w-12 h-12 rounded-lg bg-green-50 flex items-center justify-center text-green-600 text-xl">
          <i class="pi pi-check-circle"></i>
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-800">{{ stats.disponiveis || 0 }}</p>
          <p class="text-xs text-gray-500 uppercase font-semibold">Disponíveis</p>
        </div>
      </div>
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
        <div class="w-12 h-12 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600 text-xl">
          <i class="pi pi-sign-out"></i>
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-800">{{ stats.em_posse || 0 }}</p>
          <p class="text-xs text-gray-500 uppercase font-semibold">Em Posse</p>
        </div>
      </div>
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
        <div class="w-12 h-12 rounded-lg bg-red-50 flex items-center justify-center text-red-600 text-xl">
          <i class="pi pi-exclamation-circle"></i>
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-800">{{ stats.pendentes || 0 }}</p>
          <p class="text-xs text-gray-500 uppercase font-semibold">Pendentes</p>
        </div>
      </div>
    </div>

    <!-- Main Content Card -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <!-- Search/Filter Header -->
      <div class="p-6 border-b border-gray-50 flex gap-4 items-center bg-gray-50/50">
        <div class="relative flex-1">
          <i class="pi pi-search absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
          <InputText v-model="busca" placeholder="Buscar por cliente, contrato ou CPF..." class="pl-12 w-full border-gray-200" @keyup.enter="fetchProcessos" />
        </div>
        <Button label="Buscar" icon="pi pi-search" class="px-6" @click="fetchProcessos" />
      </div>

      <!-- Data Table -->
      <DataTable :value="processos" :loading="loading" paginator :rows="10" stripedRows class="p-datatable-sm">
        <Column field="numero_contrato" header="Nº Contrato" sortable class="font-bold text-primary-900"></Column>
        <Column field="nome_cliente" header="Cliente" sortable></Column>
        <Column field="tipo_processo" header="Tipo de Processo"></Column>
        <Column field="setor_responsavel" header="Setor Atual"></Column>
        <Column field="status" header="Status">
          <template #body="slotProps">
            <span :class="getStatusClass(slotProps.data.status)" class="px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider">
              {{ slotProps.data.status }}
            </span>
          </template>
        </Column>
        <Column header="Ações" class="text-right">
          <template #body="slotProps">
            <div class="flex gap-2 justify-end">
              <Button icon="pi pi-history" rounded text severity="secondary" title="Ver Histórico" @click="router.push(`/processos/${slotProps.data.id}/historico`)" />
              <Button v-if="slotProps.data.status === 'Disponível'" icon="pi pi-sign-out" rounded text severity="warn" title="Registrar Retirada" @click="abrirRetirada(slotProps.data)" />
              <Button v-if="slotProps.data.status === 'Em Posse'" icon="pi pi-sign-in" rounded text severity="success" title="Registrar Devolução" @click="abrirDevolucao(slotProps.data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Modal Retirada -->
    <Dialog v-model:visible="showRetiradaDialog" header="Registrar Retirada de Processo" modal class="w-full max-w-md">
      <div class="space-y-4 pt-4">
        <div class="p-4 bg-blue-50 rounded-lg border border-blue-100 mb-4">
          <p class="text-sm font-bold text-blue-900">Processo: {{ selectedProcesso?.numero_contrato }}</p>
          <p class="text-xs text-blue-700">{{ selectedProcesso?.nome_cliente }}</p>
        </div>
        
        <div class="flex flex-col gap-2">
          <label class="font-semibold text-gray-700">Setor de Destino</label>
          <Select v-model="formRetirada.setor_destino" :options="setores" optionLabel="nome" optionValue="nome" placeholder="Selecione o setor..." class="w-full" />
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-semibold text-gray-700">Observações (Opcional)</label>
          <Textarea v-model="formRetirada.observacoes" rows="3" class="w-full border-gray-300" />
        </div>

        <div class="flex justify-end gap-2 pt-4 border-t border-gray-100">
          <Button label="Cancelar" text severity="secondary" @click="showRetiradaDialog = false" />
          <Button label="Confirmar Retirada" icon="pi pi-sign-out" :loading="submetendo" @click="confirmarRetirada" />
        </div>
      </div>
    </Dialog>

    <!-- Modal Devolução -->
    <Dialog v-model:visible="showDevolucaoDialog" header="Registrar Devolução de Processo" modal class="w-full max-w-md">
      <div class="space-y-4 pt-4">
        <div class="p-4 bg-green-50 rounded-lg border border-green-100 mb-4">
          <p class="text-sm font-bold text-green-900">Processo: {{ selectedProcesso?.numero_contrato }}</p>
          <p class="text-xs text-green-700">{{ selectedProcesso?.nome_cliente }}</p>
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-semibold text-gray-700">Novo Status do Processo</label>
          <Select v-model="formDevolucao.novo_status_processo" :options="statusOpcoes" optionLabel="label" optionValue="value" class="w-full" />
        </div>

        <div class="flex justify-end gap-2 pt-4 border-t border-gray-100">
          <Button label="Cancelar" text severity="secondary" @click="showDevolucaoDialog = false" />
          <Button label="Confirmar Devolução" icon="pi pi-check" severity="success" :loading="submetendo" @click="confirmarDevolucao" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<style scoped>
:deep(.p-datatable-sm .p-datatable-thead > tr > th) {
  padding: 1rem 1.5rem;
}
:deep(.p-datatable-sm .p-datatable-tbody > tr > td) {
  padding: 1rem 1.5rem;
}
</style>
