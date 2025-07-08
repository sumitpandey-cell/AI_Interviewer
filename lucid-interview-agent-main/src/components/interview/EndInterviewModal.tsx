
import { CheckCircle, Clock, MessageSquare, Download, RotateCcw, Share2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

interface EndInterviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  duration: number;
  questionsAnswered: number;
  totalQuestions: number;
  onGoToDashboard: () => void;
}

const EndInterviewModal = ({ 
  isOpen, 
  onClose, 
  duration, 
  questionsAnswered, 
  totalQuestions,
  onGoToDashboard 
}: EndInterviewModalProps) => {
  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const completionPercentage = Math.round((questionsAnswered / totalQuestions) * 100);

  const handleDownloadReport = () => {
    // Mock download functionality
    console.log('Downloading interview report...');
  };

  const handleShareFeedback = () => {
    // Mock share functionality
    console.log('Sharing feedback...');
  };

  const handleRetakeInterview = () => {
    // Mock retake functionality
    window.location.reload();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl bg-card-bg border-primary/20">
        <DialogHeader>
          <DialogTitle className="text-2xl font-lovable text-white flex items-center space-x-2">
            <CheckCircle className="h-6 w-6 text-green-400" />
            <span>Interview Complete!</span>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-3 gap-4">
            <Card className="bg-primary/10 border-primary/20">
              <CardContent className="p-4 text-center">
                <Clock className="h-6 w-6 text-primary mx-auto mb-2" />
                <p className="text-2xl font-bold text-white">{formatTime(duration)}</p>
                <p className="text-sm text-muted">Total Duration</p>
              </CardContent>
            </Card>

            <Card className="bg-secondary/10 border-secondary/20">
              <CardContent className="p-4 text-center">
                <MessageSquare className="h-6 w-6 text-secondary mx-auto mb-2" />
                <p className="text-2xl font-bold text-white">{questionsAnswered}</p>
                <p className="text-sm text-muted">Questions Answered</p>
              </CardContent>
            </Card>

            <Card className="bg-green-500/10 border-green-500/20">
              <CardContent className="p-4 text-center">
                <CheckCircle className="h-6 w-6 text-green-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-white">{completionPercentage}%</p>
                <p className="text-sm text-muted">Completion Rate</p>
              </CardContent>
            </Card>
          </div>

          {/* Feedback Preview */}
          <Card className="bg-primary/5 border-primary/10">
            <CardHeader>
              <CardTitle className="text-lg text-white">Quick Feedback</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm text-white">Strong communication skills demonstrated</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm text-white">Good technical knowledge for the role</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                  <span className="text-sm text-white">Consider providing more specific examples</span>
                </div>
              </div>
              <p className="text-xs text-muted mt-4">
                Full detailed report will be available shortly
              </p>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <Button
              variant="outline"
              onClick={handleDownloadReport}
              className="border-primary/20 hover:border-primary/40"
            >
              <Download className="h-4 w-4 mr-2" />
              Download Report
            </Button>

            <Button
              variant="outline"
              onClick={handleShareFeedback}
              className="border-secondary/20 hover:border-secondary/40 text-secondary"
            >
              <Share2 className="h-4 w-4 mr-2" />
              Share Feedback
            </Button>

            <Button
              variant="outline"
              onClick={handleRetakeInterview}
              className="border-yellow-500/20 hover:border-yellow-500/40 text-yellow-400"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Retake Interview
            </Button>

            <Button
              onClick={onGoToDashboard}
              className="bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90"
            >
              Back to Dashboard
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default EndInterviewModal;
