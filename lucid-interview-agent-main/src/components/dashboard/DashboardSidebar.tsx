
import { Home, Play, History, BarChart3, BookOpen, Settings, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DashboardSidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const DashboardSidebar = ({ activeTab, setActiveTab }: DashboardSidebarProps) => {
  const navigation = [
    { id: 'overview', name: 'Dashboard', icon: Home },
    { id: 'start', name: 'Start Interview', icon: Play },
    { id: 'history', name: 'Interview History', icon: History },
    { id: 'analytics', name: 'Analytics', icon: BarChart3 },
    { id: 'questions', name: 'Question Bank', icon: BookOpen },
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'settings', name: 'Settings', icon: Settings },
  ];

  return (
    <div className="w-64 bg-card-bg border-r border-primary/20 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-primary/20">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-primary to-secondary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">AI</span>
          </div>
          <span className="text-xl font-lovable text-white">InterviewAI</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigation.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => setActiveTab(item.id)}
                className={cn(
                  "w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 text-left",
                  activeTab === item.id
                    ? "bg-primary/20 text-primary border border-primary/30"
                    : "text-muted hover:text-white hover:bg-primary/10"
                )}
              >
                <item.icon className="h-5 w-5" />
                <span className="font-medium">{item.name}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-primary/20">
        <div className="flex items-center space-x-3 p-3 rounded-lg bg-primary/10">
          <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-bold">U</span>
          </div>
          <div className="flex-1">
            <p className="text-white text-sm font-medium">Ujjawal</p>
            <p className="text-muted text-xs">Pro Plan</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardSidebar;
