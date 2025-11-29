'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import Link from 'next/link';
import { 
  Upload, 
  FileText, 
  Video, 
  Sparkles, 
  ArrowRight,
  CheckCircle,
  Loader2,
  AlertCircle
} from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UploadResponse {
  job_id: string;
  status: string;
  message: string;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [stylePreset, setStylePreset] = useState<'concise' | 'detailed'>('concise');
  const [avatarOption, setAvatarOption] = useState<'none' | 'svg' | 'realistic'>('svg');
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError(null);
      setUploadResult(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/zip': ['.zip']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('style_preset', stylePreset);
    formData.append('avatar_option', avatarOption);

    try {
      const response = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data: UploadResponse = await response.json();
      setUploadResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleStartProcessing = async () => {
    if (!uploadResult?.job_id) return;

    setStarting(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/jobs/${uploadResult.job_id}/start`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start processing');
      }

      // Redirect to job page
      window.location.href = `/job/${uploadResult.job_id}`;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start processing');
      setStarting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-white mb-6">
          Transform Your Research into
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-accent-500"> Video Presentations</span>
        </h1>
        <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto">
          Upload your research paper and let AI create an engaging video presentation with slides, narration, and a virtual presenter.
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-6 mb-16">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg card-hover">
          <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mb-4">
            <FileText className="w-6 h-6 text-primary-600" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Smart Parsing</h3>
          <p className="text-slate-600 dark:text-slate-300">Upload PDF, DOCX, PPTX, or LaTeX files. Our AI extracts and understands your content.</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg card-hover">
          <div className="w-12 h-12 bg-accent-100 dark:bg-accent-900 rounded-lg flex items-center justify-center mb-4">
            <Sparkles className="w-6 h-6 text-accent-600" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">AI-Powered Scripts</h3>
          <p className="text-slate-600 dark:text-slate-300">Gemini AI generates engaging slide scripts and natural narration for your presentation.</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg card-hover">
          <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mb-4">
            <Video className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Video Generation</h3>
          <p className="text-slate-600 dark:text-slate-300">Get a professional video with slides, voiceover, and optional talking-head avatar.</p>
        </div>
      </div>

      {/* Upload Section */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 mb-8">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Upload Your Paper</h2>
        
        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`dropzone border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
            isDragActive 
              ? 'dropzone-active border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
              : 'border-slate-300 dark:border-slate-600 hover:border-primary-400 hover:bg-slate-50 dark:hover:bg-slate-700/50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className={`w-16 h-16 mx-auto mb-4 ${isDragActive ? 'text-primary-500' : 'text-slate-400'}`} />
          {file ? (
            <div>
              <p className="text-lg font-medium text-slate-900 dark:text-white mb-2">
                Selected: {file.name}
              </p>
              <p className="text-sm text-slate-500">
                {(file.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          ) : isDragActive ? (
            <p className="text-lg text-primary-600 dark:text-primary-400">Drop your file here...</p>
          ) : (
            <div>
              <p className="text-lg text-slate-600 dark:text-slate-300 mb-2">
                Drag & drop your research paper here
              </p>
              <p className="text-sm text-slate-500">
                or click to browse (PDF, DOCX, PPTX, ZIP for LaTeX)
              </p>
            </div>
          )}
        </div>

        {/* Options */}
        {file && !uploadResult && (
          <div className="mt-8 grid md:grid-cols-2 gap-6">
            {/* Style Preset */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                Presentation Style
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setStylePreset('concise')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    stylePreset === 'concise'
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-slate-200 dark:border-slate-600 hover:border-slate-300'
                  }`}
                >
                  <div className="font-medium text-slate-900 dark:text-white">Concise</div>
                  <div className="text-sm text-slate-500">5-8 slides, quick overview</div>
                </button>
                <button
                  onClick={() => setStylePreset('detailed')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    stylePreset === 'detailed'
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-slate-200 dark:border-slate-600 hover:border-slate-300'
                  }`}
                >
                  <div className="font-medium text-slate-900 dark:text-white">Detailed</div>
                  <div className="text-sm text-slate-500">8-12 slides, comprehensive</div>
                </button>
              </div>
            </div>

            {/* Avatar Option */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                Avatar Option
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={() => setAvatarOption('none')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    avatarOption === 'none'
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-slate-200 dark:border-slate-600 hover:border-slate-300'
                  }`}
                >
                  <div className="font-medium text-slate-900 dark:text-white">None</div>
                  <div className="text-xs text-slate-500">Slides only</div>
                </button>
                <button
                  onClick={() => setAvatarOption('svg')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    avatarOption === 'svg'
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-slate-200 dark:border-slate-600 hover:border-slate-300'
                  }`}
                >
                  <div className="font-medium text-slate-900 dark:text-white">SVG Avatar</div>
                  <div className="text-xs text-slate-500">Animated</div>
                </button>
                <button
                  onClick={() => setAvatarOption('realistic')}
                  className={`p-4 rounded-lg border-2 transition-all relative ${
                    avatarOption === 'realistic'
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-slate-200 dark:border-slate-600 hover:border-slate-300'
                  }`}
                >
                  <div className="font-medium text-slate-900 dark:text-white">Realistic</div>
                  <div className="text-xs text-slate-500">Coming soon</div>
                  <span className="absolute -top-2 -right-2 bg-amber-500 text-white text-xs px-2 py-0.5 rounded-full">
                    Pro
                  </span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <p className="text-red-700 dark:text-red-300">{error}</p>
          </div>
        )}

        {/* Upload Success */}
        {uploadResult && (
          <div className="mt-6 p-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle className="w-6 h-6 text-green-500" />
              <p className="text-green-700 dark:text-green-300 font-medium">File uploaded successfully!</p>
            </div>
            <p className="text-slate-600 dark:text-slate-400 mb-4">
              Job ID: <code className="bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">{uploadResult.job_id}</code>
            </p>
            <button
              onClick={handleStartProcessing}
              disabled={starting}
              className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-medium px-6 py-3 rounded-lg transition-colors disabled:opacity-50"
            >
              {starting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Start Processing
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        )}

        {/* Upload Button */}
        {file && !uploadResult && (
          <div className="mt-8 flex justify-center">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-medium px-8 py-4 rounded-lg text-lg transition-colors disabled:opacity-50"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  Upload Paper
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* View Jobs Link */}
      <div className="text-center">
        <Link 
          href="/dashboard"
          className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium inline-flex items-center gap-2"
        >
          View all jobs
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
