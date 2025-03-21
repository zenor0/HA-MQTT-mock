'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { deviceService, DeviceResponse, DeviceState, DeviceUpdate } from '../services/api';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';
import { useConfig } from '@/providers/ConfigProvider';
import { DeviceStateVisualizer } from './DeviceStateVisualizer';

interface DeviceDetailProps {
  deviceId: string;
}

export default function DeviceDetail({ deviceId }: DeviceDetailProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<DeviceUpdate>({});
  const [stateData, setStateData] = useState<Record<string, any>>({});
  const { debugMode } = useConfig();

  // 获取设备详情
  const { data: device, isLoading, error } = useQuery<DeviceResponse, Error>({
    queryKey: ['device', deviceId],
    queryFn: () => deviceService.getDevice(deviceId),
  });

  // 获取设备状态
  const { data: deviceState } = useQuery<DeviceState, Error>({
    queryKey: ['deviceState', deviceId],
    queryFn: () => deviceService.getDeviceState(deviceId),
    enabled: !!device,
  });

  // 更新设备
  const updateMutation = useMutation({
    mutationFn: (data: DeviceUpdate) => deviceService.updateDevice(deviceId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['device', deviceId] });
      setIsEditing(false);
    },
  });

  // 更新设备状态
  const updateStateMutation = useMutation({
    mutationFn: (data: DeviceState) => deviceService.updateDeviceState(deviceId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deviceState', deviceId] });
    },
  });

  // 删除设备
  const deleteMutation = useMutation({
    mutationFn: () => deviceService.deleteDevice(deviceId),
    onSuccess: () => {
      router.push('/');
    },
  });

  const handleEditToggle = () => {
    if (isEditing) {
      setIsEditing(false);
    } else {
      setFormData({
        type: device?.type,
        name: device?.name,
        sensor_type: device?.sensor_type,
      });
      setIsEditing(true);
    }
  };

  const handleUpdateDevice = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate(formData);
  };

  const handleUpdateState = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const state = { state: stateData };
      updateStateMutation.mutate(state);
    } catch (error) {
      console.error('Invalid state data:', error);
    }
  };

  const handleDelete = () => {
    if (confirm('确定要删除此设备吗？此操作不可撤销。')) {
      deleteMutation.mutate();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleStateChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    try {
      const value = JSON.parse(e.target.value);
      setStateData(value);
    } catch (error) {
      // 解析错误时不更新状态
      console.error('Invalid JSON:', error);
    }
  };

  if (isLoading) return <div className="text-center py-10">加载中...</div>;
  if (error) return <div className="text-center py-10 text-red-500">加载失败: {error.message}</div>;
  if (!device) return <div className="text-center py-10">设备不存在</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link href="/" className="flex items-center text-blue-500 hover:text-blue-700">
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          返回设备列表
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">{device.name || device.object_id}</h1>
          <div className="flex space-x-2">
            <button
              onClick={handleEditToggle}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              {isEditing ? '取消' : '编辑'}
            </button>
            <button
              onClick={handleDelete}
              className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            >
              删除
            </button>
          </div>
        </div>

        {isEditing ? (
          <form onSubmit={handleUpdateDevice} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">设备类型</label>
              <input
                type="text"
                name="type"
                value={formData.type || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">设备名称</label>
              <input
                type="text"
                name="name"
                value={formData.name || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">传感器类型</label>
              <input
                type="text"
                name="sensor_type"
                value={formData.sensor_type || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div className="flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                保存
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-medium">设备信息</h2>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-500">设备ID</label>
                  <p className="mt-1">{device.object_id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">设备类型</label>
                  <p className="mt-1">{device.type}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">设备名称</label>
                  <p className="mt-1">{device.name || '-'}</p>
                </div>
                {device.sensor_type && (
                  <div>
                    <label className="block text-sm font-medium text-gray-500">传感器类型</label>
                    <p className="mt-1">{device.sensor_type}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="border-t pt-4">
              <h2 className="text-lg font-medium">设备状态 {debugMode && '(调试模式)'}</h2>
              {deviceState ? (
                <div className="mt-2">
                  {debugMode ? (
                    <pre className="p-3 bg-gray-50 rounded text-sm overflow-auto max-h-60">
                      {JSON.stringify(deviceState.state, null, 2)}
                    </pre>
                  ) : (
                    <DeviceStateVisualizer device={{
                      ...device,
                      state: deviceState.state
                    }} />
                  )}
                </div>
              ) : (
                <p className="text-gray-500">暂无状态数据</p>
              )}
            </div>
          </div>
        )}

        <div className="mt-8 border-t pt-6">
          <h2 className="text-lg font-medium mb-4">更新设备状态</h2>
          <form onSubmit={handleUpdateState} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">状态数据 (JSON格式)</label>
              <textarea
                defaultValue={deviceState ? JSON.stringify(deviceState.state, null, 2) : '{}'}
                onChange={handleStateChange}
                rows={6}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 font-mono text-sm"
              />
            </div>
            <div className="flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                更新状态
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
} 