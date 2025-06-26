<template>
  <v-container class="mt-6">
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
    <v-row class="d-flex align-center">
      <v-col cols="auto">
        <v-btn color="primary" @click="openAddDialog">
          <v-icon class="me-1">mdi-plus</v-icon>
          Добавить устройство
        </v-btn>
      </v-col>
      <v-spacer />
      <v-col cols="auto" class="d-flex justify-end">
        <v-chip :color="wsConnected ? 'green' : 'error'" small>
          <v-icon start size="16">{{ wsConnected ? 'mdi-check' : 'mdi-alert' }}</v-icon>
          {{ wsConnected ? 'Online' : 'Offline' }}
        </v-chip>
      </v-col>
    </v-row>

    <!-- Карточки устройств -->
    <v-row>
      <v-col v-for="device in devices" :key="device.id" cols="12" sm="6" md="4" lg="3">
        <v-card>
          <v-card-title class="d-flex align-center no-wrap-title">
            <v-icon class="me-2" :color="device.online ? 'green' : 'grey'">
              {{ device.online ? 'mdi-access-point' : 'mdi-access-point-off' }}
            </v-icon>
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
              <span>{{ device.description || '—' }}</span>
            </div>
            <div class="mb-2">
              <span class="font-weight-bold">Локация:&nbsp;</span>
              <span>{{ device.location || '—' }}</span>
            </div>
            <hr class="mb-2">
            <div class="mb-2" v-if="device.last_data">
              <v-icon class="me-1" color="blue">mdi-thermometer</v-icon>
              Температура: <b>{{ device.last_data.temperature }}°C</b>
            </div>
            <div class="mb-2" v-if="device.last_data">
              <v-icon class="me-1" color="green">mdi-water-percent</v-icon>
              Влажность: <b>{{ device.last_data.humidity }}%</b>
            </div>
            <div class="d-flex align-center" v-if="device.last_data">
              <v-icon class="me-2" color="grey">mdi-clock-outline</v-icon>
              Обновлено:<span class="ms-1">{{ formatTime(device.last_data.timestamp) }}</span>
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
          <v-form ref="deviceForm">
            <v-text-field class="mb-1" v-model="form.name" label="Название" :rules="nameRules" />
            <v-text-field class="mb-1" v-model="form.description" label="Описание" />
            <v-text-field class="mb-1" v-model="form.location" label="Местоположение" />
          </v-form>
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
          <div class="mb-1">{{ deviceDetails.description || "—" }}</div>
          <div class="mb-1"><b>Местоположение:</b> {{ deviceDetails.location || "—" }}</div>
          <div v-if="deviceDetails?.data && deviceDetails.data.length">
            <div class="my-2"><b>Графики последних измерений</b></div>
            <DeviceChart class="my-3" :data="deviceDetails.data" field="temperature" label="Температура (°C)" color="#ff5252" />
            <DeviceChart class="my-3" :data="deviceDetails.data" field="humidity" label="Влажность (%)" color="#43a047" />
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
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import logger from '@/common/helpers/logger';

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

let ws = null

const wsConnected = ref(false);

const wsStatus = reactive({
  show: false,
  ok: true,
  msg: '',
})

function showWsStatus(msg, ok = true) {
  wsStatus.msg = msg;
  wsStatus.ok = ok;
  wsStatus.show = true;
}

function connectWebSocket() {
  const token = authStore.accessToken
  const WS_BASE_URL = import.meta.env.VITE_WS_URL || import.meta.env.VITE_SERVICE_URL.replace(/^http/, 'ws')
  const wsUrl = `${WS_BASE_URL}/api/v1/devices/ws/?token=${token}`
  const ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    logger.info('WS OPENED');
    wsConnected.value = true;
    showWsStatus('WS соединение установлено', true);
  }

  ws.onmessage = (event) => {

    try {
      const data = JSON.parse(event.data)
      if (data.type === 'devices_update' && Array.isArray(data.devices)) {
        devices.value = data.devices
      }
    } catch (e) {
    }
  }

  ws.onclose = () => {
    logger.info('WS CLOSED');
    wsConnected.value = false;
    showWsStatus('WS соединение разорвано', false);
    setTimeout(connectWebSocket, 2000)
  }
}

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

const deviceForm = ref(null)

const nameRules = [
  v => !!v || 'Обязательное поле',
  v => /^[a-z0-9_]{1,8}$/.test(v) || 'Строчные латинские буквы, цифры и _ (до 8)'
]

async function saveDevice() {
  const { valid } = await deviceForm.value.validate();
  if (!valid) return;

  if (editingDevice.value) {
    // Обновление устройства
    const updated = await deviceStore.updateDevice(editingDevice.value.id, {
      name: form.name,
      description: form.description,
      location: form.location
    })
  } else {
    // Добавление устройства
    const created = await deviceStore.createDevice({
      name: form.name,
      description: form.description,
      location: form.location
    })
  }
  dialogVisible.value = false

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
  const d = new Date(date) // здесь автоматом учитывается зона браузера
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

async function loadDevices() {
  devices.value = await deviceStore.loadDevices();
}

onMounted(async () => {
  loadDevices();
  connectWebSocket();
});

onUnmounted(() => {
  if (ws) ws.close();
});

// Вариант работы пулера для периодического обновления данных:

// const pollingInterval = 5000
// let poller = null

// onMounted(async () => {
//   loadDevices();

//   poller = setInterval(() => {
//     loadDevices();
//   }, pollingInterval);
// });

// onUnmounted(() => {
//   if (poller) clearInterval(poller);
// });

</script>