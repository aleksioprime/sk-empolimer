<template>
  <div style="width: 100%; height: 200px">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
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

Chart.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

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
    tooltip: { enabled: true }
  },
  scales: {
    x: {
      ticks: {
        display: false
      }
    },
    y: {
      type: 'linear',
      display: true,
      title: { display: true, text: props.label || props.field }
    }
  }
}
</script>
