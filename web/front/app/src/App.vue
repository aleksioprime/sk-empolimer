<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script setup>
import { watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

watch(
  () => route.name,
  (name) => {
    document.title = `EmPolimer - ${route.meta.title}` || 'EmPolimer'
  },
  { immediate: true }
)
</script>