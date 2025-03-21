'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { deviceService, DeviceResponse } from '../services/api';
import { useState } from 'react';
import Link from 'next/link';
import { PlusIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { useConfig } from '@/providers/ConfigProvider';
import { DeviceStateVisualizer } from './DeviceStateVisualizer';

export default function DeviceList() {
  const queryClient = useQueryClient();
  const [isReloading, setIsReloading] = useState(false);

  // 获取所有设备
  const { data: devices = [], isLoading, error } = useQuery<DeviceResponse[], Error>({
    queryKey: ['devices'],
    queryFn: deviceService.getAllDevices,
  });

  // 重新加载设备配置
  const reloadMutation = useMutation({
    mutationFn: deviceService.reloadDevices,
    onMutate: () => {
      setIsReloading(true);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
    onSettled: () => {
      setIsReloading(false);
    },
  });

  // 删除设备
  const deleteMutation = useMutation({
    mutationFn: (deviceId: string) => deviceService.deleteDevice(deviceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
  });

  const handleReload = () => {
    reloadMutation.mutate();
  };

  const handleDelete = (deviceId: string) => {
    if (confirm('确定要删除此设备吗？')) {
      deleteMutation.mutate(deviceId);
    }
  };

  if (isLoading) return <div className="text-center py-10">加载中...</div>;
  if (error) return <div className="text-center py-10 text-red-500">加载失败: {error.message}</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">设备列表</h1>
        <div className="flex space-x-2">
          <button
            onClick={handleReload}
            disabled={isReloading}
            className="flex items-center px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            <ArrowPathIcon className={`h-5 w-5 mr-2 ${isReloading ? 'animate-spin' : ''}`} />
            重新加载
          </button>
          <Link
            href="/devices/new"
            className="flex items-center px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            添加设备
          </Link>
        </div>
      </div>

      {devices.length === 0 ? (
        <div className="text-center py-10 bg-gray-50 rounded-lg">
          <p className="text-gray-500">暂无设备，请添加新设备</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {devices.map((device: DeviceResponse) => (
            <DeviceCard 
              key={device.object_id} 
              device={device} 
              onDelete={() => handleDelete(device.object_id)} 
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface DeviceCardProps {
  device: DeviceResponse;
  onDelete: () => void;
}

function DeviceCard({ device, onDelete }: DeviceCardProps) {
  const { debugMode } = useConfig();
  
  // 获取设备类型对应的图标和颜色
  const getDeviceTypeInfo = (type: string) => {
    switch (type) {
      case 'light':
        return { bgColor: 'bg-yellow-100', textColor: 'text-yellow-800' };
      case 'sensor':
        return { bgColor: 'bg-blue-100', textColor: 'text-blue-800' };
      case 'binary_sensor':
        return { bgColor: 'bg-purple-100', textColor: 'text-purple-800' };
      default:
        return { bgColor: 'bg-gray-100', textColor: 'text-gray-800' };
    }
  };

  const { bgColor, textColor } = getDeviceTypeInfo(device.type);

  return (
    <div className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      <div className="p-4">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-semibold">{device.name || device.object_id}</h2>
            <div className="flex items-center mt-1">
              <span className={`inline-block px-2 py-1 text-xs rounded-full ${bgColor} ${textColor}`}>
                {device.type}
              </span>
              {device.sensor_type && (
                <span className="ml-2 text-sm text-gray-500">{device.sensor_type}</span>
              )}
            </div>
          </div>
          <div className="flex space-x-2">
            <Link
              href={`/devices/${device.object_id}`}
              className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              详情
            </Link>
            <button
              onClick={onDelete}
              className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
            >
              删除
            </button>
          </div>
        </div>

        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-500">设备ID</h3>
          <p className="text-gray-700">{device.object_id}</p>
        </div>

        {device.state && (
          <div className="mt-4">
            {debugMode ? (
              <>
                <h3 className="text-sm font-medium text-gray-500">当前状态 (调试模式)</h3>
                <pre className="mt-1 p-2 bg-gray-50 rounded text-xs overflow-auto max-h-40">
                  {JSON.stringify(device.state, null, 2)}
                </pre>
              </>
            ) : (
              <div className="mt-2">
                <DeviceStateVisualizer device={device} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 