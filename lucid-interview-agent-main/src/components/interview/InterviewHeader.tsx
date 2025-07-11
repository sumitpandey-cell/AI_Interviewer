import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import InterviewTimer from '@/components/interview/InterviewTimer';

interface HeaderProps {
  position: string;
  company: string;
  duration: number;
  isRecording: boolean;
  onNavigateBack: () => void;
}

/**
 * Header component for the interview view
 */
const InterviewHeader = ({
  position,
  company,
  duration,
  isRecording,
  onNavigateBack
}: HeaderProps) => {
  return (
    <header className="bg-[#262933]/80 backdrop-blur-xl border-b border-primary/10 px-6 py-4 shadow-2xl">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={onNavigateBack}
            className="text-muted hover:text-white hover:bg-primary/10 transition-all duration-300"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="space-y-1">
            <h1 className="text-xl font-bold text-white flex items-center space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
              <span>AI Interview Session</span>
            </h1>
            <p className="text-sm text-cyan-400 font-medium">
              {position} {company ? `- ${company}` : ''}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-6">
          <InterviewTimer duration={duration} />
          {isRecording && (
            <div className="flex items-center space-x-3 bg-red-500/10 px-3 py-2 rounded-full border border-red-500/20">
              <div className="relative">
                <div className="w-3 h-3 bg-red-400 rounded-full animate-pulse"></div>
                <div className="absolute inset-0 w-3 h-3 bg-red-400 rounded-full animate-ping opacity-75"></div>
              </div>
              <span className="text-sm font-medium text-red-400">Recording</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default InterviewHeader;
