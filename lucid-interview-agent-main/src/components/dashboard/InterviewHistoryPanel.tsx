
import { useState } from 'react';
import { Eye, RotateCcw, Share, Download, Calendar, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

interface InterviewHistoryPanelProps {
  expanded?: boolean;
}

const InterviewHistoryPanel = ({ expanded = false }: InterviewHistoryPanelProps) => {
  const [view, setView] = useState<'table' | 'cards'>('table');

  const interviews = [
    {
      id: 1,
      type: 'Frontend',
      score: 8.5,
      date: '2024-01-15',
      status: 'completed',
      duration: '45 min',
      questions: 12,
      category: 'React/JS'
    },
    {
      id: 2,
      type: 'Backend',
      score: 7.2,
      date: '2024-01-14',
      status: 'completed',
      duration: '38 min',
      questions: 10,
      category: 'Node.js'
    },
    {
      id: 3,
      type: 'HR',
      score: 9.1,
      date: '2024-01-13',
      status: 'completed',
      duration: '25 min',
      questions: 8,
      category: 'Behavioral'
    },
    {
      id: 4,
      type: 'DSA',
      score: 6.8,
      date: '2024-01-12',
      status: 'incomplete',
      duration: '20 min',
      questions: 5,
      category: 'Arrays'
    },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-500';
    if (score >= 6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      completed: 'bg-green-500/20 text-green-500',
      incomplete: 'bg-yellow-500/20 text-yellow-500',
      failed: 'bg-red-500/20 text-red-500'
    };
    return variants[status as keyof typeof variants] || variants.completed;
  };

  return (
    <Card className="bg-card-bg border-primary/20">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-xl font-lovable text-white flex items-center space-x-2">
              <Calendar className="h-6 w-6 text-primary" />
              <span>Interview History</span>
            </CardTitle>
            <CardDescription className="text-muted">
              Review your past interviews and track progress
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant={view === 'table' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setView('table')}
            >
              Table
            </Button>
            <Button
              variant={view === 'cards' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setView('cards')}
            >
              Cards
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {view === 'table' ? (
          <div className="rounded-lg border border-primary/20">
            <Table>
              <TableHeader>
                <TableRow className="border-primary/20">
                  <TableHead className="text-white">Type</TableHead>
                  <TableHead className="text-white">Score</TableHead>
                  <TableHead className="text-white">Date</TableHead>
                  <TableHead className="text-white">Status</TableHead>
                  <TableHead className="text-white">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {interviews.slice(0, expanded ? interviews.length : 3).map((interview) => (
                  <TableRow key={interview.id} className="border-primary/20 hover:bg-primary/5">
                    <TableCell>
                      <div>
                        <p className="text-white font-medium">{interview.type}</p>
                        <p className="text-muted text-sm">{interview.category}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <span className={`font-bold text-lg ${getScoreColor(interview.score)}`}>
                          {interview.score}/10
                        </span>
                        {interview.score >= 8 && <Star className="h-4 w-4 text-yellow-500 fill-current" />}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="text-white">{interview.date}</p>
                        <p className="text-muted text-sm">{interview.duration}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusBadge(interview.status)}>
                        {interview.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <RotateCcw className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Share className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {interviews.slice(0, expanded ? interviews.length : 4).map((interview) => (
              <Card key={interview.id} className="bg-primary/5 border-primary/20 hover:border-primary/40 transition-all duration-200">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h4 className="text-white font-medium">{interview.type}</h4>
                      <p className="text-muted text-sm">{interview.category}</p>
                    </div>
                    <Badge className={getStatusBadge(interview.status)}>
                      {interview.status}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between mb-3">
                    <span className={`font-bold text-xl ${getScoreColor(interview.score)}`}>
                      {interview.score}/10
                    </span>
                    <span className="text-muted text-sm">{interview.date}</span>
                  </div>
                  <div className="flex items-center justify-between text-muted text-sm mb-4">
                    <span>{interview.duration}</span>
                    <span>{interview.questions} questions</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button variant="ghost" size="sm" className="flex-1">
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button variant="ghost" size="sm" className="flex-1">
                      <RotateCcw className="h-4 w-4 mr-1" />
                      Retake
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
        
        {!expanded && (
          <div className="mt-4 text-center">
            <Button variant="outline" className="border-primary/20 text-primary hover:bg-primary/10">
              View All History
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default InterviewHistoryPanel;
