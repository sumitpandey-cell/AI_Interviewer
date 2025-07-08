
import { Award, Star, Zap, Target, Trophy, Medal } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const GamifiedBadges = () => {
  const badges = [
    {
      icon: Trophy,
      name: 'High Performer',
      description: '5 interviews with 8+ score',
      earned: true,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/20',
    },
    {
      icon: Zap,
      name: 'Consistency Streak',
      description: '7 days in a row',
      earned: true,
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/20',
    },
    {
      icon: Target,
      name: 'Perfect Score',
      description: 'Score 10/10 in any category',
      earned: false,
      color: 'text-green-500',
      bgColor: 'bg-green-500/20',
    },
    {
      icon: Medal,
      name: 'Interview Master',
      description: '50 completed interviews',
      earned: false,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/20',
    },
  ];

  return (
    <Card className="bg-card-bg border-primary/20">
      <CardHeader>
        <CardTitle className="text-lg font-lovable text-white flex items-center space-x-2">
          <Star className="h-5 w-5 text-yellow-500" />
          <span>Achievements</span>
        </CardTitle>
        <CardDescription className="text-muted">
          Your progress milestones
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {badges.map((badge, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border transition-all duration-200 ${
                badge.earned
                  ? `${badge.bgColor} border-transparent`
                  : 'bg-primary/5 border-primary/20 opacity-60'
              }`}
            >
              <div className="flex flex-col items-center text-center space-y-2">
                <div className={`p-2 rounded-full ${badge.bgColor}`}>
                  <badge.icon className={`h-5 w-5 ${badge.color}`} />
                </div>
                <div>
                  <p className={`font-medium text-sm ${badge.earned ? 'text-white' : 'text-muted'}`}>
                    {badge.name}
                  </p>
                  <p className="text-xs text-muted">{badge.description}</p>
                </div>
                {badge.earned && (
                  <Badge className="bg-green-500/20 text-green-500 text-xs">
                    Earned
                  </Badge>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-primary/20">
          <div className="text-center">
            <p className="text-white font-medium">Progress to next level</p>
            <div className="mt-2 w-full bg-primary/20 rounded-full h-2">
              <div className="bg-gradient-to-r from-primary to-secondary h-2 rounded-full w-3/4"></div>
            </div>
            <p className="text-muted text-sm mt-1">3 more interviews to unlock Interview Master</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default GamifiedBadges;
