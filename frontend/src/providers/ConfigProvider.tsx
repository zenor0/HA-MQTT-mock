"use client"
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface ConfigContextType {
  debugMode: boolean;
  setDebugMode: (value: boolean) => void;
  apiEndpoint: string;
  setApiEndpoint: (value: string) => void;
  saveConfig: () => void;
}

const defaultConfig: Omit<ConfigContextType, 'setDebugMode' | 'setApiEndpoint' | 'saveConfig'> = {
  debugMode: false,
  apiEndpoint: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
};

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export function useConfig() {
  const context = useContext(ConfigContext);
  if (context === undefined) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
}

interface ConfigProviderProps {
  children: ReactNode;
}

export function ConfigProvider({ children }: ConfigProviderProps) {
  const [debugMode, setDebugMode] = useState(defaultConfig.debugMode);
  const [apiEndpoint, setApiEndpoint] = useState(defaultConfig.apiEndpoint);

  // 从localStorage加载配置
  useEffect(() => {
    const savedConfig = localStorage.getItem('appConfig');
    if (savedConfig) {
      try {
        const parsedConfig = JSON.parse(savedConfig);
        if (parsedConfig.debugMode !== undefined) {
          setDebugMode(parsedConfig.debugMode);
        }
        if (parsedConfig.apiEndpoint) {
          setApiEndpoint(parsedConfig.apiEndpoint);
        }
      } catch (error) {
        console.error('Failed to parse saved config:', error);
      }
    }
  }, []);

  // 保存配置到localStorage
  const saveConfig = () => {
    const configToSave = {
      debugMode,
      apiEndpoint,
    };
    localStorage.setItem('appConfig', JSON.stringify(configToSave));
  };

  const value = {
    debugMode,
    setDebugMode,
    apiEndpoint,
    setApiEndpoint,
    saveConfig,
  };

  return (
    <ConfigContext.Provider value={value}>
      {children}
    </ConfigContext.Provider>
  );
} 