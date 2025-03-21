import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from './card';

interface DataPoint {
  timestamp: string;
  value: number;
}

interface DeviceStateChartProps {
  title: string;
  data: DataPoint[];
  dataKey?: string;
  unit?: string;
  color?: string;
}

export function DeviceStateChart({
  title,
  data,
  dataKey = 'value',
  unit = '',
  color = 'hsl(var(--primary))',
}: DeviceStateChartProps) {
  // 格式化时间戳为更友好的格式
  const formattedData = data.map(point => ({
    ...point,
    formattedTime: new Date(point.timestamp).toLocaleTimeString(),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[200px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={formattedData}
              margin={{
                top: 5,
                right: 10,
                left: 10,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="formattedTime" 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => value.split(':').slice(0, 2).join(':')}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `${value}${unit}`}
              />
              <Tooltip 
                formatter={(value: number) => [`${value}${unit}`, title]}
                labelFormatter={(label) => `时间: ${label}`}
              />
              <Line
                type="monotone"
                dataKey={dataKey}
                stroke={color}
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
} 