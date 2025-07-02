<template>
  <v-container class="mt-6">
    <v-snackbar v-model="wsStatus.show" :color="wsStatus.ok ? 'green' : 'red'" location="bottom right" :timeout="3000">
      <v-icon class="me-2" :color="wsStatus.ok ? 'white' : 'white'">
        {{ wsStatus.ok ? 'mdi-check-circle' : 'mdi-alert-circle' }}
      </v-icon>
      {{ wsStatus.msg }}
    </v-snackbar>

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
            <div class="mb-2" v-if="device.last_data">
              <v-icon class="me-1" color="orange">mdi-battery</v-icon>
              Батарея: <b>{{ device.last_data.battery ? device.last_data.battery + ' В' : '—' }}</b>
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
            <DeviceChart class="my-3" :data="deviceDetails.data" field="temperature" label="Температура (°C)"
              color="#ff5252" />
            <DeviceChart class="my-3" :data="deviceDetails.data" field="humidity" label="Влажность (%)"
              color="#43a047" />
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
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue'
import logger from '@/common/helpers/logger';
import { jwtDecode } from "jwt-decode";

import DeviceChart from '@/components/DeviceChart.vue'

// Инициализация роутера
import { useRouter } from 'vue-router'
const router = useRouter()

// Инициализация стора авторизации
import { useAuthStore } from "@/stores/auth";
const authStore = useAuthStore();

// Инициализация стора устройств
import { useDeviceStore } from "@/stores/device";
const deviceStore = useDeviceStore();

const devices = ref([]); // Список устройств

/**
 * Загружает список устройств из стора
 */
const loadDevices = async () => {
  devices.value = await deviceStore.loadDevices();
}

// --- POOLING ---

const poller = ref(null) // Таймер polling (интервал опроса API при потере WS)

const POLLING_INTERVAL = 5000 // Интервал polling, мс

/**
 * Запускает polling устройств, если не удалось подключиться к WebSocket
 */
const startPolling = () => {
  if (poller.value) return; // Polling уже активен
  poller.value = setInterval(() => {
    loadDevices()
  }, POLLING_INTERVAL)
  logger.info('Start polling')
}

/**
 * Останавливает polling
 */
const stopPolling = () => {
  if (poller.value) {
    clearInterval(poller.value)
    poller.value = null
    logger.info('Stop polling')
  }
}

// --- WEBSOCKET ---

let ws = null // WebSocket-соединение
const wsConnected = ref(false); // Состояние WebSocket-соединения

/**
 * Для всплывающих уведомлений статуса WS (плашка внизу)
 */
const wsStatus = reactive({
  show: false,
  ok: true,
  msg: '',
})

/**
 * Отображает всплывающий статус WS
 */
const showWsStatus = (msg, ok = true) => {
  wsStatus.msg = msg;
  wsStatus.ok = ok;
  wsStatus.show = true;
}

/**
 * Подключается к WebSocket с текущим токеном из стора.
 * Если не удалось — переходит на polling.
 */
const connectWebSocket = async () => {

  // Если токена нет или скоро истекает, делаем refresh
  if (needRefresh(authStore.accessToken)) {
    logger.info('AccessToken почти истёк, обновляем...');
    const refreshed = await authStore.refresh();
    if (!refreshed) {
      logger.error('Refresh failed, logging out');
      logout();
      return;
    }
  }

  if (ws) ws.close(); // Закрыть старое соединение, если было

  if (!authStore.user) return;

  const token = authStore.accessToken
  // Определяем адрес WebSocket в зависимости от настроек окружения
  const WS_BASE_URL = import.meta.env.VITE_WS_URL || import.meta.env.VITE_SERVICE_URL.replace(/^http/, 'ws')
  const wsUrl = `${WS_BASE_URL}/api/v1/devices/ws/?token=${token}`
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    logger.info('WS OPENED');
    wsConnected.value = true;
    stopPolling();
    showWsStatus('WS соединение установлено', true);
  }

  ws.onmessage = (event) => {
    // Обрабатываем входящие сообщения (например, обновление списка устройств)
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'devices_update' && Array.isArray(data.devices)) {
        devices.value = data.devices
      }
    } catch (e) {
      // Некорректные данные игнорируем
    }
  }

  ws.onerror = (e) => {
    logger.info('WS ERROR')
    wsConnected.value = false
    showWsStatus('Ошибка WS соединения, перехожу на polling', false)
    startPolling()
  }

  ws.onclose = () => {
    logger.info('WS CLOSED');
    wsConnected.value = false;
    showWsStatus('WS соединение разорвано, перехожу на polling', false)
    startPolling()
    // Попытка переподключения через 2 сек
    setTimeout(connectWebSocket, 2000)
  }
}

/**
 * Закрывает WebSocket-соединение
 */
const stopSocket = () => {
  if (ws) {
    ws.close();
    ws = null;
  }
}

// --- СОЗДАНИЕ И РЕДАКТИРОВАНИЕ УСТРОЙСТВ ---

// Модель для формы создания/редактирования устройства
const form = reactive({
  name: '',
  description: '',
  location: ''
})

const dialogVisible = ref(false) // Диалог добавления/редактирования устройства
const editingDevice = ref(null) // Текущее редактируемое устройство
const deviceForm = ref(null) // Ссылка на форму устройства

/**
 * Открывает диалог добавления нового устройства
 */
const openAddDialog = () => {
  editingDevice.value = null
  form.name = ''
  form.description = ''
  form.location = ''
  dialogVisible.value = true
}

/**
 * Открывает диалог редактирования существующего устройства
 */
const openEditDialog = (device) => {
  editingDevice.value = device
  form.name = device.name
  form.description = device.description
  form.location = device.location
  dialogVisible.value = true
}

/**
 * Закрывает диалог добавления/редактирования
 */
const closeDialog = () => {
  dialogVisible.value = false
}

// --- Валидация имени устройства ---
const nameRules = [
  v => !!v || 'Обязательное поле',
  v => /^[a-z0-9_]{1,8}$/.test(v) || 'Строчные латинские буквы, цифры и _ (до 8)'
]

/**
 * Сохраняет (создаёт/обновляет) устройство по данным формы
 */
const saveDevice = async () => {
  const { valid } = await deviceForm.value.validate();
  if (!valid) return;

  if (editingDevice.value) {
    // Обновление устройства
    await deviceStore.updateDevice(editingDevice.value.id, {
      name: form.name,
      description: form.description,
      location: form.location
    })
  } else {
    // Добавление нового устройства
    await deviceStore.createDevice({
      name: form.name,
      description: form.description,
      location: form.location
    })
  }
  dialogVisible.value = false

  devices.value = await deviceStore.loadDevices();
}

// --- УДАЛЕНИЕ УСТРОЙСТВА ---

const deleteDialogVisible = ref(false) // Диалог подтверждения удаления
const deviceToDelete = ref(null) // Устройство, выбранное для удаления

/**
 * Открывает диалог подтверждения удаления устройства
 */
const openDeleteDialog = (device) => {
  deviceToDelete.value = device
  deleteDialogVisible.value = true
}

/**
 * Удаляет выбранное устройство
 */
const deleteDevice = async () => {
  const deleted = await deviceStore.deleteDevice(deviceToDelete.value.id)
  if (deleted) {
    devices.value = devices.value.filter(d => d.id !== deviceToDelete.value.id)
  }
  deleteDialogVisible.value = false
  devices.value = await deviceStore.loadDevices();
}

// --- ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ ---

const detailDialogVisible = ref(false) // Диалог детальной информации
const deviceDetails = ref(null) // Детальная информация по устройству

/**
 * Открывает диалог с информацией устройства и загружает данные для графиков
 */
const viewDevice = async (device) => {
  deviceDetails.value = await deviceStore.loadDeviceDetailed(device.id)
  detailDialogVisible.value = true
}

// --- ДРУГИЕ ФУНКЦИИ ---

/**
 * Проверяет, что токен скоро истекает
 */
const needRefresh = (token) => {
  if (!token) return true;
  try {
    const decoded = jwtDecode(token);
    const now = Math.floor(Date.now() / 1000);
    return (decoded.exp - now) < 30; // например, если осталось меньше 30 сек
  } catch (e) {
    return true;
  }
}

/**
 * Форматирует дату в удобный вид (например, "14:32 27.06.25")
 */
const formatTime = (date) => {
  if (!date) return '-'
  const d = new Date(date) // Автоматически учитывает временную зону браузера
  return (
    d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) +
    ' ' +
    d.toLocaleDateString('ru-RU')
  )
}

/**
 * Выход из аккаунта, переход на экран авторизации
 */
const logout = async () => {
  await authStore.logout()
  stopSocket();
  stopPolling();
  router.push({ name: 'login' })
}

// --- ЖИЗНЕННЫЙ ЦИКЛ КОМПОНЕНТА ---

// При монтировании компонента: загрузить устройства и подключиться к WebSocket
onMounted(async () => {
  loadDevices();
  connectWebSocket();
});

// При размонтировании: закрыть соединения и polling
onUnmounted(() => {
  stopSocket();
  stopPolling();
});

</script>