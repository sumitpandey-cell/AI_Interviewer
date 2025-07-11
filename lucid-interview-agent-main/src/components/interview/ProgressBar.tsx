import { Progress } from '@/components/ui/progress';

interface ProgressBarProps {
  currentQuestion: number;
  totalQuestions: number;
}

/**
 * Progress bar component for the interview
 */
const ProgressBar = ({ currentQuestion, totalQuestions }: ProgressBarProps) => {
  const progressPercentage = (currentQuestion / totalQuestions) * 100;
  
  return (
    <div className="px-6 py-4 bg-[#262933]/40 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            <span className="text-sm font-medium text-white">Question {currentQuestion} of {totalQuestions}</span>
            <div className="flex space-x-1">
              {Array.from({ length: totalQuestions }).map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full transition-all duration-300 ${
                    index < currentQuestion ? 'bg-primary' : 'bg-primary/20'
                  }`}
                />
              ))}
            </div>
          </div>
          <span className="text-sm font-medium text-cyan-400">{Math.round(progressPercentage)}% Complete</span>
        </div>
        <Progress 
          value={progressPercentage} 
          className="h-2 bg-primary/10 border border-primary/20 rounded-full overflow-hidden"
        />
      </div>
    </div>
  );
};

export default ProgressBar;
