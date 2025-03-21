'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { deviceService, DeviceResponse } from '@/services/api';
import { getDeviceTypeConfig } from '@/config/device-types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, Plus, ExternalLink } from 'lucide-react';

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const { data: devices = [], isLoading, error } = useQuery({
    queryKey: ['devices'],
    queryFn: deviceService.getAllDevices,
  });

  // 根据搜索条件过滤设备
  const filteredDevices = devices.filter(
    (device: DeviceResponse) =>
      device.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      device.object_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      device.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 根据类型对设备分组
  const devicesByType: Record<string, DeviceResponse[]> = {};
  filteredDevices.forEach((device: DeviceResponse) => {
    if (!devicesByType[device.type]) {
      devicesByType[device.type] = [];
    }
    devicesByType[device.type].push(device);
  });

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-8">
        <h1 className="text-3xl font-bold">智能设备</h1>
        
        <div className="flex items-center w-full md:w-auto space-x-2">
          <div className="relative w-full md:w-80">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="搜索设备..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button asChild>
            <Link href="/devices/new">
              <Plus className="mr-1 h-4 w-4" />
              添加设备
            </Link>
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-pulse text-lg">加载中...</div>
        </div>
      ) : error ? (
        <div className="bg-destructive/10 p-4 rounded-md text-destructive">
          <h2 className="font-semibold">出错了</h2>
          <p>{(error as Error)?.message || '无法加载设备列表'}</p>
        </div>
      ) : filteredDevices.length === 0 ? (
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold mb-2">没有找到设备</h2>
          <p className="text-muted-foreground mb-6">
            {searchQuery
              ? '没有符合搜索条件的设备'
              : '开始添加你的第一个智能设备吧'}
          </p>
          <Button asChild>
            <Link href="/devices/new">
              <Plus className="mr-1 h-4 w-4" />
              添加设备
            </Link>
          </Button>
        </div>
      ) : (
        <div className="space-y-8">
          {Object.entries(devicesByType).map(([type, devicesOfType]) => {
            const deviceTypeConfig = getDeviceTypeConfig(type);
            const Icon = deviceTypeConfig?.icon;
            
            return (
              <div key={type} className="space-y-4">
                <div className="flex items-center gap-2">
                  {Icon && <Icon className="h-5 w-5" />}
                  <h2 className="text-xl font-semibold">
                    {deviceTypeConfig?.label || type}
                  </h2>
                  <span className="text-muted-foreground text-sm">
                    ({devicesOfType.length})
                  </span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {devicesOfType.map((device) => (
                    <Card key={device.object_id}>
                      <CardHeader>
                        <CardTitle>{device.name || device.object_id}</CardTitle>
                        <CardDescription>
                          ID: {device.object_id}
                          {device.sensor_type && ` · 类型: ${device.sensor_type}`}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-sm text-muted-foreground">
                          {device.last_seen ? (
                            <p>最后活动: {new Date(device.last_seen).toLocaleString()}</p>
                          ) : (
                            <p>尚未连接</p>
                          )}
                        </div>
                      </CardContent>
                      <CardFooter>
                        <Button asChild variant="outline" className="w-full">
                          <Link href={`/devices/${device.object_id}`}>
                            <ExternalLink className="mr-1 h-4 w-4" />
                            查看详情
                          </Link>
                        </Button>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
} 