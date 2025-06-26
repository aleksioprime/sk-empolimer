<template>
  <v-container class="mt-12">
    <!-- Заголовок -->
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
                <v-list-item @click="viewDevice(device)">
                  <v-list-item-title>
                    <v-icon size="18" class="me-2">mdi-eye</v-icon>
                    Подробнее
                  </v-list-item-title>
                </v-list-item>
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
            <div class="mb-2">
              <span class="font-weight-bold">Описание:</span>
              <span>{{ device.description || '—' }}</span>
            </div>
            <div class="mb-2">
              <span class="font-weight-bold">Локация:</span>
              <span>{{ device.location || '—' }}</span>
            </div>
            <div class="mb-2" v-if="device.last_data">
              <v-icon class="me-2" color="blue">mdi-thermometer</v-icon>
              Температура: <b class="ms-1">{{ device.last_data.temperature }}°C</b>
            </div>
            <div class="mb-2" v-if="device.last_data">
              <v-icon class="me-2" color="green">mdi-water-percent</v-icon>
              Влажность: <b class="ms-1">{{ device.last_data.humidity }}%</b>
            </div>
            <div class="d-flex align-center" v-if="device.last_data">
              <v-icon class="me-2" color="grey">mdi-clock-outline</v-icon>
              Обновлено: <span class="ms-1">{{ formatTime(device.last_data.timestamp) }}</span>
            </div>
            <div class="mt-2">
              <v-chip :color="device.online ? 'green' : 'grey'" size="small" class="ma-0 pa-0">
                {{ device.online ? "Online" : "Offline" }}
              </v-chip>
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
          <v-text-field v-model="form.description" label="Описание" />
          <v-text-field v-model="form.location" label="Местоположение" />
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

    <!-- Диалог детальной информации -->
    <v-dialog v-model="detailDialogVisible" max-width="500">
      <v-card>
        <v-card-title>
          Детали устройства: {{ deviceDetails?.name }}
        </v-card-title>
        <v-card-text v-if="deviceDetails">
          <div>
            <b>Описание:</b> {{ deviceDetails.description || "—" }}
          </div>
          <div>
            <b>Местоположение:</b> {{ deviceDetails.location || "—" }}
          </div>
          <div>
            <b>ID:</b> {{ deviceDetails.id }}
          </div>
          <div v-if="deviceDetails?.data && deviceDetails.data.length">
            <div class="mb-2"><b>График температуры и влажности</b></div>
            <div style="width: 100%; height: 300px;">
              <DeviceChart :data="deviceDetails.data" />
            </div>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="detailDialogVisible = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

import DeviceChart from '@/components/DeviceChart.vue'

import { useRouter } from 'vue-router'
import { useAuthStore } from "@/stores/auth";
import { useDeviceStore } from "@/stores/device";

const router = useRouter()
const authStore = useAuthStore();
const deviceStore = useDeviceStore();

const devices = ref([]);
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const editingDevice = ref(null)
const deviceToDelete = ref(null)
const deviceDetails = ref(null)

const form = reactive({
  name: '',
  description: '',
  location: ''
})

function openAddDialog() {
  editingDevice.value = null
  form.name = ''
  form.description = ''
  form.location = ''
  dialogVisible.value = true
}

function openEditDialog(device) {
  editingDevice.value = device
  form.name = device.name
  form.description = device.description
  form.location = device.location
  dialogVisible.value = true
}

function closeDialog() {
  dialogVisible.value = false
}

async function saveDevice() {
  if (!form.name) return
  if (editingDevice.value) {
    // Обновление устройства
    const updated = await deviceStore.updateDevice(editingDevice.value.id, {
      name: form.name,
      description: form.description,
      location: form.location
    })
    if (updated) {
      // Локально обновляем в списке
      Object.assign(editingDevice.value, updated)
    }
  } else {
    // Добавление устройства
    const created = await deviceStore.createDevice({
      name: form.name,
      description: form.description,
      location: form.location
    })
    if (created) {
      devices.value.push(created)
    }
  }
  dialogVisible.value = false
  // Обновить список
  devices.value = await deviceStore.loadDevices();
}

function openDeleteDialog(device) {
  deviceToDelete.value = device
  deleteDialogVisible.value = true
}

async function deleteDevice() {
  const deleted = await deviceStore.deleteDevice(deviceToDelete.value.id)
  if (deleted) {
    devices.value = devices.value.filter(d => d.id !== deviceToDelete.value.id)
  }
  deleteDialogVisible.value = false
  // Обновить список
  devices.value = await deviceStore.loadDevices();
}

// Открыть диалог с деталями устройства (и получить данные с сервера)
async function viewDevice(device) {
  deviceDetails.value = await deviceStore.loadDeviceDetailed(device.id)
  detailDialogVisible.value = true
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

async function logout() {
  await authStore.logout()
  router.push({ name: 'login' })
}

const getChartData = (dataArray) => {
  if (!dataArray) return []
  return dataArray.map(item => ({
    timestamp: item.timestamp,
    temperature: item.temperature,
    humidity: item.humidity,
  }));
};

function formatChartTime(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

onMounted(async () => {
  devices.value = await deviceStore.loadDevices();
});
</script>