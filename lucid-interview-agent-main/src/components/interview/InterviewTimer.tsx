
import { Clock } from 'lucide-react';

interface InterviewTimerProps {
  duration: number; // duration in seconds
}

const InterviewTimer = ({ duration }: InterviewTimerProps) => {
  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex items-center space-x-2 text-white">
      <Clock className="h-4 w-4 text-primary" />
      <span className="text-sm font-mono">
        {formatTime(duration)}
      </span>
    </div>
  );
};

export default InterviewTimer;
