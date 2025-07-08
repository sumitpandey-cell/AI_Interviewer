
import { useState } from 'react';
import { X, Download, Copy, User, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';

interface TranscriptEntry {
  speaker: 'AI' | 'User' | 'System';
  text: string;
  timestamp: Date;
}

interface TranscriptPanelProps {
  transcript: TranscriptEntry[];
  onClose: () => void;
}

const TranscriptPanel = ({ transcript, onClose }: TranscriptPanelProps) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleCopyTranscript = async () => {
    const transcriptText = transcript
      .map(entry => `[${entry.timestamp.toLocaleTimeString()}] ${entry.speaker}: ${entry.text}`)
      .join('\n\n');
    
    try {
      await navigator.clipboard.writeText(transcriptText);
      setCopiedIndex(-1); // Use -1 to indicate full transcript copied
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy transcript:', err);
    }
  };

  const handleCopyEntry = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy entry:', err);
    }
  };

  const handleDownloadTranscript = () => {
    const transcriptText = transcript
      .map(entry => `[${entry.timestamp.toLocaleTimeString()}] ${entry.speaker}: ${entry.text}`)
      .join('\n\n');
    
    const blob = new Blob([transcriptText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview-transcript-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getSpeakerIcon = (speaker: string) => {
    switch (speaker) {
      case 'AI':
        return <Bot className="h-4 w-4 text-primary" />;
      case 'User':
        return <User className="h-4 w-4 text-cyan-400" />;
      default:
        return null;
    }
  };

  const getSpeakerColor = (speaker: string) => {
    switch (speaker) {
      case 'AI':
        return 'text-primary';
      case 'User':
        return 'text-cyan-400';
      case 'System':
        return 'text-yellow-400';
      default:
        return 'text-white';
    }
  };

  return (
    <Card className="w-96 h-full bg-[#262933]/90 backdrop-blur-xl border-l border-primary/20 rounded-none shadow-2xl">
      <CardHeader className="pb-4 border-b border-primary/10">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-bold text-white flex items-center space-x-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
            <span>Live Transcript</span>
          </CardTitle>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="text-muted hover:text-white hover:bg-primary/10 transition-all duration-300"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="flex space-x-2 pt-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopyTranscript}
            className="flex-1 border-primary/30 hover:border-primary/60 hover:bg-primary/10 transition-all duration-300"
          >
            <Copy className="h-3 w-3 mr-1" />
            {copiedIndex === -1 ? 'Copied!' : 'Copy All'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadTranscript}
            className="flex-1 border-primary/30 hover:border-primary/60 hover:bg-primary/10 transition-all duration-300"
          >
            <Download className="h-3 w-3 mr-1" />
            Download
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <ScrollArea className="h-[calc(100vh-200px)] px-4">
          <div className="space-y-4 pb-4">
            {transcript.map((entry, index) => (
              <div
                key={index}
                className={`p-4 rounded-xl border transition-all duration-300 hover:border-primary/40 hover:shadow-lg ${
                  entry.speaker === 'AI' 
                    ? 'bg-primary/5 border-primary/20 hover:bg-primary/10' :
                  entry.speaker === 'User' 
                    ? 'bg-cyan-500/5 border-cyan-500/20 hover:bg-cyan-500/10' :
                  'bg-yellow-500/5 border-yellow-500/20 hover:bg-yellow-500/10'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    {getSpeakerIcon(entry.speaker)}
                    <span className={`text-sm font-semibold ${getSpeakerColor(entry.speaker)}`}>
                      {entry.speaker}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted font-mono">
                      {entry.timestamp.toLocaleTimeString()}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleCopyEntry(entry.text, index)}
                      className="h-6 w-6 text-muted hover:text-white hover:bg-primary/20 transition-all duration-300"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
                <p className="text-sm text-white leading-relaxed">
                  {copiedIndex === index ? (
                    <span className="text-green-400 font-medium">Copied!</span>
                  ) : (
                    entry.text
                  )}
                </p>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default TranscriptPanel;
