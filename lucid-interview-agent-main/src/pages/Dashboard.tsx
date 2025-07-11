import { useState, useEffect } from 'react';
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
import { AuthAPI, API_BASE_URL } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchUserInterviews } from '@/store/slices/interviewSlice';
import { fetchUserInfo } from '@/store/slices/authSlice';
import { fetchDashboardData } from '@/store/slices/dashboardSlice';

const Dashboard = () => {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');

  // Get state from Redux
  const { user: userProfile, loading: userLoading } = useAppSelector(state => state.auth);
  const { interviews, loading: interviewsLoading } = useAppSelector(state => state.interview);
  const { dashboardData, loading: dashboardLoading } = useAppSelector(state => state.dashboard);

  const { toast } = useToast();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  // Debug: Log when search query changes or interviews load
  useEffect(() => {
    

    if (searchQuery && interviews && Array.isArray(interviews) && interviews.length > 0) {
      const filtered = interviews.filter(interview =>
        (interview.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (interview.position || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (interview.company_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (interview.description || '').toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
  }, [searchQuery, interviews, interviewsLoading, activeTab]);

  const isLoading = interviewsLoading || dashboardLoading || userLoading;

  // Fetch data from backend using Redux
  useEffect(() => {
    if (!AuthAPI.isAuthenticated()) {
      navigate('/');
      return;
    }


    // Load user data from Redux
    const loadDashboardData = async () => {
      try {
        // Fetch user info first
        console.log("[DASHBOARD LOAD] Fetching user info...");
        const userResult = await dispatch(fetchUserInfo()).unwrap();
        console.log("[DASHBOARD LOAD] User profile loaded:", userResult);

        // Fetch interviews with explicit error handling
        console.log("[DASHBOARD LOAD] Fetching interviews...");
        try {
          const interviewsResult = await dispatch(fetchUserInterviews()).unwrap();
          console.log("[DASHBOARD LOAD] Interviews loaded:", interviewsResult);
          console.log("[DASHBOARD LOAD] Interviews count:", interviewsResult.length);

          // Force refresh Redux state if needed
          if (interviewsResult.length > 0 && (!interviews || interviews.length === 0)) {
            console.log("[DASHBOARD LOAD] Redux state not updated with interviews, consider component refresh");
          }
        } catch (interviewError) {
          console.error("[DASHBOARD LOAD] Failed to load interviews:", interviewError);
          toast({
            title: "Interview data error",
            description: "There was a problem loading your interviews.",
            variant: "destructive"
          });
        }

        // Fetch dashboard data
        console.log("[DASHBOARD LOAD] Fetching dashboard data...");
        const dashboardResult = await dispatch(fetchDashboardData()).unwrap();
        console.log("[DASHBOARD LOAD] Dashboard data loaded:", dashboardResult);

      } catch (error) {
        console.error('[DASHBOARD LOAD] Failed to fetch dashboard data:', error);
        toast({
          variant: "destructive",
          title: "Failed to load dashboard",
          description: "Please try refreshing the page or log in again.",
        });

        // If there's an authentication error, redirect to login
        if (error instanceof Error &&
          (error.message.includes('401') ||
            error.message.includes('Failed to fetch user profile: 401'))) {
          console.log("[DASHBOARD LOAD] Auth error detected, logging out");
          AuthAPI.logout();
          navigate('/');
        }
      }
    };

    loadDashboardData();
  }, [dispatch, navigate, toast]);

  // Debug API URL
  useEffect(() => {
    console.log("API Base URL:", API_BASE_URL);
    console.log("Authentication status:", AuthAPI.isAuthenticated());
  }, []);

  // Function to get user initials for avatar
  const getUserInitials = () => {
    if (!userProfile?.full_name) return 'U';

    const nameParts = userProfile.full_name.split(' ');
    if (nameParts.length >= 2) {
      return `${nameParts[0][0]}${nameParts[1][0]}`.toUpperCase();
    }

    return nameParts[0][0].toUpperCase();
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="flex flex-col items-center">
          <Loader2 className="h-12 w-12 text-primary animate-spin mb-4" />
          <p className="text-white text-lg">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-bg text-white flex">
      <DashboardSidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header Bar */}
        <header className="bg-card-bg/50 backdrop-blur-md border-b border-primary/20 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-lovable text-white">
                Hi {userProfile?.full_name?.split(' ')[0] || 'there'} 👋
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted h-4 w-4" />
                <Input
                  placeholder="Search interviews, reports..."
                  className="pl-10 w-80 bg-card-bg border-primary/20 focus:border-primary"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 bg-secondary text-xs rounded-full h-4 w-4 flex items-center justify-center">
                  {interviews.filter(i => i.status === 'new' || i.status === 'in_progress').length || 0}
                </span>
              </Button>

              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsDarkMode(!isDarkMode)}
              >
                {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </Button>

              <div className="flex items-center space-x-2 pl-4 border-l border-primary/20">
                <Avatar>
                  <AvatarImage src={userProfile?.avatar_url} />
                  <AvatarFallback className="bg-gradient-to-br from-primary to-secondary">
                    {getUserInitials()}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-medium">{userProfile?.full_name}</p>
                  <p className="text-xs text-muted">{userProfile?.email}</p>

                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Dashboard Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <Tabs value={activeTab}>
            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-8 mt-0">
              {/* Dashboard Stats */}
              {/* Always show DashboardStats with proper fallbacks if dashboardData is not available */}
              <DashboardStats
                totalInterviews={(dashboardData?.total_interviews !== undefined) ? dashboardData.total_interviews : interviews.length}
                completedInterviews={(dashboardData?.completed_interviews !== undefined) ? dashboardData.completed_interviews : interviews.filter(i => i.status === 'completed').length}
                averageScore={(dashboardData?.average_score !== undefined) ? dashboardData.average_score : 0}
                totalQuestionsAnswered={(dashboardData?.total_questions_answered !== undefined) ? dashboardData.total_questions_answered : 0}
              />

              {/* Main content area with cards */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left column */}
                <div className="space-y-6 lg:col-span-2">
                  {/* Start Interview Card */}
                  <StartInterviewCard />

                  {/* Performance Analytics */}
                  <PerformanceAnalytics
                    interviews={interviews}
                  />

                  {/* Recent Feedback */}
                  <RecentFeedback
                    interviews={interviews.filter(i => i.status === 'completed').slice(0, 3)}
                  />
                </div>

                {/* Right column */}
                <div className="space-y-10">
                  {/* Quick Actions */}
                  <QuickActions />

                  {/* Gamified Badges */}
                  <GamifiedBadges
                    completedInterviews={interviews.filter(i => i.status === 'completed').length}
                  />
                </div>
              </div>

            </TabsContent>

            <TabsContent value="start">
              <StartInterviewCard />
            </TabsContent>

            <TabsContent value='history'>
              {isLoading ? (
                <div className="min-h-screen bg-dark-bg flex items-center justify-center">
                  <div className="flex flex-col items-center">
                    <Loader2 className="h-12 w-12 text-primary animate-spin mb-4" />
                    <p className="text-white text-lg">Loading your dashboard...</p>
                  </div>
                </div>
              ) : (
                <InterviewHistoryPanel
                  expanded={true} // Show more interviews
                  interviews={interviews || []} // Ensure it's not undefined
                  filteredInterviews={
                    searchQuery ?
                      interviews.filter(interview =>
                        (interview.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                        (interview.position || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                        (interview.company_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                        (interview.description || '').toLowerCase().includes(searchQuery.toLowerCase())
                      ) :
                      interviews
                  }
                />
              )}
            </TabsContent>

            <TabsContent value="analytics">
              <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
                <div className="text-6xl font-bold text-primary">🚧</div>
                <h2 className="text-3xl font-semibold text-center">Analytics Coming Soon</h2>
                <p className="text-muted text-center max-w-md">
                  We're working hard to bring you detailed performance analytics and insights. Stay tuned!
                </p>
              </div>
            </TabsContent>
            <TabsContent value="questions">
              <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
                <div className="text-6xl font-bold text-primary">🚧</div>
                <h2 className="text-3xl font-semibold text-center">Question Coming Soon</h2>
                <p className="text-muted text-center max-w-md">
                  We're working hard to bring you detailed performance analytics and insights. Stay tuned!
                </p>
              </div>
            </TabsContent>
            <TabsContent value="profile">
              <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
                <div className="text-6xl font-bold text-primary">🚧</div>
                <h2 className="text-3xl font-semibold text-center">Profile Coming Soon</h2>
                <p className="text-muted text-center max-w-md">
                  We're working hard to bring you detailed performance analytics and insights. Stay tuned!
                </p>
              </div>
            </TabsContent>
            <TabsContent value="settings">
              <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
                <div className="text-6xl font-bold text-primary">🚧</div>
                <h2 className="text-3xl font-semibold text-center">Settings Coming Soon</h2>
                <p className="text-muted text-center max-w-md">
                  We're working hard to bring you Settings. Stay tuned!
                </p>
              </div>
            </TabsContent>
          </Tabs>
          
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
