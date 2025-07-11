import { useState, useEffect, useCallback } from 'react';

interface UseTTSAudioProps {
  onSpeakingStateChange?: (isSpeaking: boolean) => void;
}

/**
 * Custom hook for handling Text-to-Speech audio playback
 * Supports both backend TTS audio and browser TTS fallback
 */
export function useTTSAudio({ onSpeakingStateChange }: UseTTSAudioProps = {}) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  // Update internal and external speaking state
  const updateSpeakingState = useCallback((speaking: boolean) => {
    setIsSpeaking(speaking);
    if (onSpeakingStateChange) {
      onSpeakingStateChange(speaking);
    }
  }, [onSpeakingStateChange]);
  
  // Cancel any ongoing speech when component unmounts
  useEffect(() => {
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);
  
  /**
   * Play audio from backend TTS
   */
  const playBackendAudio = useCallback((audioData: { audio: string }) => {
    if (!audioData?.audio) return false;
    
    try {
      console.log("Playing audio from backend TTS");
      
      // Create audio element
      const audio = new Audio();
      
      // Set up event handlers before setting the src
      audio.oncanplay = () => {
        console.log("Audio can play, starting playback");
        updateSpeakingState(true);
        audio.play().catch(err => {
          console.error('Failed to play audio after canplay event:', err);
          updateSpeakingState(false);
          return false;
        });
      };
      
      audio.onended = () => {
        console.log("Audio playback ended");
        updateSpeakingState(false);
      };
      
      audio.onerror = (e) => {
        console.error('Error playing backend audio:', e);
        updateSpeakingState(false);
        return false;
      };
      
      // Set the audio source - using LINEAR16 format from Google TTS
      audio.src = `data:audio/wav;base64,${audioData.audio}`;
      
      // Attempt to load the audio
      audio.load();
      
      return true;
    } catch (error) {
      console.error('Error setting up audio playback:', error);
      updateSpeakingState(false);
      return false;
    }
  }, [updateSpeakingState]);
  
  /**
   * Play audio using browser's built-in TTS
   */
  const speakText = useCallback((text: string) => {
    if (!text) return false;
    
    try {
      console.log('Using browser TTS:', text);
      
      // Cancel any existing speech
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
      
      // Create a new utterance
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Configure voice settings
      utterance.rate = 1.0; // Speed
      utterance.pitch = 1.0; // Pitch
      utterance.volume = 1.0; // Volume
      
      // Try to find a good voice
      let voices = window.speechSynthesis.getVoices();
      
      if (voices.length === 0) {
        // Voice list might not be loaded yet
        window.speechSynthesis.onvoiceschanged = () => {
          voices = window.speechSynthesis.getVoices();
          const englishVoice = voices.find(voice => 
            voice.lang.includes('en') && (voice.name.includes('Google') || voice.name.includes('Premium'))
          );
          
          if (englishVoice) {
            console.log('Using voice:', englishVoice.name);
            utterance.voice = englishVoice;
            window.speechSynthesis.speak(utterance);
          }
        };
      } else {
        // Voice list is already loaded
        const englishVoice = voices.find(voice => 
          voice.lang.includes('en') && (voice.name.includes('Google') || voice.name.includes('Premium'))
        );
        
        if (englishVoice) {
          console.log('Using voice:', englishVoice.name);
          utterance.voice = englishVoice;
        }
      }
      
      // Events
      utterance.onstart = () => {
        console.log('Started speaking');
        updateSpeakingState(true);
      };
      
      utterance.onend = () => {
        console.log('Finished speaking');
        updateSpeakingState(false);
      };
      
      utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
        updateSpeakingState(false);
      };
      
      // Start speaking
      window.speechSynthesis.speak(utterance);
      return true;
    } catch (error) {
      console.error('Speech synthesis failed:', error);
      updateSpeakingState(false);
      return false;
    }
  }, [updateSpeakingState]);
  
  /**
   * Play audio from backend or fallback to browser TTS
   */
  const playAudio = useCallback((audioData?: { audio: string } | null, fallbackText?: string) => {
    // If we have backend audio data, try to use it
    if (audioData && audioData.audio) {
      const success = playBackendAudio(audioData);
      // If backend audio fails and we have fallback text, use browser TTS
      if (!success && fallbackText) {
        return speakText(fallbackText);
      }
      return success;
    } 
    // No backend audio but we have fallback text, use browser TTS
    else if (fallbackText) {
      return speakText(fallbackText);
    }
    return false;
  }, [playBackendAudio, speakText]);
  
  return {
    isSpeaking,
    playAudio,
    speakText,
    playBackendAudio
  };
}

export default useTTSAudio;
