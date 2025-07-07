import { defineStore } from "pinia";
import resources from "@/services/resources";


export const useDeviceStore = defineStore("device", {
  state: () => ({
    devices: [],
    data: {},
  }),
  getters: {

  },
  actions: {
    // Загрузка списка устройств
    async loadDevices(config) {
      const res = await resources.device.getDevices(config);
      if (res.__state === "success") {
        this.devices = res.data
        return res.data
      }
      return null
    },
    // Загрузка детальной информации об устройстве по ID
    async loadDeviceDetailed(id) {
      const res = await resources.device.getDeviceDetailed(id);
      if (res.__state === "success") {
        return res.data
      }
      return null
    },
    // Добавление устройства
    async createDevice(data) {
      const res = await resources.device.createDevice(data);
      if (res.__state === "success") {
        return res.data
      }
      return null
    },
    // Обновление устройства
    async updateDevice(id, data) {
      const res = await resources.device.partialUpdateDevice(id, data);
      if (res.__state === "success") {
        return res.data
      }
      return null
    },
    // Удаление устройства
    async deleteDevice(id) {
      const res = await resources.device.deleteDevice(id);
      if (res.__state === "success") {
        return true
      }
      return null
    },
    // Загрузка данных устройства
    async loadDeviceData(id, config) {
      const res = await resources.device.getDeviceData(id, config);
      if (res.__state === "success") {
        return res.data
      }
      return null
    },
    // Загрузка данных устройства для графика
    async loadDeviceDataChart(id, config) {
      const res = await resources.device.getDeviceDataChart(id, config);
      if (res.__state === "success") {
        return res.data
      }
      return null
    },
    // Скачивание данных устройства в excel
    async  downloadDeviceData(id, config) {
      const res = await resources.device.downloadDeviceData(id, config);
      if (res.__state === "success") {
        const filename =
          res.headers['content-disposition']
            ?.split('filename=')[1]?.replace(/"/g, '') ||
          `device_${deviceId}_data.xlsx`
        return { blob: res.data, filename }
      }
      return null
    },
    // Очистка данных выбраного устройства
    async clearDeviceData(id) {
      const res = await resources.device.deleteDeviceData(id);
      if (res.__state === "success") {
        return true
      }
      return null
    }
  }
});