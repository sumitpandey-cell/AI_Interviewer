import { Card, CardContent } from '@/components/ui/card';

interface QuestionDisplayProps {
  question: string;
  isAiThinking: boolean;
  isSpeaking: boolean;
}

/**
 * Component to display the current interview question
 */
const QuestionDisplay = ({ 
  question, 
  isAiThinking,
  isSpeaking 
}: QuestionDisplayProps) => {
  return (
    <Card className="w-full max-w-4xl bg-[#262933]/60 backdrop-blur-xl border border-primary/20 shadow-2xl">
      <CardContent className="p-8 text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <div className="w-1 h-1 bg-primary rounded-full animate-pulse"></div>
          <h2 className="text-xl font-bold text-white">Current Question</h2>
          <div className="w-1 h-1 bg-primary rounded-full animate-pulse"></div>
        </div>
        
        <div className="relative">
          {isAiThinking ? (
            <div className="flex items-center justify-center space-x-3 py-4">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
              <span className="text-primary font-medium">AI is preparing your next question...</span>
            </div>
          ) : (
            <div className="relative">
              <p className="text-lg text-gray-200 leading-relaxed font-medium">
                {question}
              </p>
              {isSpeaking && (
                <div className="absolute right-0 top-0 flex items-center space-x-2 text-primary text-sm">
                  <span className="animate-pulse">Speaking</span>
                  <div className="flex space-x-1">
                    <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse"></div>
                    <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default QuestionDisplay;
