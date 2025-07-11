import { useState, useRef, useCallback, useEffect } from 'react';

interface UseAudioRecorderProps {
  onRecordingStateChange?: (isRecording: boolean) => void;
  onError?: (error: Error) => void;
}

/**
 * Custom hook for handling audio recording
 */
export function useAudioRecorder({ 
  onRecordingStateChange,
  onError 
}: UseAudioRecorderProps = {}) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const mediaChunks = useRef<Blob[]>([]);
  const audioContext = useRef<AudioContext | null>(null);
  const analyser = useRef<AnalyserNode | null>(null);
  const audioStream = useRef<MediaStream | null>(null);
  
  // Update recording state and notify parent if needed
  const updateRecordingState = useCallback((recording: boolean) => {
    setIsRecording(recording);
    if (onRecordingStateChange) {
      onRecordingStateChange(recording);
    }
  }, [onRecordingStateChange]);
  
  // Handle recording errors
  const handleError = useCallback((error: Error) => {
    console.error('Audio recording error:', error);
    if (onError) {
      onError(error);
    }
  }, [onError]);
  
  // Start audio recording
  const startRecording = useCallback(async (onDataAvailable?: (data: Blob) => void) => {
    try {
      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStream.current = stream;
      
      // Setup audio context for visualization
      audioContext.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      analyser.current = audioContext.current.createAnalyser();
      const source = audioContext.current.createMediaStreamSource(stream);
      source.connect(analyser.current);
      
      // Setup media recorder
      mediaRecorder.current = new MediaRecorder(stream);
      mediaChunks.current = [];
      
      // Handle data available event
      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          mediaChunks.current.push(event.data);
          
          // Call callback if provided
          if (onDataAvailable) {
            onDataAvailable(event.data);
          }
        }
      };
      
      // Start recording
      mediaRecorder.current.start(1000); // Collect data every second
      updateRecordingState(true);
      
      return true;
    } catch (error) {
      handleError(error instanceof Error ? error : new Error('Failed to start recording'));
      return false;
    }
  }, [updateRecordingState, handleError]);
  
  // Stop audio recording
  const stopRecording = useCallback(() => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop();
      updateRecordingState(false);
      
      // Close audio tracks
      if (audioStream.current) {
        audioStream.current.getTracks().forEach(track => track.stop());
      }
    }
    
    // Close audio context
    if (audioContext.current) {
      audioContext.current.close();
    }
    
    return mediaChunks.current;
  }, [updateRecordingState]);
  
  // Get audio data for visualization
  const getAudioVisualizationData = useCallback(() => {
    if (analyser.current) {
      const bufferLength = analyser.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      analyser.current.getByteFrequencyData(dataArray);
      return dataArray;
    }
    return null;
  }, []);
  
  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
        mediaRecorder.current.stop();
      }
      
      if (audioStream.current) {
        audioStream.current.getTracks().forEach(track => track.stop());
      }
      
      if (audioContext.current) {
        audioContext.current.close();
      }
    };
  }, []);
  
  return {
    isRecording,
    startRecording,
    stopRecording,
    getAudioVisualizationData
  };
}

export default useAudioRecorder;
