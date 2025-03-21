"use client";

import React, { useState, useEffect } from 'react';
import { DeviceResponse } from '@/services/api';
import { getDeviceTypeConfig, DeviceStateVisualization } from '@/config/device-types';
import { DeviceStateChart } from './ui/device-state-chart';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Switch } from './ui/switch';
import { Label } from './ui/label';
import { Slider } from './ui/slider';

interface DeviceStateVisualizerProps {
  device: DeviceResponse;
}

// 模拟历史数据生成
const generateMockHistoryData = (value: number, count = 24) => {
  const now = new Date();
  const data = [];
  
  for (let i = count - 1; i >= 0; i--) {
    const timestamp = new Date(now.getTime() - i * 3600000).toISOString(); // 每小时一个点
    const randomVariation = Math.random() * 10 - 5; // -5 到 5 之间的随机变化
    const adjustedValue = Math.max(0, value + randomVariation);
    
    data.push({
      timestamp,
      value: Number(adjustedValue.toFixed(1))
    });
  }
  
  return data;
};

export function DeviceStateVisualizer({ device }: DeviceStateVisualizerProps) {
  const [historyData, setHistoryData] = useState<any[]>([]);
  const deviceConfig = getDeviceTypeConfig(device.type);
  
  useEffect(() => {
    // 如果是传感器类型，生成模拟历史数据
    if (device.type === 'sensor' && device.state?.state) {
      const value = parseFloat(device.state.state);
      if (!isNaN(value)) {
        setHistoryData(generateMockHistoryData(value));
      }
    }
  }, [device]);

  if (!deviceConfig || !device.state) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>设备状态</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">无可用状态数据</p>
        </CardContent>
      </Card>
    );
  }

  const renderVisualization = (property: string, config: DeviceStateVisualization) => {
    const value = device.state?.[property];
    
    if (value === undefined) return null;
    
    switch (config.type) {
      case 'toggle':
        return (
          <div className="flex items-center space-x-2" key={property}>
            <Switch id={`${device.object_id}-${property}`} checked={value === 'on' || value === true} disabled />
            <Label htmlFor={`${device.object_id}-${property}`}>{config.label}: {value === 'on' || value === true ? '开启' : '关闭'}</Label>
          </div>
        );
        
      case 'slider':
        return (
          <div className="space-y-2" key={property}>
            <div className="flex justify-between">
              <Label>{config.label}</Label>
              <span>{value}{config.unit || ''}</span>
            </div>
            <Slider
              value={[parseFloat(value)]}
              min={config.min || 0}
              max={config.max || 100}
              step={config.step || 1}
              disabled
            />
          </div>
        );
        
      case 'text':
        return (
          <div className="space-y-1" key={property}>
            <Label>{config.label}</Label>
            <div className="text-2xl font-bold">{value}{config.unit || ''}</div>
          </div>
        );
        
      case 'lineChart':
        if (property === 'history' && historyData.length > 0) {
          return (
            <DeviceStateChart
              key={property}
              title={`${device.name || device.object_id} ${config.label}`}
              data={historyData}
              unit={device.sensor_type === 'temperature' ? '°C' : ''}
            />
          );
        }
        return null;
        
      default:
        return (
          <div key={property}>
            <Label>{config.label}</Label>
            <div className="mt-1 text-sm">{JSON.stringify(value)}</div>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>设备状态</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(deviceConfig.stateProperties).map(([property, config]) => 
            renderVisualization(property, config)
          )}
        </CardContent>
      </Card>
      
      {/* 对于传感器类型，添加历史数据图表 */}
      {device.type === 'sensor' && device.state?.state && historyData.length > 0 && (
        <DeviceStateChart
          title={`${device.name || device.object_id} 历史数据`}
          data={historyData}
          unit={device.sensor_type === 'temperature' ? '°C' : 
                device.sensor_type === 'humidity' ? '%' : ''}
        />
      )}
    </div>
  );
} 