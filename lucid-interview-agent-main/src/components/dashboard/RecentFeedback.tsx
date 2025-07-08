
import { MessageSquare, Download, Share } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const RecentFeedback = () => {
  return (
    <Card className="bg-card-bg border-primary/20">
      <CardHeader>
        <CardTitle className="text-lg font-lovable text-white flex items-center space-x-2">
          <MessageSquare className="h-5 w-5 text-secondary" />
          <span>Recent Feedback</span>
        </CardTitle>
        <CardDescription className="text-muted">
          AI insights from your latest interview
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Interview Summary */}
        <div className="p-4 bg-primary/5 rounded-lg border border-primary/20">
          <div className="flex items-center justify-between mb-3">
            <Badge className="bg-blue-500/20 text-blue-500">Frontend Interview</Badge>
            <span className="text-green-500 font-bold">8.5/10</span>
          </div>
          <p className="text-white text-sm mb-2">
            <strong>Overall Performance:</strong> Excellent understanding of React concepts and clean code practices.
          </p>
        </div>

        {/* Strengths */}
        <div className="space-y-2">
          <h4 className="text-white font-medium text-sm">✅ Strengths</h4>
          <ul className="text-muted text-sm space-y-1">
            <li>• Clear explanation of React hooks</li>
            <li>• Good problem-solving approach</li>
            <li>• Well-structured code organization</li>
          </ul>
        </div>

        {/* Areas to Improve */}
        <div className="space-y-2">
          <h4 className="text-white font-medium text-sm">🎯 Areas to Improve</h4>
          <ul className="text-muted text-sm space-y-1">
            <li>• Consider edge cases in solutions</li>
            <li>• Practice time complexity analysis</li>
            <li>• Improve communication speed</li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2 pt-2">
          <Button variant="outline" size="sm" className="flex-1 border-primary/20 text-muted hover:text-white">
            <Download className="h-4 w-4 mr-1" />
            PDF
          </Button>
          <Button variant="outline" size="sm" className="flex-1 border-primary/20 text-muted hover:text-white">
            <Share className="h-4 w-4 mr-1" />
            Share
          </Button>
        </div>

        {/* Mini Tip */}
        <div className="p-3 bg-secondary/10 rounded-lg border border-secondary/20">
          <h4 className="text-secondary font-medium text-sm mb-1">💡 Today's Tip</h4>
          <p className="text-muted text-xs">
            Practice explaining your thought process out loud - it helps interviewers follow your logic!
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default RecentFeedback;
