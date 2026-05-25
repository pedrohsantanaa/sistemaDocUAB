<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import Button from 'primevue/button'
import Timeline from 'primevue/timeline'
import Card from 'primevue/card'
import Tag from 'primevue/tag'

const route = useRoute()
const router = useRouter()
const processo = ref(null)
const historico = ref([])
const loading = ref(true)

const fetchHistorico = async () => {
  try {
    const response = await api.get(`/processos/${route.params.id}/historico`)
    processo.value = response.data.processo
    historico.value = response.data.historico
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchHistorico)
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto space-y-6">
    <div class="flex items-center gap-4">
      <Button icon="pi pi-arrow-left" rounded text @click="router.back()" />
      <h1 class="text-2xl font-bold">Histórico do Processo</h1>
    </div>

    <div v-if="loading" class="flex justify-center p-12">
       <i class="pi pi-spin pi-spinner text-4xl text-primary-500" />
    </div>

    <div v-else-if="processo" class="space-y-6">
      <!-- Process Info Card -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <p class="text-xs text-gray-500 uppercase font-bold mb-1">Cliente</p>
          <p class="font-semibold">{{ processo.nome_cliente }}</p>
          <p class="text-sm text-gray-600">{{ processo.cpf_cnpj }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-500 uppercase font-bold mb-1">Contrato</p>
          <p class="font-semibold">{{ processo.numero_contrato }}</p>
          <p class="text-sm text-gray-600">{{ processo.tipo_processo }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-500 uppercase font-bold mb-1">Status Atual</p>
          <Tag :value="processo.status" :severity="processo.status === 'Disponível' ? 'success' : 'warn'" />
        </div>
      </div>

      <!-- Timeline -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 class="text-lg font-semibold mb-8">Linha do Tempo de Movimentações</h3>
        <Timeline :value="historico" align="alternate" class="customized-timeline">
          <template #marker="slotProps">
            <span class="flex w-8 h-8 items-center justify-center text-white rounded-full shadow-sm" :class="slotProps.item.data_devolucao ? 'bg-green-500' : 'bg-blue-500'">
              <i :class="slotProps.item.data_devolucao ? 'pi pi-check' : 'pi pi-sign-out'"></i>
            </span>
          </template>
          <template #content="slotProps">
            <Card class="mb-4">
              <template #title>
                <span class="text-base">{{ slotProps.item.data_devolucao ? 'Devolvido' : 'Retirado' }}</span>
              </template>
              <template #subtitle>
                {{ new Date(slotProps.item.data_retirada).toLocaleDateString() }}
              </template>
              <template #content>
                <div class="text-sm space-y-1">
                  <p><strong>Destino:</strong> {{ slotProps.item.setor_destino }}</p>
                  <p><strong>Usuário:</strong> {{ slotProps.item.usuario_nome }}</p>
                  <p v-if="slotProps.item.observacoes"><strong>Obs:</strong> {{ slotProps.item.observacoes }}</p>
                  <p v-if="slotProps.item.data_devolucao" class="text-green-600 font-semibold">
                    Devolvido em: {{ new Date(slotProps.item.data_devolucao).toLocaleDateString() }}
                  </p>
                </div>
              </template>
            </Card>
          </template>
        </Timeline>
      </div>
    </div>
  </div>
</template>

<style scoped>
@media screen and (max-width: 960px) {
    ::v-deep(.customized-timeline) {
        .p-timeline-event:nth-child(even) {
            flex-direction: row;

            .p-timeline-event-content {
                text-align: left;
            }
        }

        .p-timeline-event-opposite {
            flex: 0;
        }
    }
}
</style>
