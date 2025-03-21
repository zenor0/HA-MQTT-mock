'use client';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { deviceService, DeviceResponse, DeviceState } from '@/services/api';
import { ArrowLeftIcon, TrashIcon } from '@heroicons/react/24/outline';
import { getDeviceTypeConfig } from '@/config/device-types';
import { DeviceStateVisualizer } from '@/components/DeviceStateVisualizer';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { useLogMessage } from '@/lib/log-utils';
import { useState } from 'react';

export default function DeviceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { logMessage } = useLogMessage();
  const [isDeleting, setIsDeleting] = useState(false);
  const deviceId = params.id as string;

  // 获取设备详情
  const { data: device, isLoading, error } = useQuery({
    queryKey: ['device', deviceId],
    queryFn: () => deviceService.getDevice(deviceId),
  });

  // 轮询设备状态
  const { data: deviceState } = useQuery({
    queryKey: ['deviceState', deviceId],
    queryFn: () => deviceService.getDeviceState(deviceId),
    refetchInterval: 5000, // 每5秒刷新一次
    enabled: !!device,
  });

  // 删除设备
  const deleteMutation = useMutation({
    mutationFn: deviceService.deleteDevice,
    onSuccess: () => {
      logMessage({
        title: '删除成功',
        description: '设备已成功删除',
      });
      router.push('/');
    },
    onError: (error) => {
      logMessage({
        title: '删除失败',
        description: (error as Error).message,
        variant: 'destructive',
      });
      setIsDeleting(false);
    },
  });

  // 合并设备信息和状态
  const deviceWithState = device ? {
    ...device,
    state: deviceState,
  } : undefined;

  const handleDelete = () => {
    if (isDeleting) {
      deleteMutation.mutate(deviceId);
    } else {
      setIsDeleting(true);
    }
  };

  const cancelDelete = () => {
    setIsDeleting(false);
  };

  const deviceTypeConfig = device ? getDeviceTypeConfig(device.type) : undefined;

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-pulse text-lg">加载中...</div>
        </div>
      </div>
    );
  }

  if (error || !device) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-destructive/10 p-4 rounded-md text-destructive">
          <h2 className="font-semibold">出错了</h2>
          <p>{(error as Error)?.message || '无法加载设备信息'}</p>
          <Link href="/" className="mt-4 text-blue-500 hover:underline flex items-center">
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            返回设备列表
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6 flex justify-between items-center">
        <Link href="/" className="flex items-center text-primary hover:underline">
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          返回设备列表
        </Link>

        {!isDeleting ? (
          <Button 
            variant="destructive" 
            size="sm"
            onClick={handleDelete}
          >
            <TrashIcon className="h-4 w-4 mr-1" />
            删除设备
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button 
              variant="destructive" 
              size="sm"
              onClick={handleDelete}
            >
              确认删除
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={cancelDelete}
            >
              取消
            </Button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>设备信息</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">设备ID</h3>
              <p className="text-lg">{device.object_id}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">设备名称</h3>
              <p className="text-lg">{device.name || device.object_id}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">设备类型</h3>
              <p className="text-lg">{deviceTypeConfig?.label || device.type}</p>
            </div>
            {device.sensor_type && (
              <div>
                <h3 className="text-sm font-medium text-muted-foreground">传感器类型</h3>
                <p className="text-lg">{device.sensor_type}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="md:col-span-2">
          {deviceWithState && <DeviceStateVisualizer device={deviceWithState} />}
        </div>
      </div>
    </div>
  );
} 