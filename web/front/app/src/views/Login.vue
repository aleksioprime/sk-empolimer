<template>
  <v-card class="mx-auto mt-16" width="400" max-width="400" elevation="8">
    <v-card-title class="text-h6 font-weight-bold">Войдите в свой аккаунт</v-card-title>
    <v-card-text>
      <v-form @submit.prevent="login" ref="form" v-model="valid">
        <v-text-field v-model="username" label="Пользователь" type="email" :rules="[rules.required]"
          prepend-inner-icon="mdi-account" autocomplete="username" required />
        <v-text-field v-model="password" label="Пароль" type="password" :rules="[rules.required]"
          prepend-inner-icon="mdi-lock" autocomplete="current-password" required />
        <v-btn :loading="loading" color="primary" type="submit" class="mt-4" block>
          Войти
        </v-btn>
        <v-alert v-if="error" type="error" class="mt-3" dense>{{ error }}</v-alert>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import logger from '@/common/helpers/logger';

import { useRouter } from 'vue-router'
const router = useRouter()

import { useAuthStore } from '@/stores'
const authStore = useAuthStore()

import jwtService from "@/services/jwt/jwt.service"

const form = ref(null)

const error = ref('')
const username = ref('')
const password = ref('')
const loading = ref(false)
const valid = ref(false)

const rules = {
  required: v => !!v || 'Обязательное поле',
  email: v => !v || /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/.test(v) || 'Некорректный email',
}

async function login() {
  const { valid } = await form.value.validate();
  if (!valid) return;

  loading.value = true

  const credentials = {
    username: username.value,
    password: password.value,
  }

  error.value = null

  const responseMessage = await authStore.login(credentials);
  loading.value = false

  if (responseMessage !== 'success') {
    error.value = responseMessage;
    return
  }

  await authStore.getMe();
  await router.push({ name: "dashboard" });
}

onMounted(async () => {
  const accessToken = jwtService.getAccessToken();

  if (accessToken && authStore.isAuthenticated) {
    router.push({ name: "dashboard" });
  }
})
</script>