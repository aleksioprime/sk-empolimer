<template>
  <v-container class="mt-12">
    <v-card elevation="10" class="mb-8">
      <v-card-title>
        <v-icon class="me-2">mdi-view-dashboard</v-icon>
        Добро пожаловать на EmPolimer!
      </v-card-title>
      <v-card-text>
        <div>Вы вошли как <b>{{ authStore.user?.email }}</b>.</div>
        <v-btn class="mt-4" color="error" @click="logout">
          Выйти
        </v-btn>
      </v-card-text>
    </v-card>

    <!-- Кнопка добавить устройство -->
    <v-btn color="primary" class="mb-4" @click="openAddDialog">
      <v-icon class="me-1">mdi-plus</v-icon>
      Добавить устройство
    </v-btn>

    <!-- Карточки устройств -->
    <v-row>
      <v-col v-for="device in devices" :key="device.id" cols="12" sm="6" md="4" lg="3">
        <v-card>
          <v-card-title class="d-flex align-center no-wrap-title">
            <v-icon class="me-2" color="primary">mdi-access-point</v-icon>
            {{ device.name }}
            <v-spacer />
            <v-menu offset-y>
              <template #activator="{ props }">
                <v-btn icon size="small" v-bind="props">
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item @click="openEditDialog(device)">
                  <v-list-item-title>
                    <v-icon size="18" class="me-2">mdi-pencil</v-icon>
                    Редактировать
                  </v-list-item-title>
                </v-list-item>
                <v-list-item @click="openDeleteDialog(device)">
                  <v-list-item-title class="text-error">
                    <v-icon size="18" class="me-2" color="error">mdi-delete</v-icon>
                    Удалить
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-card-title>
          <v-card-text>
            <div class="d-flex align-center mb-2">
              <v-icon class="me-2" color="blue">mdi-thermometer</v-icon>
              Температура: <b class="ms-1">{{ device.temperature }}°C</b>
            </div>
            <div class="d-flex align-center mb-2">
              <v-icon class="me-2" color="green">mdi-water-percent</v-icon>
              Влажность: <b class="ms-1">{{ device.humidity }}%</b>
            </div>
            <div class="d-flex align-center">
              <v-icon class="me-2" color="grey">mdi-clock-outline</v-icon>
              Обновлено: <span class="ms-1">{{ formatTime(device.updatedAt) }}</span>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Диалог добавления/редактирования -->
    <v-dialog v-model="dialogVisible" persistent max-width="400">
      <v-card>
        <v-card-title>
          {{ editingDevice ? "Редактировать устройство" : "Добавить устройство" }}
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="form.name" label="Название" />
          <v-text-field v-model="form.temperature" label="Температура (°C)" type="number" />
          <v-text-field v-model="form.humidity" label="Влажность (%)" type="number" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="closeDialog">Отмена</v-btn>
          <v-btn color="primary" @click="saveDevice">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Диалог удаления -->
    <v-dialog v-model="deleteDialogVisible" max-width="400">
      <v-card>
        <v-card-title class="text-h6">Удалить устройство?</v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить <b>{{ deviceToDelete?.name }}</b>?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="deleteDialogVisible = false">Отмена</v-btn>
          <v-btn color="error" @click="deleteDevice">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, reactive } from 'vue'

// Импорт роутера
import { useRouter } from 'vue-router'
const router = useRouter()

// Импорт стора авторизации
import { useAuthStore } from "@/stores/auth";
const authStore = useAuthStore();

// Выход пользователя и переход на страницу логина
async function logout() {
  await authStore.logout()
  router.push({ name: 'login' })
}

// Список устройств (mock)
const devices = ref([
  {
    id: 1,
    name: 'Гостиная',
    temperature: 24.6,
    humidity: 51,
    updatedAt: new Date()
  },
  {
    id: 2,
    name: 'Спальня',
    temperature: 22.2,
    humidity: 46,
    updatedAt: new Date()
  }
])

// Формы и диалоги
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const editingDevice = ref(null)
const deviceToDelete = ref(null)
const form = reactive({
  name: '',
  temperature: '',
  humidity: ''
})

function openAddDialog() {
  editingDevice.value = null
  form.name = ''
  form.temperature = ''
  form.humidity = ''
  dialogVisible.value = true
}

function openEditDialog(device) {
  editingDevice.value = device
  form.name = device.name
  form.temperature = device.temperature
  form.humidity = device.humidity
  dialogVisible.value = true
}

function closeDialog() {
  dialogVisible.value = false
}

function saveDevice() {
  if (!form.name) return
  if (editingDevice.value) {
    // Редактирование
    editingDevice.value.name = form.name
    editingDevice.value.temperature = Number(form.temperature)
    editingDevice.value.humidity = Number(form.humidity)
    editingDevice.value.updatedAt = new Date()
  } else {
    // Добавление
    devices.value.push({
      id: Date.now(),
      name: form.name,
      temperature: Number(form.temperature),
      humidity: Number(form.humidity),
      updatedAt: new Date()
    })
  }
  dialogVisible.value = false
}

function openDeleteDialog(device) {
  deviceToDelete.value = device
  deleteDialogVisible.value = true
}

function deleteDevice() {
  devices.value = devices.value.filter(d => d.id !== deviceToDelete.value.id)
  deleteDialogVisible.value = false
}

// Форматирование времени (например, HH:MM DD.MM.YY)
function formatTime(date) {
  if (!date) return '-'
  const d = new Date(date)
  return (
    d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) +
    ' ' +
    d.toLocaleDateString('ru-RU')
  )
}
</script>