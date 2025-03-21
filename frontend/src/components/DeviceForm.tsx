'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { deviceService, DeviceCreate } from '../services/api';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { getDeviceTypeOptions, getSensorTypeOptions, getBinarySensorTypeOptions } from '@/config/device-types';

export default function DeviceForm() {
  const router = useRouter();
  const [formData, setFormData] = useState<DeviceCreate>({
    type: '',
    object_id: '',
    name: '',
    sensor_type: '',
  });

  // 创建设备
  const createMutation = useMutation({
    mutationFn: deviceService.createDevice,
    onSuccess: () => {
      router.push('/');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link href="/" className="flex items-center text-blue-500 hover:text-blue-700">
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          返回设备列表
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>创建新设备</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="type">设备类型 *</Label>
              <Select
                name="type"
                value={formData.type}
                onValueChange={(value) => setFormData((prev) => ({ ...prev, type: value }))}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="选择设备类型" />
                </SelectTrigger>
                <SelectContent>
                  {getDeviceTypeOptions().map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="object_id">设备ID *</Label>
              <Input
                id="object_id"
                name="object_id"
                value={formData.object_id}
                onChange={handleInputChange}
                required
                placeholder="例如: living_room_light"
              />
              <p className="text-xs text-muted-foreground">
                设备的唯一标识符，只能包含字母、数字和下划线
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">设备名称</Label>
              <Input
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="例如: 客厅灯"
              />
              <p className="text-xs text-muted-foreground">
                设备的显示名称，如不提供则使用设备ID
              </p>
            </div>

            {(formData.type === 'sensor' || formData.type === 'binary_sensor') && (
              <div className="space-y-2">
                <Label htmlFor="sensor_type">传感器类型</Label>
                <Select
                  name="sensor_type"
                  value={formData.sensor_type}
                  onValueChange={(value) => setFormData((prev) => ({ ...prev, sensor_type: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={formData.type === 'sensor' ? '例如: temperature' : '例如: motion'} />
                  </SelectTrigger>
                  <SelectContent>
                    {(formData.type === 'sensor' ? getSensorTypeOptions() : getBinarySensorTypeOptions()).map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  传感器的类型，如温度、湿度、运动等
                </p>
              </div>
            )}

            <div className="pt-4">
              <Button
                type="submit"
                disabled={createMutation.isPending}
                className="w-full"
              >
                {createMutation.isPending ? '创建中...' : '创建设备'}
              </Button>
            </div>

            {createMutation.isError && (
              <div className="p-3 bg-destructive/10 text-destructive rounded-md">
                创建失败: {(createMutation.error as Error).message}
              </div>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  );
} 