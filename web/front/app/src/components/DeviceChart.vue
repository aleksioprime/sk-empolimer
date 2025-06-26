<template>
  <div>
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
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
  }
})

const chartData = {
  labels: props.data.map(item =>
    new Date(item.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  ),
  datasets: [
    {
      label: 'Температура (°C)',
      data: props.data.map(item => item.temperature),
      fill: false,
      borderColor: '#1976d2',
      tension: 0.3,
      yAxisID: 'temperature',
      pointRadius: 2
    },
    {
      label: 'Влажность (%)',
      data: props.data.map(item => item.humidity),
      fill: false,
      borderColor: '#43a047',
      tension: 0.3,
      yAxisID: 'humidity',
      pointRadius: 2
    }
  ]
}

const chartOptions = {
  responsive: true,
  interaction: {
    mode: 'index',
    intersect: false
  },
  stacked: false,
  plugins: {
    legend: { position: 'top' },
    tooltip: { enabled: true }
  },
  scales: {
    temperature: {
      type: 'linear',
      display: true,
      position: 'left',
      title: { display: true, text: 'Температура (°C)' }
    },
    humidity: {
      type: 'linear',
      display: true,
      position: 'right',
      title: { display: true, text: 'Влажность (%)' },
      grid: { drawOnChartArea: false }
    }
  }
}
</script>
