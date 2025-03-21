import Link from 'next/link';
import { Home, PlusCircle } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { Button } from './ui/button';
import { ConfigPanel } from './ConfigPanel';

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between">
        <div className="flex items-center gap-2 md:gap-4">
          <Link href="/" className="flex items-center space-x-2">
            <Home className="h-5 w-5" />
            <span className="font-bold inline-block">Homie</span>
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link 
              href="/" 
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              设备列表
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-2">
          <Button asChild variant="default" size="sm">
            <Link href="/devices/new">
              <PlusCircle className="h-4 w-4 mr-1" />
              添加设备
            </Link>
          </Button>
          <ConfigPanel />
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
} 