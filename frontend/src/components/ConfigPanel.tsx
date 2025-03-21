"use client"

import React, { useState } from 'react';
import { useConfig } from '@/providers/ConfigProvider';
import { updateApiBaseUrl } from '@/services/api';
import { Settings, X } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { toast } from '@/components/ui/use-toast';
import { DialogClose } from '@radix-ui/react-dialog';

export function ConfigPanel() {
  const { 
    debugMode, 
    setDebugMode, 
    apiEndpoint, 
    setApiEndpoint, 
    saveConfig 
  } = useConfig();
  
  const [tempApiEndpoint, setTempApiEndpoint] = useState(apiEndpoint);
  const [isOpen, setIsOpen] = useState(false);

  const handleSave = () => {
    setApiEndpoint(tempApiEndpoint);
    updateApiBaseUrl(tempApiEndpoint);
    saveConfig();
    setIsOpen(false);
    toast({
      title: "配置已保存",
      description: "您的设置已成功更新。",
    });
  };

  const handleDialogOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (open) {
      setTempApiEndpoint(apiEndpoint);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleDialogOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon" className="rounded-full">
          <Settings className="h-5 w-5" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>系统配置</DialogTitle>
          <DialogClose className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
            <X className="h-4 w-4" />
            <span className="sr-only">关闭</span>
          </DialogClose>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="debugMode" className="col-span-2">
              调试模式
            </Label>
            <div className="col-span-2 flex items-center justify-end space-x-2">
              <Switch
                id="debugMode"
                checked={debugMode}
                onCheckedChange={(checked) => {
                  setDebugMode(checked);
                  saveConfig();
                }}
              />
              <Label htmlFor="debugMode">{debugMode ? '开启' : '关闭'}</Label>
            </div>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="apiEndpoint" className="col-span-4">
              API 服务端点
            </Label>
            <Input
              id="apiEndpoint"
              value={tempApiEndpoint}
              onChange={(e) => setTempApiEndpoint(e.target.value)}
              className="col-span-4"
              placeholder="http://localhost:8000"
            />
          </div>
        </div>
        <div className="flex justify-end">
          <Button type="submit" onClick={handleSave}>保存设置</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
} 