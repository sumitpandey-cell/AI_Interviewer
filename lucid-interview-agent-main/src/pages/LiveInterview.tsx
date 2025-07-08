
import { useState, useEffect } from 'react';
import { Mic, MicOff, Square, FileText, RotateCcw, BookmarkMinus, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { useNavigate } from 'react-router-dom';
import VoiceWaveform from '@/components/interview/VoiceWaveform';
import TranscriptPanel from '@/components/interview/TranscriptPanel';
import InterviewTimer from '@/components/interview/InterviewTimer';
import SilenceDetector from '@/components/interview/SilenceDetector';
import EndInterviewModal from '@/components/interview/EndInterviewModal';

interface TranscriptEntry {
  speaker: 'AI' | 'User' | 'System';
  text: string;
  timestamp: Date;
}

const LiveInterview = () => {
  const navigate = useNavigate();
  const [isMuted, setIsMuted] = useState(false);
  const [showTranscript, setShowTranscript] = useState(false);
  const [isRecording, setIsRecording] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState("Tell me about yourself and why you're interested in this position.");
  const [questionProgress, setQuestionProgress] = useState(1);
  const [totalQuestions] = useState(8);
  const [showEndModal, setShowEndModal] = useState(false);
  const [interviewDuration, setInterviewDuration] = useState(0);
  const [isAiThinking, setIsAiThinking] = useState(false);
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([
    { speaker: 'AI', text: "Welcome! I'm your AI interviewer today. Let's begin with our first question.", timestamp: new Date() },
  ]);

  // Mock questions for demo
  const questions = [
    "Tell me about yourself and why you're interested in this position.",
    "What are your greatest strengths and how do they apply to this role?",
    "Describe a challenging project you've worked on recently.",
    "How do you handle working under pressure and tight deadlines?",
    "Where do you see yourself in 5 years?",
    "What questions do you have about our company or this role?",
    "Describe a time when you had to learn a new technology quickly.",
    "Thank you for your time. Do you have any final thoughts to share?"
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setInterviewDuration(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleMuteToggle = () => {
    setIsMuted(!isMuted);
  };

  const handleEndInterview = () => {
    setShowEndModal(true);
    setIsRecording(false);
  };

  const handleRetryQuestion = () => {
    setIsAiThinking(true);
    setTimeout(() => {
      setIsAiThinking(false);
      // Add to transcript
      setTranscript(prev => [...prev, {
        speaker: 'AI',
        text: `Let me rephrase that: ${currentQuestion}`,
        timestamp: new Date()
      }]);
    }, 2000);
  };

  const handleNextQuestion = () => {
    if (questionProgress < totalQuestions) {
      setIsAiThinking(true);
      setTimeout(() => {
        const nextIndex = questionProgress;
        setCurrentQuestion(questions[nextIndex]);
        setQuestionProgress(prev => prev + 1);
        setIsAiThinking(false);
        
        setTranscript(prev => [...prev, {
          speaker: 'AI',
          text: questions[nextIndex],
          timestamp: new Date()
        }]);
      }, 3000);
    } else {
      handleEndInterview();
    }
  };

  const handleMarkDifficult = () => {
    // Add visual feedback for marking question as difficult
    setTranscript(prev => [...prev, {
      speaker: 'System',
      text: '📝 Question marked as difficult for review',
      timestamp: new Date()
    }]);
  };

  const progressPercentage = (questionProgress / totalQuestions) * 100;

  return (
    <div className="min-h-screen bg-[#1A1C23] text-white flex flex-col">
      {/* Enhanced Header */}
      <header className="bg-[#262933]/80 backdrop-blur-xl border-b border-primary/10 px-6 py-4 shadow-2xl">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/dashboard')}
              className="text-muted hover:text-white hover:bg-primary/10 transition-all duration-300"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="space-y-1">
              <h1 className="text-xl font-bold text-white flex items-center space-x-3">
                <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                <span>AI Interview Session</span>
              </h1>
              <p className="text-sm text-cyan-400 font-medium">Frontend Developer - TCS</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            <InterviewTimer duration={interviewDuration} />
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

      {/* Enhanced Progress Bar */}
      <div className="px-6 py-4 bg-[#262933]/40 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-white">Question {questionProgress} of {totalQuestions}</span>
              <div className="flex space-x-1">
                {Array.from({ length: totalQuestions }).map((_, index) => (
                  <div
                    key={index}
                    className={`w-2 h-2 rounded-full transition-all duration-300 ${
                      index < questionProgress ? 'bg-primary' : 'bg-primary/20'
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

      {/* Main Content */}
      <main className="flex-1 flex">
        <div className="flex-1 flex flex-col">
          {/* Enhanced Interview Interface */}
          <div className="flex-1 flex flex-col items-center justify-center p-8 space-y-8">
            {/* Current Question Panel - Glassmorphism */}
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
                    <p className="text-lg text-gray-200 leading-relaxed font-medium">
                      {currentQuestion}
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Enhanced Voice Waveform */}
            <VoiceWaveform isMuted={isMuted} isActive={!isAiThinking} />

            {/* Subtitle */}
            <p className="text-muted text-center max-w-md">
              {isMuted ? 'Click unmute to continue your interview' : 'Speak when ready — your voice is being recorded'}
            </p>

            {/* Silence Detector */}
            <SilenceDetector onTimeout={handleNextQuestion} isActive={!isMuted && !isAiThinking} />
          </div>

          {/* Enhanced Control Toolbar */}
          <div className="bg-[#262933]/60 backdrop-blur-xl border-t border-primary/10 p-6 shadow-2xl">
            <div className="flex items-center justify-center space-x-4">
              <Button
                variant={isMuted ? "default" : "outline"}
                size="lg"
                onClick={handleMuteToggle}
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
                onClick={() => setShowTranscript(!showTranscript)}
                className="border-primary/30 hover:border-primary/60 hover:bg-primary/10 transition-all duration-300 hover:scale-105"
              >
                <FileText className="h-5 w-5 mr-2" />
                Transcript
              </Button>

              <Button
                variant="outline"
                size="lg"
                onClick={handleRetryQuestion}
                className="border-primary/30 hover:border-primary/60 hover:bg-primary/10 transition-all duration-300 hover:scale-105"
                disabled={isAiThinking}
              >
                <RotateCcw className="h-5 w-5 mr-2" />
                Retry
              </Button>

              <Button
                variant="outline"
                size="lg"
                onClick={handleMarkDifficult}
                className="border-yellow-500/30 hover:border-yellow-500/60 text-yellow-400 hover:bg-yellow-500/10 transition-all duration-300 hover:scale-105"
              >
                <BookmarkMinus className="h-5 w-5 mr-2" />
                Mark Difficult
              </Button>

              <Button
                variant="destructive"
                size="lg"
                onClick={handleEndInterview}
                className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border-red-500/30 hover:border-red-500/60 transition-all duration-300 hover:scale-105"
              >
                <Square className="h-5 w-5 mr-2" />
                End Interview
              </Button>
            </div>
          </div>
        </div>

        {/* Enhanced Transcript Panel */}
        {showTranscript && (
          <div className="animate-slide-in-right">
            <TranscriptPanel 
              transcript={transcript} 
              onClose={() => setShowTranscript(false)}
            />
          </div>
        )}
      </main>

      {/* End Interview Modal */}
      <EndInterviewModal 
        isOpen={showEndModal}
        onClose={() => setShowEndModal(false)}
        duration={interviewDuration}
        questionsAnswered={questionProgress}
        totalQuestions={totalQuestions}
        onGoToDashboard={() => navigate('/dashboard')}
      />
    </div>
  );
};

export default LiveInterview;
