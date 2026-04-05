import React, { useState, useRef, useCallback } from 'react';
import { Mic, Square, Play, Upload } from 'lucide-react';

interface VoiceRecorderProps {
  onTranscriptionComplete?: (text: string) => void;
  language?: string;
}

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({ onTranscriptionComplete, language = 'sw' }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      mediaRecorder.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };

      mediaRecorder.current.onstop = () => {
        const blob = new Blob(audioChunks.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        // Stop all tracks to release the microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Microphone access denied:', err);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop();
      setIsRecording(false);
    }
  }, []);

  const discardRecording = useCallback(() => {
    setAudioBlob(null);
  }, []);

  const playRecording = useCallback(() => {
    if (!audioBlob) return;
    const url = URL.createObjectURL(audioBlob);
    if (audioRef.current) {
      audioRef.current.src = url;
      audioRef.current.play();
      setIsPlaying(true);
      audioRef.current.onended = () => setIsPlaying(false);
    }
  }, [audioBlob]);

  const submitRecording = useCallback(async () => {
    if (!audioBlob) return;
    setIsTranscribing(true);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      if (language) formData.append('language', language);

      const response = await fetch('/api/v1/voice/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Transcription failed');
      }

      const data = await response.json();
      if (data.text && onTranscriptionComplete) {
        onTranscriptionComplete(data.text);
      }
    } catch (err) {
      console.error('Voice transcription error:', err);
    } finally {
      setIsTranscribing(false);
    }
  }, [audioBlob, language, onTranscriptionComplete]);

  return (
    <div className="flex flex-col items-center gap-3">
      {audioBlob && !isRecording && (
        <div className="flex items-center gap-2 mb-2">
          <button
            onClick={playRecording}
            className={`p-2 rounded-full transition-colors ${
              isPlaying ? 'bg-amber-500 hover:bg-amber-600' : 'bg-blue-500 hover:bg-blue-600'
            } text-white`}
            title="Preview"
          >
            {isPlaying ? <Square size={20} /> : <Play size={20} />}
          </button>
          <button
            onClick={discardRecording}
            className="p-2 rounded-full bg-gray-300 hover:bg-gray-400 text-gray-700 transition-colors"
            title="Discard"
          >
            ✕
          </button>
          <button
            onClick={submitRecording}
            disabled={isTranscribing}
            className="px-4 py-2 rounded-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium transition-colors flex items-center gap-2"
          >
            <Upload size={16} />
            {isTranscribing ? 'Transcribing...' : 'Submit'}
          </button>
        </div>
      )}

      <button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isTranscribing}
        className={`rounded-full p-4 shadow-lg transition-all transform hover:scale-105 disabled:opacity-50 ${
          isRecording
            ? 'bg-red-600 hover:bg-red-700 animate-pulse'
            : 'bg-blue-600 hover:bg-blue-700'
        } text-white`}
      >
        {isRecording ? <Square size={28} /> : <Mic size={28} />}
      </button>

      <p className="text-sm text-gray-500 text-center max-w-32">
        {isRecording ? 'Tap to stop' : isTranscribing ? 'Processing...' : 'Tap to speak'}
      </p>

      {/* Hidden audio element for playback */}
      <audio ref={audioRef} className="hidden" />
    </div>
  );
};

// ── Voice Response Player ──────────────────────────

interface VoiceResponsePlayerProps {
  audioUrl: string;
  autoPlay?: boolean;
}

export const VoiceResponsePlayer: React.FC<VoiceResponsePlayerProps> = ({ audioUrl, autoPlay = false }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  const togglePlayback = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  return (
    <div className="flex items-center gap-2 p-2 rounded-lg bg-gray-50">
      <button
        onClick={togglePlayback}
        className="p-2 rounded-full bg-green-600 hover:bg-green-700 text-white transition-colors"
      >
        {isPlaying ? <Square size={18} /> : <Play size={18} />}
      </button>
      <span className="text-sm text-gray-600">
        {isPlaying ? 'Playing response...' : 'Listen to response'}
      </span>
      <audio
        ref={audioRef}
        src={audioUrl}
        onEnded={() => setIsPlaying(false)}
        className="hidden"
      />
    </div>
  );
};
