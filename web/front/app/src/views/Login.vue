<template>
  <div class="auth-wrapper d-flex flex-column align-center justify-center fill-height pa-4">
    <div style="margin-bottom: 19vh; width:100%">
      <!-- Логотип и название -->
      <div class="mb-6 text-center">
        <v-img :src="logo" alt="EmPolimer Logo" max-width="100" class="mx-auto mb-2"
          style="border-radius: 16px;"></v-img>
        <div class="text-h5 font-weight-bold" style="letter-spacing:1px;">Проект ЕмПолимер</div>
      </div>
      <!-- Карточка авторизации -->
      <v-card class="mx-auto" width="100%" max-width="400" elevation="8">
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

import logo from '@/assets/img/logo.png'

import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'

import jwtService from "@/services/jwt/jwt.service"

const router = useRouter()
const authStore = useAuthStore()
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
  const credentials = { username: username.value, password: password.value }
  error.value = null
  const responseMessage = await authStore.login(credentials)
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

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  background: linear-gradient(120deg, #f8fafc 0%, #e0e7ef 100%);
}

@media (max-width: 600px) {
  .auth-wrapper .v-card {
    max-width: 100vw !important;
    width: 100vw !important;
    border-radius: 0 !important;
  }

  .auth-wrapper {
    padding: 0 !important;
  }
}
</style>