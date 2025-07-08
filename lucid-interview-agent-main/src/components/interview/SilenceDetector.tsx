
import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageCircle, SkipForward } from 'lucide-react';

interface SilenceDetectorProps {
  onTimeout: () => void;
  isActive: boolean;
  timeoutDuration?: number; // in seconds
}

const SilenceDetector = ({ onTimeout, isActive, timeoutDuration = 15 }: SilenceDetectorProps) => {
  const [silenceTimer, setSilenceTimer] = useState(0);
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    if (isActive) {
      const interval = setInterval(() => {
        setSilenceTimer(prev => {
          const newTime = prev + 1;
          
          if (newTime >= timeoutDuration && !showPrompt) {
            setShowPrompt(true);
          }
          
          return newTime;
        });
      }, 1000);

      return () => clearInterval(interval);
    } else {
      setSilenceTimer(0);
      setShowPrompt(false);
    }
  }, [isActive, timeoutDuration, showPrompt]);

  const handleContinue = () => {
    setSilenceTimer(0);
    setShowPrompt(false);
  };

  const handleNextQuestion = () => {
    onTimeout();
    setSilenceTimer(0);
    setShowPrompt(false);
  };

  if (!showPrompt) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <Card className="w-full max-w-md bg-card-bg border-primary/20 animate-fade-in-up">
        <CardContent className="p-6 text-center">
          <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <MessageCircle className="h-8 w-8 text-primary animate-pulse" />
          </div>
          
          <h3 className="text-xl font-lovable text-white mb-2">
            We noticed a pause...
          </h3>
          
          <p className="text-muted mb-6 leading-relaxed">
            Take your time to think. Would you like to continue with this question or move to the next one?
          </p>
          
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={handleContinue}
              className="flex-1 border-primary/20 hover:border-primary/40"
            >
              Continue Thinking
            </Button>
            <Button
              onClick={handleNextQuestion}
              className="flex-1 bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90"
            >
              <SkipForward className="h-4 w-4 mr-2" />
              Next Question
            </Button>
          </div>
          
          <p className="text-xs text-muted mt-4">
            Silence detected for {timeoutDuration} seconds
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default SilenceDetector;
