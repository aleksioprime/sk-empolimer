import { ApiService } from "@/services/api/api.service";

export class DeviceResource extends ApiService {
  constructor() {
    super();
  }

  getDevices(config) {
    return this.$get(`/api/v1/devices/`, config);
  }

  getDeviceDetailed(id) {
    return this.$get(`/api/v1/devices/${id}/`);
  }

  createDevice(data) {
    return this.$post(`/api/v1/devices/`, data);
  }

  partialUpdateDevice(id, data) {
    return this.$patch(`/api/v1/devices/${id}/`, data);
  }

  deleteDevice(id, data) {
    return this.$delete(`/api/v1/devices/${id}/`, data);
  }

  getDeviceData(id, config) {
    return this.$get(`/api/v1/devices/${id}/data/`, config);
  }

  getDeviceDataChart(id, config) {
    return this.$get(`/api/v1/devices/${id}/data/chart`, config);
  }

  downloadDeviceData(id, config) {
    config.responseType = 'blob';
    return this.$get(`/api/v1/devices/${id}/data/export`, config);
  }
}