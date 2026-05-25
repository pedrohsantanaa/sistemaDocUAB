<script setup>
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import AppLayout from './components/AppLayout.vue'

const route = useRoute()
const auth = useAuthStore()

auth.init()
</script>

<template>
  <template v-if="route.meta.public">
    <router-view />
  </template>
  <template v-else>
    <AppLayout>
      <router-view />
    </AppLayout>
  </template>
</template>
