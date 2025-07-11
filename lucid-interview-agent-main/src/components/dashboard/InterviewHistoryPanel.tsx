import { useState, useEffect } from 'react';
import { Eye, RotateCcw, Share, Download, Calendar, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';

interface Interview {
  id: number;
  title: string;
  description?: string;
  interview_type: string;
  position: string;
  status: string;
  created_at: string;
  completed_at?: string;
  difficulty_level?: string;
  company_name?: string;
}

interface InterviewHistoryPanelProps {
  expanded?: boolean;
  interviews?: Interview[];
  filteredInterviews?: Interview[];
}

const InterviewHistoryPanel = ({ 
  expanded = false, 
  interviews = [],
  filteredInterviews
}: InterviewHistoryPanelProps) => {
  // Use filteredInterviews if provided, otherwise fallback to interviews
  const displayInterviews = filteredInterviews || interviews;
  const [view, setView] = useState<'table' | 'cards'>('table');
  const navigate = useNavigate();
  
  // Add debug logging when component renders
  console.log("[PANEL DEBUG] InterviewHistoryPanel rendering");
  console.log("[PANEL DEBUG] Props - interviews:", interviews);
  console.log("[PANEL DEBUG] Props - filteredInterviews:", filteredInterviews);
  console.log("[PANEL DEBUG] displayInterviews:", displayInterviews);
  console.log("[PANEL DEBUG] expanded:", expanded);
  
  // Monitor prop changes
  useEffect(() => {
    console.log("[PANEL DEBUG] Interviews prop changed:", interviews);
    console.log("[PANEL DEBUG] displayInterviews updated:", displayInterviews);
    
    if (interviews && interviews.length > 0) {
      console.log("[PANEL DEBUG] First interview:", interviews[0]);
    }
  }, [interviews, displayInterviews]);
  console.log("HEllo")

  // Function to format date
  const formatDate = (dateString: string) => {
    try {
      console.log("!!!!!!!!!!!!!!!",displayInterviews)
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch (e) {
      return 'Invalid date';
    }
  };
  
  // Function to get random score for demo
  const getRandomScore = () => {
    return (Math.floor(Math.random() * 30) + 70) / 10;
  };
  
  // Function to continue an interview
  const continueInterview = (id: number) => {
    navigate(`/interview?id=${id}`);
  };
  
  // If no interviews to display, show placeholder
  if (displayInterviews.length === 0) {
    return (
      <Card className="bg-card-bg border-primary/20">
        <CardHeader className="pb-3">
          <CardTitle className="text-xl text-white flex items-center justify-between">
            <span>Interview History</span>
          </CardTitle>
          <CardDescription>
            {interviews.length === 0 
              ? "No interviews yet. Start your first interview from the card above."
              : "No interviews match your search criteria."}
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  // Process interviews for display
  const processedInterviews = displayInterviews.map(interview => ({
    id: interview.id,
    type: interview.interview_type,
    score: interview.status === 'completed' ? 5 : undefined,
    date: formatDate(interview.created_at),
    status: interview.status,
    duration: '30 min', // Placeholder, replace with actual duration if available
    questions: 5, // Placeholder, replace with actual questions count if available
    category: interview.position,
    title: interview.title,
    company: interview.company_name || 'Company'
  }));

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-500';
    if (score >= 6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      completed: 'bg-green-500/20 text-green-500',
      in_progress: 'bg-yellow-500/20 text-yellow-500',
      new: 'bg-blue-500/20 text-blue-500',
      cancelled: 'bg-red-500/20 text-red-500',
    };
    
    const displayText = {
      completed: 'Completed',
      in_progress: 'In Progress',
      new: 'Not Started',
      cancelled: 'Cancelled',
    };
    
    const statusKey = status as keyof typeof variants;
    
    return (
      <Badge variant="outline" className={`${variants[statusKey] || variants.new} border-0`}>
        {displayText[statusKey] || 'Not Started'}
      </Badge>
    );
  };

  return (
    <Card className="bg-card-bg border-primary/20">
      <CardHeader className="pb-3">
        <CardTitle className="text-xl text-white flex items-center justify-between">
          <span>Interview History</span>
          <div className="flex items-center space-x-2">
            <Button variant="ghost" size="icon" onClick={() => setView('table')} className={view === 'table' ? 'bg-primary/20' : ''}>
              <Calendar className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => setView('cards')} className={view === 'cards' ? 'bg-primary/20' : ''}>
              <Star className="h-4 w-4" />
            </Button>
          </div>
        </CardTitle>
        <CardDescription>Your recent interview sessions</CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        {view === 'table' ? (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-primary/20 hover:bg-card-bg/90">
                  <TableHead>Type</TableHead>
                  <TableHead>Position</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Status</TableHead>
                  {expanded && (
                    <>
                      <TableHead>Duration</TableHead>
                      <TableHead>Score</TableHead>
                    </>
                  )}
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {processedInterviews.slice(0, expanded ? processedInterviews.length : 5).map((interview) => (
                  <TableRow key={interview.id} className="border-primary/20 hover:bg-card-bg/90">
                    <TableCell className="font-medium">{interview.type}</TableCell>
                    <TableCell>{interview.category}</TableCell>
                    <TableCell>{interview.date}</TableCell>
                    <TableCell>{getStatusBadge(interview.status)}</TableCell>
                    {expanded && (
                      <>
                        <TableCell>{interview.duration}</TableCell>
                        <TableCell>
                          {interview.score ? (
                            <span className={getScoreColor(interview.score)}>{interview.score.toFixed(1)}</span>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                      </>
                    )}
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <Button variant="ghost" size="icon">
                          <Eye className="h-4 w-4" />
                        </Button>
                        {interview.status !== 'completed' && (
                          <Button variant="ghost" size="icon" onClick={() => continueInterview(interview.id)}>
                            <RotateCcw className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
            {processedInterviews.slice(0, expanded ? processedInterviews.length : 6).map((interview) => (
              <Card key={interview.id} className="bg-card-bg/50 border-primary/20 hover:border-primary/40 transition-all duration-300">
                <CardContent className="p-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <h3 className="font-medium text-white">{interview.type}</h3>
                      <p className="text-sm text-muted">{interview.company} - {interview.category}</p>
                    </div>
                    {getStatusBadge(interview.status)}
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted">Date</span>
                      <span className="text-white">{interview.date}</span>
                    </div>
                    {interview.score && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted">Score</span>
                        <span className={getScoreColor(interview.score)}>{interview.score.toFixed(1)}/10</span>
                      </div>
                    )}
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted">Duration</span>
                      <span className="text-white">{interview.duration}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4 mr-2" />
                      View
                    </Button>
                    {interview.status !== 'completed' && (
                      <Button variant="outline" size="sm" onClick={() => continueInterview(interview.id)}>
                        <RotateCcw className="h-4 w-4 mr-2" />
                        Continue
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!expanded && processedInterviews.length > (view === 'table' ? 5 : 6) && (
          <div className="p-4 flex justify-center">
            <Button variant="outline" size="sm" className="border-primary/30 hover:border-primary/60 hover:bg-primary/10 w-full">
              View All ({processedInterviews.length})
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default InterviewHistoryPanel;
