
import { useEffect, useState } from 'react';
import { Mic, MicOff } from 'lucide-react';

interface VoiceWaveformProps {
  isMuted: boolean;
  isActive: boolean;
}

const VoiceWaveform = ({ isMuted, isActive }: VoiceWaveformProps) => {
  const [waveformData, setWaveformData] = useState<number[]>(Array(24).fill(0));
  const [isListening, setIsListening] = useState(false);
  const [micLevel, setMicLevel] = useState(0);

  useEffect(() => {
    if (!isMuted && isActive) {
      const interval = setInterval(() => {
        // Simulate voice waveform data with more realistic patterns
        const newData = Array(24).fill(0).map((_, index) => {
          const baseHeight = Math.sin(Date.now() * 0.001 + index * 0.3) * 30 + 40;
          const randomVariation = Math.random() * 60;
          return Math.max(4, baseHeight + randomVariation);
        });
        setWaveformData(newData);
        setIsListening(Math.random() > 0.4); // Simulate voice detection
        setMicLevel(Math.random() * 100);
      }, 120);

      return () => clearInterval(interval);
    } else {
      setWaveformData(Array(24).fill(4));
      setIsListening(false);
      setMicLevel(0);
    }
  }, [isMuted, isActive]);

  return (
    <div className="flex flex-col items-center space-y-8">
      {/* Enhanced AI Avatar Circle */}
      <div className="relative">
        <div className={`relative w-40 h-40 rounded-full flex items-center justify-center transition-all duration-500 ${
          isListening && !isMuted 
            ? 'bg-gradient-to-br from-primary/30 via-cyan-500/20 to-primary/30 shadow-2xl shadow-primary/25' 
            : 'bg-gradient-to-br from-[#262933] to-[#1A1C23] shadow-xl'
        } border-2 ${
          isListening && !isMuted ? 'border-primary/60' : 'border-primary/20'
        }`}>
          
          {/* Inner circle */}
          <div className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-500 ${
            isListening && !isMuted 
              ? 'bg-gradient-to-br from-primary/40 to-cyan-500/30 shadow-lg shadow-primary/20' 
              : 'bg-gradient-to-br from-primary/20 to-primary/10'
          }`}>
            {isMuted ? (
              <MicOff className="h-10 w-10 text-red-400" />
            ) : (
              <Mic className={`h-10 w-10 transition-all duration-300 ${
                isListening ? 'text-primary scale-110' : 'text-muted'
              }`} />
            )}
          </div>
          
          {/* Animated pulse rings when active */}
          {isListening && !isMuted && (
            <>
              <div className="absolute inset-0 rounded-full border-2 border-primary/40 animate-ping"></div>
              <div className="absolute inset-0 rounded-full border-2 border-cyan-500/30 animate-ping" style={{animationDelay: '0.5s'}}></div>
              <div className="absolute inset-0 rounded-full border border-primary/20 animate-ping" style={{animationDelay: '1s'}}></div>
            </>
          )}

          {/* Dynamic glow effect */}
          {isListening && !isMuted && (
            <div 
              className="absolute inset-0 rounded-full bg-gradient-to-br from-primary/20 to-cyan-500/20 animate-pulse"
              style={{
                filter: 'blur(20px)',
                transform: `scale(${1 + micLevel * 0.002})`
              }}
            ></div>
          )}
        </div>
      </div>

      {/* Enhanced Waveform Visualization */}
      <div className="flex items-end justify-center space-x-1 h-20 px-4">
        {waveformData.map((height, index) => (
          <div
            key={index}
            className={`w-1.5 transition-all duration-150 rounded-full ${
              isMuted 
                ? 'bg-gradient-to-t from-muted/30 to-muted/50' 
                : isListening
                ? 'bg-gradient-to-t from-primary via-cyan-500 to-primary shadow-sm shadow-primary/50'
                : 'bg-gradient-to-t from-primary/60 to-primary/80'
            }`}
            style={{ 
              height: `${height}px`,
              opacity: isListening && !isMuted ? 0.8 + (index % 3) * 0.1 : 0.6,
              animationDelay: `${index * 50}ms`
            }}
          />
        ))}
      </div>

      {/* Enhanced Status Text */}
      <div className="text-center space-y-2">
        <p className={`text-xl font-semibold transition-all duration-300 ${
          isMuted 
            ? 'text-red-400' 
            : isListening 
            ? 'text-primary' 
            : 'text-muted'
        }`}>
          {isMuted ? 'Microphone Muted' : isListening ? 'Listening...' : 'Speak when ready'}
        </p>
        <p className="text-sm text-muted">
          {isMuted ? 'Click unmute to continue' : 'Your voice is being recorded and analyzed'}
        </p>
        
        {/* Voice level indicator */}
        {!isMuted && isListening && (
          <div className="flex items-center justify-center space-x-2 mt-3">
            <div className="flex space-x-1">
              {Array.from({ length: 5 }).map((_, i) => (
                <div
                  key={i}
                  className={`w-1 h-2 rounded-full transition-all duration-150 ${
                    micLevel > i * 20 ? 'bg-primary' : 'bg-primary/20'
                  }`}
                />
              ))}
            </div>
            <span className="text-xs text-primary font-medium">Voice Level</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceWaveform;
