import { useState, useEffect } from 'react';

interface AudioPlayerProps {
  audioData?: { audio: string } | null;
  fallbackText?: string;
  onSpeakingStateChange?: (isSpeaking: boolean) => void;
  autoPlay?: boolean;
}

/**
 * AudioPlayer component for handling TTS audio playback
 * Plays audio from Google Cloud TTS (backend-provided)
 * Only uses browser TTS as a last resort fallback
 */
export const AudioPlayer = ({ 
  audioData, 
  fallbackText,
  onSpeakingStateChange,
  autoPlay = false
}: AudioPlayerProps) => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  // Update parent component speaking state
  const updateSpeakingState = (speaking: boolean) => {
    setIsSpeaking(speaking);
    if (onSpeakingStateChange) {
      onSpeakingStateChange(speaking);
    }
  };

  // Effect to auto-play audio when audioData changes
  useEffect(() => {
    if (autoPlay && audioData?.audio) {
      playBackendAudio();
    }
  }, [audioData, autoPlay]);
  
  /**
   * Play audio using backend Google Cloud TTS audio data
   */
  const playBackendAudio = () => {
    if (!audioData) {
      console.error('audioData object is null or undefined');
      return handleMissingAudio();
    }
    
    if (!audioData.audio) {
      console.error('audioData exists but audio property is missing');
      console.log('Available audioData:', JSON.stringify(audioData));
      return handleMissingAudio();
    }
    
    try {
      console.log("Playing audio from Google Cloud TTS", audioData);
      
      // Create audio element
      const audio = new Audio();
      
      // Set up event handlers before setting the src
      audio.oncanplay = () => {
        console.log("Google Cloud TTS audio can play, starting playback");
        updateSpeakingState(true);
        audio.play().catch(err => {
          console.error('Failed to play Google Cloud TTS audio after canplay event:', err);
          updateSpeakingState(false);
          return handleMissingAudio();
        });
      };
      
      audio.onended = () => {
        console.log("Google Cloud TTS audio playback ended");
        updateSpeakingState(false);
      };
      
      audio.onerror = (e) => {
        console.error('Error playing Google Cloud TTS audio:', e);
        updateSpeakingState(false);
        return handleMissingAudio();
      };
      
      // Set the audio source - using LINEAR16 format from Google TTS
      audio.src = `data:audio/wav;base64,${audioData.audio}`;
      
      // Attempt to load the audio
      audio.load();
      
      return true;
    } catch (error) {
      console.error('Error setting up Google Cloud TTS audio playback:', error);
      return handleMissingAudio();
    }
  };
  
  /**
   * Handle missing or failed Google Cloud TTS audio
   * Only uses browser TTS as an absolute last resort
   */
  const handleMissingAudio = () => {
    if (fallbackText) {
      console.warn('LAST RESORT FALLBACK: Using browser TTS because Google Cloud TTS audio failed');
      return speakTextWithBrowserTTS(fallbackText);
    }
    return false;
  };

  /**
   * Play audio using browser's built-in TTS
   * ONLY used as a last resort fallback
   */
  const speakTextWithBrowserTTS = (text: string) => {
    try {
      console.warn('LAST RESORT FALLBACK: Using browser TTS:', text);
      
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
            console.log('Using browser voice:', englishVoice.name);
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
          console.log('Using browser voice:', englishVoice.name);
          utterance.voice = englishVoice;
        }
      }
      
      // Events
      utterance.onstart = () => {
        console.log('Browser TTS started speaking');
        updateSpeakingState(true);
      };
      
      utterance.onend = () => {
        console.log('Browser TTS finished speaking');
        updateSpeakingState(false);
      };
      
      utterance.onerror = (event) => {
        console.error('Browser TTS error:', event);
        updateSpeakingState(false);
      };
      
      // Start speaking
      window.speechSynthesis.speak(utterance);
      return true;
    } catch (error) {
      console.error('Browser TTS failed:', error);
      updateSpeakingState(false);
      return false;
    }
  };
  
  /**
   * Public method to play audio (exposed for component users)
   * Only uses Google Cloud TTS, with browser TTS as absolute last resort
   */
  const playAudio = () => {
    if (audioData?.audio) {
      return playBackendAudio();
    } else {
      console.error('No Google Cloud TTS audio available');
      return handleMissingAudio();
    }
  };
  
  // Expose playAudio method for use by parent components
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).__audioPlayerInstance = { playAudio };
    }
    return () => {
      if (typeof window !== 'undefined') {
        (window as any).__audioPlayerInstance = null;
      }
    };
  }, [audioData, fallbackText]);

  return null; // This is a non-visual component
};

export default AudioPlayer;
