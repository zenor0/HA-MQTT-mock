# MQTT设备监控面板

这是一个用于监控和控制Home Assistant MQTT设备模拟器的前端应用。

## 功能特性

- 查看所有模拟设备列表
- 创建新的模拟设备
- 查看和编辑设备详情
- 实时监控和更新设备状态
- 重新加载设备配置

## 技术栈

- Next.js 15
- React 19
- TypeScript
- TailwindCSS
- Tanstack React Query
- Axios

## 开发环境设置

### 前提条件

- Node.js 18+
- pnpm

### 安装

```bash
# 安装依赖
pnpm install
```

### 配置

创建一个`.env.local`文件，设置API URL：

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 运行开发服务器

```bash
pnpm dev
```

应用将在 [http://localhost:3000](http://localhost:3000) 上运行。

### 构建生产版本

```bash
pnpm build
pnpm start
```

## API文档

应用使用以下API端点与后端通信：

- `GET /api/devices` - 获取所有设备列表
- `POST /api/devices` - 创建新设备
- `GET /api/devices/{device_id}` - 获取指定设备详情
- `PUT /api/devices/{device_id}` - 更新设备配置
- `DELETE /api/devices/{device_id}` - 删除设备
- `GET /api/devices/{device_id}/state` - 获取设备状态
- `PUT /api/devices/{device_id}/state` - 更新设备状态
- `POST /api/reload` - 重新加载设备配置
