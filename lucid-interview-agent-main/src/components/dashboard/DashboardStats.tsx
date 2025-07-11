
import { Play, TrendingUp, Award, Clock } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface DashboardStatsProps {
  totalInterviews: number;
  completedInterviews: number;
  averageScore: number;
  totalQuestionsAnswered: number;
}

const DashboardStats = ({
  totalInterviews = 0,
  completedInterviews = 0,
  averageScore = 0,
  totalQuestionsAnswered = 0
}: DashboardStatsProps) => {
  const stats = [
    {
      title: 'Total Interviews',
      value: totalInterviews.toString(),
      icon: Play,
      color: 'text-primary',
      bgColor: 'bg-primary/20'
    },
    {
      title: 'Average Score',
      value: `${(averageScore / 10).toFixed(1)}/10`,
      icon: TrendingUp,
      color: 'text-secondary',
      bgColor: 'bg-secondary/20'
    },
    {
      title: 'Completed',
      value: completedInterviews.toString(),
      icon: Award,
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/20'
    },
    {
      title: 'Questions Answered',
      value: totalQuestionsAnswered.toString(),
      icon: Clock,
      color: 'text-green-500',
      bgColor: 'bg-green-500/20'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <Card key={index} className="bg-card-bg border-primary/20 hover:border-primary/40 transition-all duration-300">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-muted text-sm">{stat.title}</p>
                <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
              </div>
              <div className={`${stat.bgColor} p-3 rounded-lg`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default DashboardStats;
