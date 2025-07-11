import { useState, useRef, useCallback, useEffect } from 'react';

interface AudioData {
  audio?: string;
}

/**
 * Simplified hook for playing Google Cloud TTS audio
 */
export const useGoogleCloudTTS = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  // Stop any playing audio
  const stop = useCallback(() => {
    if (audioRef.current) {
      try {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      } catch (e) {
        console.error("Error stopping audio:", e);
      }
    }
    setIsSpeaking(false);
  }, []);
  
  // Play audio from base64 string
  const play = useCallback((audioData?: AudioData | null, fallbackText?: string) => {
    // Stop any currently playing audio
    stop();
    
    // Check if we have valid audio data
    if (!audioData || !audioData.audio) {
      console.error("No valid audio data to play");
      return false;
    }
    
    try {
      // Create new audio element
      const audio = new Audio();
      audioRef.current = audio;
      
      // Set up event handlers
      audio.oncanplay = () => {
        console.log("Audio loaded, ready to play");
        audio.play()
          .then(() => {
            console.log("Audio playback started");
            setIsSpeaking(true);
          })
          .catch((err) => {
            console.error("Failed to play audio:", err);
            setIsSpeaking(false);
          });
      };
      
      audio.onended = () => {
        console.log("Audio playback ended");
        setIsSpeaking(false);
      };
      
      audio.onerror = (e) => {
        console.error("Error with audio playback:", e);
        setIsSpeaking(false);
      };
      
      // Set audio source from base64 string
      audio.src = `data:audio/wav;base64,${audioData.audio}`;
      audio.load();
      
      return true;
    } catch (error) {
      console.error("Error setting up audio:", error);
      return false;
    }
  }, [stop]);
  
  // Clean up on unmount
  useEffect(() => {
    return () => {
      stop();
    };
  }, [stop]);
  
  return {
    play,
    stop,
    isSpeaking
  };
};

export default useGoogleCloudTTS;
