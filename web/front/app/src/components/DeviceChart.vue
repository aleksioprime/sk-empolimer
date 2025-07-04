<template>
  <div>
    <div v-if="showControls" class="mb-2 flex items-center gap-2">
      <v-btn size="small" @click="zoomIn">+</v-btn>
      <v-btn size="small" @click="zoomOut">−</v-btn>
      <v-btn size="small" @click="resetZoom">Сбросить</v-btn>
    </div>
    <div style="width: 100%; height: 250px">
      <Line ref="lineChartRef" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler
} from 'chart.js'

import zoomPlugin from 'chartjs-plugin-zoom'

Chart.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler, zoomPlugin)

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  field: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: '#1976d2' // по умолчанию синий
  },
  showControls: {
    type: Boolean,
    default: false,
  }
})


const sortedData = computed(() =>
  [...props.data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
)

const chartData = computed(() => ({
  labels: sortedData.value.map(item =>
    new Date(item.timestamp).toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  ),
  datasets: [
    {
      label: props.label || props.field,
      data: sortedData.value.map(item => item[props.field]),
      fill: false,
      borderColor: props.color,
      tension: 0.3,
      pointRadius: 2
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: true },
    zoom: {
      pan: {
        enabled: true,
        mode: 'x',
      },
      zoom: {
        wheel: { enabled: false },
        pinch: { enabled: false },
        mode: 'x',
      },
      limits: {
        x: { min: 0, max: props.data.length - 1 }
      }
    }
  },
  scales: {
    x: {
      ticks: {
        display: true,
        autoSkip: true,
        maxTicksLimit: 10,
      }
    },
    y: {
      type: 'linear',
      display: true,
      title: { display: true, text: props.label || props.field }
    }
  }
}

const lineChartRef = ref(null)

// Получаем ссылку на Chart.js instance:
function getChartInstance() {
  return lineChartRef.value?.chart
}

// Кнопки управления
function zoomIn() {
  const chart = getChartInstance()
  if (chart) {
    chart.zoom(1.2) // zoom in по x, 1.2 — коэффициент увеличения
  }
}
function zoomOut() {
  const chart = getChartInstance()
  if (chart) {
    chart.zoom(0.8) // zoom out по x, 0.8 — коэффициент уменьшения
  }
}
function resetZoom() {
  const chart = getChartInstance()
  if (chart) {
    chart.resetZoom()
  }
}

</script>