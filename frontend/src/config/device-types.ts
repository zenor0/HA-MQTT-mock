import { LightbulbIcon, ThermometerIcon, BellIcon, ToggleLeftIcon, AirVentIcon } from "lucide-react";

export type DeviceStateVisualization = {
  type: 'toggle' | 'slider' | 'text' | 'lineChart' | 'gauge' | 'colorPicker';
  label: string;
  property: string;
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
  options?: { label: string; value: any }[];
};

export type DeviceTypeConfig = {
  id: string;
  label: string;
  icon: React.ElementType;
  description: string;
  stateProperties: Record<string, DeviceStateVisualization>;
  requiredProperties: string[];
  optionalProperties: string[];
};

export const DEVICE_TYPES: Record<string, DeviceTypeConfig> = {
  light: {
    id: 'light',
    label: '灯光',
    icon: LightbulbIcon,
    description: '控制灯光的开关和亮度',
    stateProperties: {
      state: {
        type: 'toggle',
        label: '开关状态',
        property: 'state',
      },
      brightness: {
        type: 'slider',
        label: '亮度',
        property: 'brightness',
        min: 0,
        max: 255,
        step: 1,
      },
      color_temp: {
        type: 'slider',
        label: '色温',
        property: 'color_temp',
        min: 153,
        max: 500,
        step: 1,
      },
      rgb_color: {
        type: 'colorPicker',
        label: '颜色',
        property: 'rgb_color',
      },
    },
    requiredProperties: [],
    optionalProperties: ['brightness', 'color_temp', 'rgb_color'],
  },
  sensor: {
    id: 'sensor',
    label: '传感器',
    icon: ThermometerIcon,
    description: '读取环境数据的传感器',
    stateProperties: {
      state: {
        type: 'text',
        label: '当前值',
        property: 'state',
      },
      history: {
        type: 'lineChart',
        label: '历史数据',
        property: 'history',
      },
    },
    requiredProperties: ['sensor_type'],
    optionalProperties: [],
  },
  binary_sensor: {
    id: 'binary_sensor',
    label: '二进制传感器',
    icon: BellIcon,
    description: '检测开/关状态的传感器',
    stateProperties: {
      state: {
        type: 'toggle',
        label: '状态',
        property: 'state',
      },
    },
    requiredProperties: ['sensor_type'],
    optionalProperties: [],
  },
  switch: {
    id: 'switch',
    label: '开关',
    icon: ToggleLeftIcon,
    description: '控制设备的开关状态',
    stateProperties: {
      state: {
        type: 'toggle',
        label: '开关状态',
        property: 'state',
      },
    },
    requiredProperties: [],
    optionalProperties: [],
  },
  climate: {
    id: 'climate',
    label: '空调',
    icon: AirVentIcon,
    description: '控制温度和模式的空调设备',
    stateProperties: {
      state: {
        type: 'toggle',
        label: '开关状态',
        property: 'state',
      },
      temperature: {
        type: 'slider',
        label: '温度',
        property: 'temperature',
        min: 16,
        max: 30,
        step: 0.5,
        unit: '°C',
      },
      mode: {
        type: 'text',
        label: '模式',
        property: 'mode',
        options: [
          { label: '制冷', value: 'cool' },
          { label: '制热', value: 'heat' },
          { label: '自动', value: 'auto' },
          { label: '送风', value: 'fan_only' },
          { label: '除湿', value: 'dry' },
        ],
      },
      fan_mode: {
        type: 'text',
        label: '风速',
        property: 'fan_mode',
        options: [
          { label: '自动', value: 'auto' },
          { label: '低速', value: 'low' },
          { label: '中速', value: 'medium' },
          { label: '高速', value: 'high' },
        ],
      },
      current_temperature: {
        type: 'gauge',
        label: '当前温度',
        property: 'current_temperature',
        min: 0,
        max: 40,
        unit: '°C',
      },
    },
    requiredProperties: [],
    optionalProperties: ['temperature', 'mode', 'fan_mode', 'current_temperature'],
  },
};

export const getSensorTypeOptions = () => [
  { label: '温度', value: 'temperature' },
  { label: '湿度', value: 'humidity' },
  { label: '光照', value: 'illuminance' },
  { label: '压力', value: 'pressure' },
  { label: '电池', value: 'battery' },
  { label: '电量', value: 'power' },
  { label: '电压', value: 'voltage' },
  { label: '电流', value: 'current' },
  { label: '能量', value: 'energy' },
  { label: '气体', value: 'gas' },
  { label: '水', value: 'water' },
];

export const getBinarySensorTypeOptions = () => [
  { label: '运动', value: 'motion' },
  { label: '门窗', value: 'door' },
  { label: '烟雾', value: 'smoke' },
  { label: '漏水', value: 'moisture' },
  { label: '存在', value: 'presence' },
  { label: '电池', value: 'battery' },
  { label: '插头', value: 'plug' },
];

export const getDeviceTypeOptions = () => 
  Object.values(DEVICE_TYPES).map(type => ({
    label: type.label,
    value: type.id,
  }));

export const getDeviceTypeConfig = (type: string): DeviceTypeConfig | undefined => 
  DEVICE_TYPES[type]; 