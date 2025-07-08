
import { TrendingUp, TrendingDown, Target, Clock } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface PerformanceAnalyticsProps {
  expanded?: boolean;
}

const PerformanceAnalytics = ({ expanded = false }: PerformanceAnalyticsProps) => {
  const categoryData = [
    { name: 'Frontend', score: 8.5, trend: 'up', change: '+12%' },
    { name: 'Backend', score: 7.2, trend: 'down', change: '-5%' },
    { name: 'HR', score: 9.1, trend: 'up', change: '+8%' },
    { name: 'DSA', score: 6.8, trend: 'up', change: '+15%' },
  ];

  const timeFilters = ['Week', 'Month', 'All Time'];

  return (
    <Card className="bg-card-bg border-primary/20">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-xl font-lovable text-white flex items-center space-x-2">
              <TrendingUp className="h-6 w-6 text-secondary" />
              <span>Performance Analytics</span>
            </CardTitle>
            <CardDescription className="text-muted">
              Track your progress across different categories
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            {timeFilters.map((filter) => (
              <Button
                key={filter}
                variant="outline"
                size="sm"
                className="border-primary/20 text-muted hover:text-white hover:border-primary/40"
              >
                {filter}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Score Trends */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {categoryData.map((category) => (
            <Card key={category.name} className="bg-primary/5 border-primary/20">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-white font-medium">{category.name}</h4>
                  <div className="flex items-center space-x-1">
                    {category.trend === 'up' ? (
                      <TrendingUp className="h-4 w-4 text-green-500" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-500" />
                    )}
                    <span className={`text-sm ${category.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                      {category.change}
                    </span>
                  </div>
                </div>
                <div className="text-2xl font-bold text-white mb-2">{category.score}/10</div>
                <div className="w-full bg-primary/20 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-primary to-secondary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(category.score / 10) * 100}%` }}
                  ></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="p-6 text-center">
              <div className="bg-secondary/20 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Target className="h-8 w-8 text-secondary" />
              </div>
              <h3 className="text-white font-medium mb-2">Accuracy Rate</h3>
              <p className="text-3xl font-bold text-secondary mb-1">87%</p>
              <p className="text-muted text-sm">+5% from last month</p>
            </CardContent>
          </Card>

          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="p-6 text-center">
              <div className="bg-primary/20 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Clock className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-white font-medium mb-2">Avg Response Time</h3>
              <p className="text-3xl font-bold text-primary mb-1">2.3s</p>
              <p className="text-muted text-sm">-0.5s improvement</p>
            </CardContent>
          </Card>

          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="p-6 text-center">
              <div className="bg-green-500/20 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <TrendingUp className="h-8 w-8 text-green-500" />
              </div>
              <h3 className="text-white font-medium mb-2">Improvement Rate</h3>
              <p className="text-3xl font-bold text-green-500 mb-1">+23%</p>
              <p className="text-muted text-sm">This month</p>
            </CardContent>
          </Card>
        </div>

        {/* Strengths & Areas to Improve */}
        {expanded && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="bg-green-500/5 border-green-500/20">
              <CardHeader>
                <CardTitle className="text-green-500 text-lg">Top Strengths</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-white">Problem Solving</span>
                    <Badge className="bg-green-500/20 text-green-500">Strong</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-white">Communication</span>
                    <Badge className="bg-green-500/20 text-green-500">Excellent</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-white">Technical Knowledge</span>
                    <Badge className="bg-green-500/20 text-green-500">Strong</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-yellow-500/5 border-yellow-500/20">
              <CardHeader>
                <CardTitle className="text-yellow-500 text-lg">Areas to Improve</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-white">Time Management</span>
                    <Badge className="bg-yellow-500/20 text-yellow-500">Focus</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-white">Algorithm Complexity</span>
                    <Badge className="bg-yellow-500/20 text-yellow-500">Practice</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-white">System Design</span>
                    <Badge className="bg-yellow-500/20 text-yellow-500">Study</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PerformanceAnalytics;
