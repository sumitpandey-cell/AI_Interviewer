
import { Play, Eye, Calendar, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const QuickActions = () => {
  const actions = [
    {
      icon: Play,
      title: 'Start Interview',
      description: 'Begin new session',
      color: 'bg-primary/20 text-primary hover:bg-primary/30',
    },
    {
      icon: Eye,
      title: 'Watch Demo',
      description: 'See how it works',
      color: 'bg-secondary/20 text-secondary hover:bg-secondary/30',
    },
    {
      icon: Eye,
      title: 'View Report',
      description: 'Latest feedback',
      color: 'bg-green-500/20 text-green-500 hover:bg-green-500/30',
    },
    {
      icon: Calendar,
      title: 'Schedule Reminder',
      description: 'Set practice time',
      color: 'bg-purple-500/20 text-purple-500 hover:bg-purple-500/30',
    },
  ];

  return (
    <Card className="bg-card-bg border-primary/20">
      <CardHeader>
        <CardTitle className="text-lg font-lovable text-white">Quick Actions</CardTitle>
        <CardDescription className="text-muted">
          Common tasks and shortcuts
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {actions.map((action, index) => (
            <Button
              key={index}
              variant="ghost"
              className={`h-auto p-4 flex flex-col items-center space-y-2 transition-all duration-200 ${action.color}`}
            >
              <action.icon className="h-6 w-6" />
              <div className="text-center">
                <p className="font-medium text-sm">{action.title}</p>
                <p className="text-xs opacity-75">{action.description}</p>
              </div>
            </Button>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-primary/20">
          <Button variant="outline" className="w-full border-primary/20 text-muted hover:text-white hover:border-primary/40">
            <Download className="h-4 w-4 mr-2" />
            Export All Reports
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default QuickActions;
