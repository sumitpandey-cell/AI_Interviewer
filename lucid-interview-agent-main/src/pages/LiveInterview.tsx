import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Square, FileText, RotateCcw, BookmarkMinus, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { useNavigate, useLocation } from 'react-router-dom';
import VoiceWaveform from '@/components/interview/VoiceWaveform';
import InterviewTimer from '@/components/interview/InterviewTimer';
import { InterviewWebSocketConnection, AuthAPI } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import SilenceDetector from '@/components/interview/SilenceDetector';
import { useGoogleCloudTTS } from '@/components/interview/audio/useGoogleCloudTTS.simplified';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  fetchInterview,
  startInterview,
  submitResponse,
  retryQuestion,
  setCurrentQuestion,
  setAudioData,
  setWorkflowState,
  clearCurrentInterview
} from '@/store/slices/interviewSlice';

interface TranscriptEntry {
  speaker: 'AI' | 'User' | 'System';
  text: string;
  timestamp: Date;
}

const LiveInterview = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const dispatch = useAppDispatch();

  // Get state from Redux
  const {
    currentInterview,
    interviewSession,
    currentQuestion,
    currentResponse,
    loading,
    error
  } = useAppSelector(state => state.interview);

  // Local state that doesn't need to be in Redux
  const [isMuted, setIsMuted] = useState(false);
  const [showTranscript, setShowTranscript] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [questionProgress, setQuestionProgress] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [showEndModal, setShowEndModal] = useState(false);
  const [interviewDuration, setInterviewDuration] = useState(0);
  const [isAiThinking, setIsAiThinking] = useState(false);
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [interviewCompleted, setInterviewCompleted] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Derived from Redux state
  const sessionToken = interviewSession?.session_token || '';
  const interviewId = currentInterview?.id || null;
  const interviewPosition = currentInterview?.position || '';
  const interviewCompany = currentInterview?.company_name || '';
  const currentAudioData = interviewSession?.audio_data || null;

  const wsConnection = useRef<InterviewWebSocketConnection | null>(null);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const mediaChunks = useRef<Blob[]>([]);
  const audioContext = useRef<AudioContext | null>(null);
  const analyser = useRef<AnalyserNode | null>(null);

  // Use simplified Google Cloud TTS for audio playback
  const { play: playGoogleCloudTTS, isSpeaking: isTTSSpeaking, stop: stopGoogleCloudTTS } = useGoogleCloudTTS();

  // Track when AI has finished speaking to auto-start recording
  useEffect(() => {
    if (!isTTSSpeaking && !isRecording && !isAiThinking && !interviewCompleted && currentQuestion) {
      // AI has stopped speaking and we're not recording - auto-start recording after a brief delay
      const timer = setTimeout(() => {
        startAudioRecording();
      }, 100); // Small delay for better UX

      return () => clearTimeout(timer);
    }
  }, [isTTSSpeaking, isRecording, isAiThinking, interviewCompleted]);

  // Enhanced audio playback helper function - ONLY use Google Cloud TTS
  const playAudioFromBackend = (audioData: any, fallbackText?: string) => {
    // Check if audioData exists and has the expected structure
    if (audioData && typeof audioData === 'object') {
      if (audioData.audio) {
        // First ensure any recording is stopped when AI starts speaking
        if (isRecording) {
          stopAudioRecording();
        }

        // Set speaking state for UI feedback
        setIsSpeaking(true);

        // Use useGoogleCloudTTS hook to play audio with the audio data
        const success = playGoogleCloudTTS(audioData);

        if (!success) {
          // Log warning if Google Cloud TTS fails
          console.warn("Failed to play Google Cloud TTS audio");
          setIsSpeaking(false);
        }

        return success;
      } else {
        console.warn("audioData object exists but has no audio property:", JSON.stringify(audioData));
      }
    } else {
      console.warn("Invalid audioData received:", audioData);
    }

    if (fallbackText) {
      console.warn("No valid Google Cloud TTS audio received from backend");
      toast({
        variant: "destructive",
        title: "Audio Playback Issue",
        description: "Using text mode only for this question. Audio will be re-enabled for the next question.",
      });
    }

    return false;
  };

  // Initialize interview from URL params or navigate back to dashboard
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const id = params.get('id');

    if (!id || !AuthAPI.isAuthenticated()) {
      toast({
        variant: "destructive",
        title: "Invalid interview session",
        description: "Please select an interview from the dashboard.",
      });
      navigate('/dashboard');
      return;
    }

    const interviewIdNum = parseInt(id, 10);

    // Use Redux to fetch interview details and start it
    const initializeInterview = async () => {
      try {
        // First fetch the interview details
        await dispatch(fetchInterview(interviewIdNum)).unwrap();

        // Then start the interview
        const startResult = await dispatch(startInterview(interviewIdNum)).unwrap();

        console.log('Start interview result from Redux:', startResult);
        console.log('Audio data from backend:', startResult.audio_data); // Debug log audio data

        // Update workflow state in Redux store
        if (startResult.workflow_state) {
          dispatch(setWorkflowState(startResult.workflow_state));
          setTotalQuestions(startResult.workflow_state.total_questions || 5);
          setQuestionProgress(1);
        }

        // Play audio from backend
        playAudioFromBackend(startResult.audio_data);
        console.log("))))))))))))))))))))))))))))))))))))))))))))))))))))))",startResult.audio_data);

        // Setup WebSocket connection
        await setupWebSocket(startResult.session_token);

      } catch (error) {
        console.error('Failed to start interview:', error);
        toast({
          variant: "destructive",
          title: "Failed to start interview",
          description: error instanceof Error ? (error as Error).message : "Please try again later.",
        });
        navigate('/dashboard');
      }
    };

    initializeInterview();

    // Cleanup function
    return () => {
      stopAudioRecording();
      if (wsConnection.current) {
        wsConnection.current.close();
      }
      stopGoogleCloudTTS();

      // Clear interview state when leaving page
      dispatch(clearCurrentInterview());
    };
  }, [dispatch, location.search, navigate, toast]);

  // Setup WebSocket connection for audio streaming
  const setupWebSocket = async (token: string) => {
    if (wsConnection.current) {
      wsConnection.current.close();
    }

    try {

      wsConnection.current = new InterviewWebSocketConnection(token);

      // Set up WebSocket event handlers
      wsConnection.current.on('open', () => {
      });

      wsConnection.current.on('message', (data: any) => {

        // Handle different message types
        if (data.type === 'start_streaming') {
          startAudioRecording();
        } else if (data.type === 'stop_streaming') {
          stopAudioRecording();
        } else if (data.type === 'ai_thinking') {
          setIsAiThinking(true);
        }
      });

      wsConnection.current.on('transcript', (text: string) => {
        // Add to transcript
        setTranscript(prev => [
          ...prev,
          {
            speaker: 'User',
            text: text,
            timestamp: new Date()
          }
        ]);
      });

      wsConnection.current.on('error', (error: any) => {
        console.error("WebSocket error:", error);
      });

      wsConnection.current.on('close', () => {
      });

      await wsConnection.current.connect();
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Connection issue",
        description: "Failed to establish real-time connection. Trying to recover...",
      });
    }
  };

  // Start audio recording
  const startAudioRecording = async () => {
    if (isRecording || isMuted) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create audio context and analyzer
      if (!audioContext.current) {
        audioContext.current = new (window.AudioContext || (window as any).webkitAudioContext)();
        const source = audioContext.current.createMediaStreamSource(stream);
        analyser.current = audioContext.current.createAnalyser();
        analyser.current.fftSize = 256;
        source.connect(analyser.current);
      }

      // Create media recorder
      mediaRecorder.current = new MediaRecorder(stream);
      mediaChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          mediaChunks.current.push(event.data);
        }
      };

      mediaRecorder.current.onstop = async () => {
        // Create audio blob from chunks
        const audioBlob = new Blob(mediaChunks.current, { type: 'audio/webm' });
        mediaChunks.current = [];

        // Convert to base64
        const reader = new FileReader();
        reader.onloadend = async () => {
          const base64Audio = (reader.result as string).split(',')[1]; // Remove data URL prefix
          console.log('Base64 audio data:', base64Audio); // Debug log

          if (base64Audio && sessionToken) {
            try {
              setIsAiThinking(true);
              // Use Redux to submit response
              const result = await dispatch(submitResponse({
                session_token: sessionToken,
                audio_data: base64Audio
              })).unwrap();
              console.log('Response from submitResponse:', result);
              setIsAiThinking(false);

              if (result.is_completed) {
                handleInterviewComplete(result.feedback);
              } else {
                // Update progress
                if (result.workflow_state) {
                  dispatch(setWorkflowState(result.workflow_state));

                  // Update progress metrics
                  const progress = result.workflow_state.current_question || questionProgress + 1;
                  setQuestionProgress(progress);
                } 
                

                // Extract question text
                let questionText = '';
                if (typeof result.next_question === 'string') {
                  questionText = result.next_question;
                } else if (result.next_question && typeof result.next_question === 'object') {
                  questionText = result.next_question.question ||
                    JSON.stringify(result.next_question);
                }

                // Update Redux state
                dispatch(setCurrentQuestion(questionText));
                dispatch(setAudioData(result.audio_data));

                // Add AI response to transcript
                setTranscript(prev => [
                  ...prev,
                  {
                    speaker: 'AI',
                    text: questionText,
                    timestamp: new Date()
                  }
                ]);

                // Play Google Cloud TTS audio
                console.log('Playing audio from backend:', result.audio_data);
                playAudioFromBackend(result.audio_data.base64);
              }
            } catch (error) {
              console.error('Error submitting response:', error);
              setIsAiThinking(false);

              toast({
                variant: "destructive",
                title: "Failed to process response",
                description: "There was an error processing your answer. Please try again.",
              });
            }
          }

        };
        reader.readAsDataURL(audioBlob);
      };

      // Start recording
      mediaRecorder.current.start(1000);
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      toast({
        variant: "destructive",
        title: "Microphone access denied",
        description: "Please enable microphone access to continue the interview.",
      });
    }
  };

  // Stop audio recording
  const stopAudioRecording = () => {
    if (!isRecording || !mediaRecorder.current) return;

    try {
      if (mediaRecorder.current.state !== 'inactive') {
        mediaRecorder.current.stop();
      }

      // Stop all tracks
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());

      setIsRecording(false);
    } catch (error) {
      console.error('Error stopping recording:', error);
    }
  };

  // Handle interview complete
  const handleInterviewComplete = (feedback: any) => {
    stopAudioRecording();
    if (wsConnection.current) {
      wsConnection.current.close();
    }

    setInterviewCompleted(true);
    setTranscript(prev => [
      ...prev,
      {
        speaker: 'System',
        text: 'Interview completed. Thank you for your participation.',
        timestamp: new Date()
      }
    ]);

    toast({
      title: "Interview Completed",
      description: "Thank you for completing the interview!",
    });

    // Show end modal with feedback
    setShowEndModal(true);
  };

  // Handle going back to dashboard
  const handleGoToDashboard = () => {
    navigate('/dashboard');
  };

  const handleSilenceDetection = () => {
    if (isRecording) {
      stopAudioRecording();
      setIsAiThinking(false);
      setIsSpeaking(false);
      setTranscript(prev => [
        ...prev,
        {
          speaker: 'System',
          text: 'Silence detected. Please respond to continue.',
          timestamp: new Date()
        }
      ]);
    }
  }

  // Main interview UI
  return (
    <div className="h-screen bg-dark-bg flex flex-col">
      {/* Header bar */}
      <header className="bg-card-bg/50 backdrop-blur-md border-b border-primary/20 px-6 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              onClick={handleGoToDashboard}
              className="text-white"
            >
              <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
            </Button>
          </div>

          <div>
            {/* <h1 className="text-2xl font-lovable text-white">
              {interviewPosition} Interview {interviewCompany ? ` - ${interviewCompany}` : ''}
            </h1> */}
          </div>

          <div className="flex items-center space-x-4">
            <InterviewTimer
              onUpdate={(duration) => setInterviewDuration(duration)}
              isPaused={interviewCompleted}
            />
          </div>
        </div>
      </header>

      {/* Progress bar */}
      <div className="px-6 pt-2">
        <div className="flex items-center justify-between text-sm text-white/60">
          {/* <span>Question {questionProgress} of {totalQuestions}</span> */}
          {/* <span>Progress: {Math.round((questionProgress / totalQuestions) * 100)}%</span> */}
        </div>
        {/* <Progress
          value={(questionProgress / totalQuestions) * 100}
          className="h-1 mt-1"
        /> */}
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden p-6">
        <div className={`flex-1 flex flex-col ${showTranscript ? 'mr-4' : ''}`}>
          {/* Question display card */}
          <Card className="bg-card-bg border-primary/20 mb-6 text-white flex-1">
            <CardContent className="p-6 flex flex-col h-full justify-between">
              <div className="space-y-6 flex-1 overflow-y-auto">
                {/* Audio status indicator */}
                <div className="flex items-center space-x-2 text-muted">
                  {isSpeaking ? (
                    <div className="flex items-center text-secondary">
                      <span className="mr-2">●</span> AI is speaking
                    </div>
                  ) : isRecording ? (
                    <div className="flex items-center text-red-500">
                      <span className="mr-2">●</span> Recording
                    </div>
                  ) : (
                    <div className="flex items-center">
                      <span className="mr-2">○</span> Waiting for response
                    </div>
                  )}
                </div>

                {/* Voice waveform */}
                <div className="h-24">
                  {isRecording && !isMuted && (
                    <VoiceWaveform
                      isActive={isRecording && !isSpeaking && !interviewCompleted}
                      isMuted={isMuted}
                    />
                  )}
                </div>

                {/* Enhanced Silence detector */}
                {isRecording && !isMuted && (
                  <SilenceDetector
                    isRecording={isRecording}
                    onSilence={handleSilenceDetection}
                    silenceThreshold={2}
                    silenceDelay={2000}
                    zcrThreshold={0.1} // ZCR threshold for speech
                    speechFreqRange={[80, 4000]} // Focus on speech frequencies
                  />
                )}
              </div>
            </CardContent>
          </Card>
        </div>

      </div>

    </div>
  );
};

export default LiveInterview;
