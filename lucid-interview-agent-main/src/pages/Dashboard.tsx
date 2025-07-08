
import { useState } from 'react';
import { Bell, Search, Moon, Sun } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent } from '@/components/ui/tabs';
import DashboardSidebar from '@/components/dashboard/DashboardSidebar';
import StartInterviewCard from '@/components/dashboard/StartInterviewCard';
import InterviewHistoryPanel from '@/components/dashboard/InterviewHistoryPanel';
import PerformanceAnalytics from '@/components/dashboard/PerformanceAnalytics';
import RecentFeedback from '@/components/dashboard/RecentFeedback';
import QuickActions from '@/components/dashboard/QuickActions';
import GamifiedBadges from '@/components/dashboard/GamifiedBadges';
import DashboardStats from '@/components/dashboard/DashboardStats';

const Dashboard = () => {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-dark-bg text-white flex">
      <DashboardSidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header Bar */}
        <header className="bg-card-bg/50 backdrop-blur-md border-b border-primary/20 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-lovable text-white">Hi Ujjawal 👋</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted h-4 w-4" />
                <Input 
                  placeholder="Search interviews, reports..." 
                  className="pl-10 w-80 bg-card-bg border-primary/20 focus:border-primary"
                />
              </div>
              
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 bg-secondary text-xs rounded-full h-4 w-4 flex items-center justify-center">3</span>
              </Button>
              
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={() => setIsDarkMode(!isDarkMode)}
              >
                {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </Button>
              
              <Avatar className="border-2 border-primary/30">
                <AvatarImage src="/placeholder.svg" />
                <AvatarFallback className="bg-primary text-white">UJ</AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-7xl mx-auto">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsContent value="overview" className="space-y-6">
                {/* Welcome Section */}
                <div className="mb-8">
                  <h2 className="text-3xl font-lovable text-white mb-2">Your Dashboard</h2>
                  <p className="text-muted text-lg">Track your progress and start your next interview</p>
                </div>

                {/* Quick Stats */}
                <DashboardStats />

                {/* Main Dashboard Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Left Column */}
                  <div className="lg:col-span-2 space-y-6">
                    <StartInterviewCard />
                    <InterviewHistoryPanel />
                  </div>

                  {/* Right Column */}
                  <div className="space-y-6">
                    <QuickActions />
                    <GamifiedBadges />
                    <RecentFeedback />
                  </div>
                </div>

                {/* Analytics Section */}
                <PerformanceAnalytics />
              </TabsContent>

              <TabsContent value="start">
                <div className="max-w-4xl mx-auto">
                  <StartInterviewCard />
                </div>
              </TabsContent>

              <TabsContent value="analytics">
                <PerformanceAnalytics expanded />
              </TabsContent>

              <TabsContent value="history">
                <InterviewHistoryPanel expanded />
              </TabsContent>

              <TabsContent value="questions">
                <div className="text-center py-12">
                  <h2 className="text-2xl font-lovable text-white mb-4">Question Bank</h2>
                  <p className="text-muted">Coming soon...</p>
                </div>
              </TabsContent>

              <TabsContent value="profile">
                <div className="text-center py-12">
                  <h2 className="text-2xl font-lovable text-white mb-4">Profile</h2>
                  <p className="text-muted">Coming soon...</p>
                </div>
              </TabsContent>

              <TabsContent value="settings">
                <div className="text-center py-12">
                  <h2 className="text-2xl font-lovable text-white mb-4">Settings</h2>
                  <p className="text-muted">Coming soon...</p>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
