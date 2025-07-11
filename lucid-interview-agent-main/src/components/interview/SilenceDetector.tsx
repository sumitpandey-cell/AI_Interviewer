import React, { useEffect, useRef } from "react";

declare global {
  interface Window {
    webkitAudioContext: typeof AudioContext;
  }
}

interface SilenceDetectorProps {
  onSilence: () => void;
  isRecording: boolean;
  silenceThreshold?: number; // Base threshold for silence detection
  silenceDelay?: number; // Time (ms) to confirm silence
  speechFreqRange?: [number, number]; // Frequency range for speech (Hz)
  zcrThreshold?: number; // Zero-crossing rate threshold for speech
}

const SilenceDetector = ({
  onSilence,
  isRecording,
  silenceThreshold = 0.1,
  silenceDelay = 3000, // Increased to 3 seconds for stability
  speechFreqRange = [100, 3000], // Narrower speech range
  zcrThreshold = 0.1, // ZCR threshold for speech detection
}: SilenceDetectorProps) => {
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const noiseFloorRef = useRef<number>(0);
  const isSpeechActiveRef = useRef<boolean>(false); // Track speech state for hysteresis

  useEffect(() => {
    if (isRecording) {
      startListening();
    } else {
      stopListening();
    }

    return () => {
      stopListening();
    };
  }, [isRecording]);

  const startListening = async () => {
    try {
      stopListening(); // Clean up previous resources

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;

      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 1024; // Reduced for performance
      analyser.smoothingTimeConstant = 0.85; // Increased smoothing
      analyserRef.current = analyser;

      source.connect(analyser);

      // Estimate initial noise floor
      await estimateNoiseFloor(analyser);
      detectSilence(analyser);
    } catch (error) {
      console.error("Error starting silence detection:", error);
    }
  };

  const estimateNoiseFloor = async (analyser: AnalyserNode): Promise<void> => {
    const freqData = new Float32Array(analyser.frequencyBinCount);
    const timeData = new Uint8Array(analyser.fftSize);
    let energySum = 0;
    const samples = 150; // More samples for better noise floor estimation
    const sampleInterval = 20; // ms between samples

    for (let i = 0; i < samples; i++) {
      analyser.getFloatFrequencyData(freqData);
      analyser.getByteTimeDomainData(timeData);
      const energy = calculateSpeechEnergy(freqData, audioContextRef.current!.sampleRate);
      energySum += energy;
      await new Promise((resolve) => setTimeout(resolve, sampleInterval));
    }

    noiseFloorRef.current = energySum / samples;
    console.log("Estimated noise floor:", noiseFloorRef.current);
  };

  const calculateSpeechEnergy = (data: Float32Array, sampleRate: number): number => {
    const binSize = sampleRate / analyserRef.current!.fftSize;
    const [minFreq, maxFreq] = speechFreqRange;
    const startBin = Math.floor(minFreq / binSize);
    const endBin = Math.min(Math.floor(maxFreq / binSize), data.length);

    let energy = 0;
    for (let i = startBin; i < endBin; i++) {
      const amplitude = Math.pow(10, data[i] / 10); // Convert dB to linear
      energy += amplitude;
    }
    return energy / (endBin - startBin);
  };

  const calculateZeroCrossingRate = (data: Uint8Array): number => {
    let crossings = 0;
    for (let i = 1; i < data.length; i++) {
      const prev = (data[i - 1] - 128) / 128;
      const curr = (data[i] - 128) / 128;
      if ((prev >= 0 && curr < 0) || (prev < 0 && curr >= 0)) {
        crossings++;
      }
    }
    return crossings / data.length;
  };

  const detectSilence = (analyser: AnalyserNode) => {
    const freqData = new Float32Array(analyser.frequencyBinCount);
    const timeData = new Uint8Array(analyser.fftSize);

    const checkSilence = () => {
      if (!isRecording) {
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
        return;
      }

      analyser.getFloatFrequencyData(freqData);
      analyser.getByteTimeDomainData(timeData);

      const speechEnergy = calculateSpeechEnergy(freqData, audioContextRef.current!.sampleRate);
      const zcr = calculateZeroCrossingRate(timeData);
      const enterSpeechThreshold = noiseFloorRef.current * (1 + silenceThreshold * 1.5); // Higher threshold to enter speech
      const exitSpeechThreshold = noiseFloorRef.current * (1 + silenceThreshold); // Lower threshold to exit speech

      // Speech detection with hysteresis
      if (isSpeechActiveRef.current) {
        // In speech state, use lower threshold to stay in speech
        if (speechEnergy < exitSpeechThreshold || zcr > zcrThreshold) {
          if (!silenceTimerRef.current) {
            console.log("Silence detected, starting timer...");
            silenceTimerRef.current = setTimeout(() => {
              console.log("Silence threshold reached, stopping recording");
              isSpeechActiveRef.current = false;
              onSilence();
            }, silenceDelay);
          }
        } else {
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
          }
        }
      } else {
        // In silence state, use higher threshold to enter speech
        if (speechEnergy > enterSpeechThreshold && zcr < zcrThreshold) {
          isSpeechActiveRef.current = true;
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
          }
        }
      }

      animationFrameRef.current = requestAnimationFrame(checkSilence);
    };

    animationFrameRef.current = requestAnimationFrame(checkSilence);
  };

  const stopListening = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (sourceRef.current) {
      sourceRef.current = null;
    }

    if (analyserRef.current) {
      analyserRef.current = null;
    }

    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  };

  return null;
};

export default SilenceDetector;