import { Mic, MicOff, FileText, RotateCcw, BookmarkMinus, Square } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ControlToolbarProps {
  isMuted: boolean;
  isAiThinking: boolean;
  isSpeaking: boolean;
  onMuteToggle: () => void;
  onShowTranscript: () => void;
  onRetryQuestion: () => void;
  onRepeatQuestion: () => void;
  onMarkDifficult: () => void;
  onEndInterview: () => void;
}

/**
 * Control toolbar component for interview actions
 */
const ControlToolbar = ({
  isMuted,
  isAiThinking,
  isSpeaking,
  onMuteToggle,
  onShowTranscript,
  onRetryQuestion,
  onRepeatQuestion,
  onMarkDifficult,
  onEndInterview
}: ControlToolbarProps) => {
  return (
    <div className="bg-[#262933]/60 backdrop-blur-xl border-t border-primary/10 p-6 shadow-2xl">
      <div className="flex items-center justify-center space-x-4">
        <Button
          variant={isMuted ? "default" : "outline"}
          size="lg"
          onClick={onMuteToggle}
          className={`transition-all duration-300 hover:scale-105 ${
            isMuted 
              ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg' 
              : 'border-primary/30 hover:border-primary/60 hover:bg-primary/10'
          }`}
        >
          {isMuted ? <MicOff className="h-5 w-5 mr-2" /> : <Mic className="h-5 w-5 mr-2" />}
          {isMuted ? 'Unmute' : 'Mute'}
        </Button>

        <Button
          variant="outline"
          size="lg"
          onClick={onShowTranscript}
          className="border-primary/30 hover:border-primary/60 hover:bg-primary/10 transition-all duration-300 hover:scale-105"
        >
          <FileText className="h-5 w-5 mr-2" />
          Transcript
        </Button>

        <Button
          variant="outline"
          size="lg"
          onClick={onRetryQuestion}
          className="border-primary/30 hover:border-primary/60 hover:bg-primary/10 transition-all duration-300 hover:scale-105"
          disabled={isAiThinking}
        >
          <RotateCcw className="h-5 w-5 mr-2" />
          Retry
        </Button>

        <Button
          variant="outline"
          size="lg"
          onClick={onRepeatQuestion}
          className="border-cyan-500/30 hover:border-cyan-500/60 text-cyan-400 hover:bg-cyan-500/10 transition-all duration-300 hover:scale-105"
          disabled={isAiThinking || isSpeaking}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg>
          Repeat
        </Button>

        <Button
          variant="outline"
          size="lg"
          onClick={onMarkDifficult}
          className="border-yellow-500/30 hover:border-yellow-500/60 text-yellow-400 hover:bg-yellow-500/10 transition-all duration-300 hover:scale-105"
        >
          <BookmarkMinus className="h-5 w-5 mr-2" />
          Mark Difficult
        </Button>

        <Button
          variant="destructive"
          size="lg"
          onClick={onEndInterview}
          className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border-red-500/30 hover:border-red-500/60 transition-all duration-300 hover:scale-105"
        >
          <Square className="h-5 w-5 mr-2" />
          End Interview
        </Button>
      </div>
    </div>
  );
};

export default ControlToolbar;
