import React, {useState} from 'react';
import {CheckCircle, FileAudio, Loader2, Upload, XCircle} from 'lucide-react';

export default function WhisperTranscriptionApp() {
  const [file, setFile] = useState  < File | null > (null);
  const [isDragging, setIsDragging] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // API Endpoint - passe dies an deine FastAPI URL an
  const API_URL = 'http://localhost:8000/transcribe';

  const handleDragOver = (e:any) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e:any) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e:any) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'audio/mpeg') {
      setFile(droppedFile);
      setError('');
      setTranscription('');
      setSuccess(false);
    } else {
      setError('Bitte nur MP3-Dateien hochladen');
    }
  };

  const handleFileInput = (e:any) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'audio/mpeg') {
      setFile(selectedFile);
      setError('');
      setTranscription('');
      setSuccess(false);
    } else {
      setError('Bitte nur MP3-Dateien hochladen');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError('');
    setSuccess(false);
    setTranscription('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server-Fehler: ${response.status}`);
      }

      const data = await response.json();
      setTranscription(data);
      setSuccess(true);
    } catch (e) {
      setError(`Fehler beim Transkribieren: ${(e as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setTranscription('');
    setError('');
    setSuccess(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              Open AI Transkription
            </h1>
            <p className="text-gray-600">
              Lade deine MP3-Datei hoch und erhalte eine Texttranskription.
            </p>
          </div>

          {/* Drag & Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-4 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
              isDragging
                ? 'border-indigo-500 bg-indigo-50'
                : 'border-gray-300 bg-gray-50'
            }`}
          >
            {!file ? (
              <div>
                <Upload className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                <p className="text-xl text-gray-700 mb-2">
                  MP3-Datei hierher ziehen
                </p>
                <p className="text-sm text-gray-500 mb-4">oder</p>
                <label className="cursor-pointer">
                  <span className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors inline-block">
                    Datei vom Gerät hochladen
                  </span>
                  <input
                    type="file"
                    accept="audio/mpeg"
                    onChange={handleFileInput}
                    className="hidden"
                  />
                </label>
              </div>
            ) : (
              <div className="flex items-center justify-center gap-4">
                <FileAudio className="h-12 w-12 text-indigo-600" />
                <div className="text-left">
                  <p className="text-lg font-semibold text-gray-800">
                    {file.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          {file && (
            <div className="flex gap-4 mt-6">
              <button
                onClick={handleUpload}
                disabled={loading}
                className="flex-1 bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="animate-spin h-5 w-5" />
                    Transkribiere...
                  </>
                ) : (
                  'Transkribieren'
                )}
              </button>
              <button
                onClick={handleReset}
                disabled={loading}
                className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Zurücksetzen
              </button>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-6 bg-red-50 border-l-4 border-red-500 p-4 rounded">
              <div className="flex items-center gap-2">
                <XCircle className="h-5 w-5 text-red-500" />
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="mt-6 bg-green-50 border-l-4 border-green-500 p-4 rounded">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <p className="text-green-700">Transkription erfolgreich!</p>
              </div>
            </div>
          )}

          {/* Transcription Result */}
          {transcription && (
            <div className="mt-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                Transkription:
              </h2>
              <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                  {transcription}
                </p>
              </div>
              <button
                onClick={() => navigator.clipboard.writeText(transcription)}
                className="mt-4 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Text kopieren
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}