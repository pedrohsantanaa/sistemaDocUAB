<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { Pie, Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, CategoryScale, LinearScale, BarElement } from 'chart.js'
import Card from 'primevue/card'

ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale, LinearScale, BarElement)

const loading = ref(true)
const reportData = ref(null)

const chartDataStatus = ref({
  labels: [],
  datasets: [{ data: [], backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#6b7280'] }]
})

const chartDataMovements = ref({
  labels: [],
  datasets: [{ label: 'Movimentações', data: [], backgroundColor: '#3b82f6' }]
})

const fetchReports = async () => {
  try {
    const response = await api.get('/relatorios/')
    reportData.value = response.data
    
    // Status Chart
    const statusKeys = Object.keys(response.data.status_distribution)
    chartDataStatus.value.labels = statusKeys
    chartDataStatus.value.datasets[0].data = statusKeys.map(k => response.data.status_distribution[k])
    
    // Movements Chart
    chartDataMovements.value.labels = response.data.movements_last_7_days.map(d => d.label)
    chartDataMovements.value.datasets[0].data = response.data.movements_last_7_days.map(d => d.total)
    
  } catch (error) {
    console.error('Erro ao buscar relatórios', error)
  } finally {
    loading.value = false
  }
}

onMounted(fetchReports)
</script>

<template>
  <div class="p-6 space-y-6">
    <h1 class="text-2xl font-bold">Relatórios e Estatísticas</h1>

    <div v-if="loading" class="flex justify-center p-12">
       <i class="pi pi-spin pi-spinner text-4xl text-primary-500" />
    </div>

    <div v-else class="space-y-6">
      <!-- Top KPIs -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <template #title><span class="text-sm font-normal text-gray-500 uppercase">Total de Processos</span></template>
          <template #content><span class="text-3xl font-bold">{{ reportData.stats.total }}</span></template>
        </Card>
        <Card>
          <template #title><span class="text-sm font-normal text-gray-500 uppercase">Em Posse</span></template>
          <template #content><span class="text-3xl font-bold text-yellow-500">{{ reportData.stats.em_posse }}</span></template>
        </Card>
        <Card>
          <template #title><span class="text-sm font-normal text-gray-500 uppercase">Disponíveis</span></template>
          <template #content><span class="text-3xl font-bold text-green-500">{{ reportData.stats.disponivel }}</span></template>
        </Card>
        <Card>
          <template #title><span class="text-sm font-normal text-gray-500 uppercase">Pendentes</span></template>
          <template #content><span class="text-3xl font-bold text-red-500">{{ reportData.stats.pendente }}</span></template>
        </Card>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 class="text-lg font-semibold mb-4">Distribuição por Status</h3>
          <div class="h-64 flex justify-center">
            <Pie :data="chartDataStatus" :options="{ responsive: true, maintainAspectRatio: false }" />
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 class="text-lg font-semibold mb-4">Movimentações (Últimos 7 dias)</h3>
          <div class="h-64">
            <Bar :data="chartDataMovements" :options="{ responsive: true, maintainAspectRatio: false }" />
          </div>
        </div>
      </div>

      <!-- Recent Movements Table -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 class="text-lg font-semibold mb-4">Movimentações Recentes</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="border-b dark:border-gray-700">
                <th class="py-2">Contrato</th>
                <th class="py-2">Cliente</th>
                <th class="py-2">Usuário</th>
                <th class="py-2">Destino</th>
                <th class="py-2">Data</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="mov in reportData.recent_movements" :key="mov.id" class="border-b dark:border-gray-700 last:border-0">
                <td class="py-3 font-medium">{{ mov.processo }}</td>
                <td class="py-3">{{ mov.cliente }}</td>
                <td class="py-3">{{ mov.usuario }}</td>
                <td class="py-3">{{ mov.setor_destino }}</td>
                <td class="py-3 text-sm text-gray-500">
                  {{ new Date(mov.data_retirada).toLocaleDateString() }} {{ new Date(mov.data_retirada).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
