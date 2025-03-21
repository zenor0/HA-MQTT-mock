import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 更新API基础URL的方法
export const updateApiBaseUrl = (newBaseUrl: string) => {
  api.defaults.baseURL = newBaseUrl;
};

// 设备类型定义
export interface DeviceCreate {
  type: string;
  object_id: string;
  name?: string;
  sensor_type?: string;
}

export interface DeviceUpdate {
  type?: string;
  name?: string;
  sensor_type?: string;
}

export interface DeviceState {
  state: Record<string, any>;
}

export interface DeviceResponse {
  id?: string;
  type: string;
  object_id: string;
  name?: string;
  sensor_type?: string;
  state?: Record<string, any>;
  last_seen?: string;
}

// API服务
export const deviceService = {
  // 获取所有设备
  getAllDevices: async (): Promise<DeviceResponse[]> => {
    const response = await api.get('/api/devices');
    return response.data;
  },

  // 获取单个设备
  getDevice: async (deviceId: string): Promise<DeviceResponse> => {
    const response = await api.get(`/api/devices/${deviceId}`);
    return response.data;
  },

  // 创建设备
  createDevice: async (device: DeviceCreate): Promise<DeviceResponse> => {
    const response = await api.post('/api/devices', device);
    return response.data;
  },

  // 更新设备
  updateDevice: async (deviceId: string, device: DeviceUpdate): Promise<DeviceResponse> => {
    const response = await api.put(`/api/devices/${deviceId}`, device);
    return response.data;
  },

  // 删除设备
  deleteDevice: async (deviceId: string): Promise<void> => {
    await api.delete(`/api/devices/${deviceId}`);
  },

  // 获取设备状态
  getDeviceState: async (deviceId: string): Promise<DeviceState> => {
    const response = await api.get(`/api/devices/${deviceId}/state`);
    return response.data;
  },

  // 更新设备状态
  updateDeviceState: async (deviceId: string, state: DeviceState): Promise<DeviceState> => {
    const response = await api.put(`/api/devices/${deviceId}/state`, state);
    return response.data;
  },

  // 重新加载设备配置
  reloadDevices: async (): Promise<void> => {
    await api.post('/api/reload');
  },
};

export default api; 