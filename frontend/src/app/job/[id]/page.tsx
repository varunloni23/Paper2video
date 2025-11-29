'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Loader2,
  Download,
  Clock,
  FileText,
  Film,
  Volume2,
  Image,
  RefreshCw,
  Play,
  Pause
} from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SlideContent {
  index: number;
  title: string;
  content: string;
  notes: string;
}

interface Job {
  id: string;
  original_filename: string;
  file_type: string;
  style_preset: string;
  avatar_option: string;
  status: string;
  progress: number;
  status_message: string;
  error_message: string | null;
  video_path: string | null;
  video_duration: number | null;
  slides_content: SlideContent[] | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

const statusSteps = [
  { key: 'pending', label: 'Pending', icon: Clock },
  { key: 'parsing', label: 'Parsing Document', icon: FileText },
  { key: 'generating_script', label: 'Generating Script', icon: FileText },
  { key: 'generating_slides', label: 'Creating Slides', icon: Image },
  { key: 'generating_audio', label: 'Generating Audio', icon: Volume2 },
  { key: 'composing_video', label: 'Composing Video', icon: Film },
  { key: 'completed', label: 'Completed', icon: CheckCircle },
];

export default function JobDetail() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;

  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSlide, setActiveSlide] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const fetchJob = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/jobs/${jobId}`);
      if (!response.ok) {
        if (response.status === 404) {
          router.push('/dashboard');
          return;
        }
        throw new Error('Failed to fetch job');
      }
      const data = await response.json();
      setJob(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load job');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (jobId) {
      fetchJob();
      
      // Auto-refresh if job is processing
      const interval = setInterval(() => {
        if (job && !['completed', 'failed'].includes(job.status)) {
          fetchJob();
        }
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [jobId, job?.status]);

  const handleRetry = async () => {
    try {
      await fetch(`${API_BASE}/api/jobs/${jobId}/retry`, { method: 'POST' });
      fetchJob();
    } catch (err) {
      console.error('Failed to retry job:', err);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStepStatus = (stepKey: string) => {
    if (!job) return 'pending';
    
    const stepOrder = statusSteps.map(s => s.key);
    const currentIndex = stepOrder.indexOf(job.status);
    const stepIndex = stepOrder.indexOf(stepKey);

    if (job.status === 'failed') {
      if (stepIndex <= currentIndex) return 'failed';
      return 'pending';
    }
    
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
          <XCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <p className="text-red-700 dark:text-red-300 mb-4">{error || 'Job not found'}</p>
          <Link href="/dashboard" className="text-primary-600 hover:underline">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const isProcessing = !['completed', 'failed'].includes(job.status);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 text-slate-600 hover:text-primary-600 dark:text-slate-400 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
        
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
              {job.original_filename}
            </h1>
            <div className="flex items-center gap-3 mt-2 text-sm text-slate-500 dark:text-slate-400">
              <span className="uppercase">{job.file_type}</span>
              <span>•</span>
              <span>{job.style_preset}</span>
              <span>•</span>
              <span>Avatar: {job.avatar_option}</span>
              <span>•</span>
              <span>Created: {formatDate(job.created_at)}</span>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {job.status === 'failed' && (
              <button
                onClick={handleRetry}
                className="inline-flex items-center gap-2 bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Retry
              </button>
            )}
            {job.status === 'completed' && (
              <a
                href={`${API_BASE}/api/jobs/${job.id}/video`}
                className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Download className="w-4 h-4" />
                Download Video
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Status Steps */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 mb-8">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">Processing Status</h2>
        
        <div className="relative">
          {/* Progress Line */}
          <div className="absolute top-5 left-0 right-0 h-0.5 bg-slate-200 dark:bg-slate-700" />
          
          {/* Steps */}
          <div className="relative flex justify-between">
            {statusSteps.map((step, index) => {
              const status = getStepStatus(step.key);
              const Icon = step.icon;
              
              return (
                <div key={step.key} className="flex flex-col items-center" style={{ flex: 1 }}>
                  <div
                    className={`
                      w-10 h-10 rounded-full flex items-center justify-center z-10
                      ${status === 'completed' ? 'bg-green-500 text-white' : ''}
                      ${status === 'active' ? 'bg-primary-600 text-white animate-pulse' : ''}
                      ${status === 'failed' ? 'bg-red-500 text-white' : ''}
                      ${status === 'pending' ? 'bg-slate-200 dark:bg-slate-700 text-slate-400' : ''}
                    `}
                  >
                    {status === 'active' && isProcessing ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : status === 'failed' && step.key === job.status ? (
                      <XCircle className="w-5 h-5" />
                    ) : status === 'completed' ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                  </div>
                  <span className={`
                    text-xs mt-2 text-center
                    ${status === 'active' ? 'text-primary-600 font-medium' : ''}
                    ${status === 'completed' ? 'text-green-600' : ''}
                    ${status === 'failed' ? 'text-red-600' : ''}
                    ${status === 'pending' ? 'text-slate-400' : ''}
                  `}>
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Current Status Message */}
        <div className="mt-8 text-center">
          {isProcessing && (
            <>
              <p className="text-slate-600 dark:text-slate-300">{job.status_message}</p>
              <div className="mt-4 max-w-md mx-auto">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-slate-600 dark:text-slate-400">Overall Progress</span>
                  <span className="text-slate-900 dark:text-white font-medium">{job.progress}%</span>
                </div>
                <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden">
                  <div
                    className="h-full progress-animated rounded-full transition-all duration-500"
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
              </div>
            </>
          )}
          
          {job.status === 'completed' && (
            <div className="flex items-center justify-center gap-2 text-green-600">
              <CheckCircle className="w-5 h-5" />
              <span>Video generation completed successfully!</span>
            </div>
          )}
          
          {job.status === 'failed' && (
            <div className="text-red-600">
              <div className="flex items-center justify-center gap-2 mb-2">
                <XCircle className="w-5 h-5" />
                <span>Processing failed</span>
              </div>
              {job.error_message && (
                <p className="text-sm text-red-500">{job.error_message}</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Video Player */}
      {job.status === 'completed' && job.video_path && (
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Generated Video</h2>
          
          <div className="aspect-video bg-black rounded-lg overflow-hidden">
            <video
              controls
              className="w-full h-full"
              src={`${API_BASE}/api/jobs/${job.id}/video`}
              poster={`${API_BASE}/api/jobs/${job.id}/thumbnail`}
            >
              Your browser does not support the video tag.
            </video>
          </div>
          
          {job.video_duration && (
            <div className="mt-4 flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
              <span>Duration: {formatDuration(job.video_duration)}</span>
              <a
                href={`${API_BASE}/api/jobs/${job.id}/video`}
                download
                className="inline-flex items-center gap-2 text-primary-600 hover:underline"
              >
                <Download className="w-4 h-4" />
                Download MP4
              </a>
            </div>
          )}
        </div>
      )}

      {/* Slides Preview */}
      {job.slides_content && job.slides_content.length > 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Slides Preview</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Slide List */}
            <div className="lg:col-span-1 space-y-2 max-h-96 overflow-y-auto">
              {job.slides_content.map((slide, index) => (
                <button
                  key={index}
                  onClick={() => setActiveSlide(index)}
                  className={`
                    w-full text-left p-3 rounded-lg transition-colors
                    ${activeSlide === index 
                      ? 'bg-primary-100 dark:bg-primary-900/30 border-2 border-primary-500' 
                      : 'bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 border-2 border-transparent'
                    }
                  `}
                >
                  <div className="flex items-center gap-3">
                    <span className={`
                      w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium
                      ${activeSlide === index 
                        ? 'bg-primary-600 text-white' 
                        : 'bg-slate-200 dark:bg-slate-600 text-slate-600 dark:text-slate-300'
                      }
                    `}>
                      {index + 1}
                    </span>
                    <span className="text-sm font-medium text-slate-900 dark:text-white truncate">
                      {slide.title}
                    </span>
                  </div>
                </button>
              ))}
            </div>
            
            {/* Active Slide */}
            <div className="lg:col-span-2">
              <div className="bg-slate-900 rounded-lg p-8 aspect-video flex flex-col justify-center">
                <h3 className="text-2xl font-bold text-white mb-4">
                  {job.slides_content[activeSlide].title}
                </h3>
                <p className="text-slate-300 whitespace-pre-wrap">
                  {job.slides_content[activeSlide].content}
                </p>
              </div>
              
              {job.slides_content[activeSlide].notes && (
                <div className="mt-4 p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                  <h4 className="text-sm font-medium text-slate-900 dark:text-white mb-2">Speaker Notes:</h4>
                  <p className="text-sm text-slate-600 dark:text-slate-300">
                    {job.slides_content[activeSlide].notes}
                  </p>
                </div>
              )}
              
              {/* Slide Navigation */}
              <div className="mt-4 flex items-center justify-between">
                <button
                  onClick={() => setActiveSlide(Math.max(0, activeSlide - 1))}
                  disabled={activeSlide === 0}
                  className="px-4 py-2 text-sm text-slate-600 dark:text-slate-300 hover:text-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  {activeSlide + 1} / {job.slides_content.length}
                </span>
                <button
                  onClick={() => setActiveSlide(Math.min(job.slides_content!.length - 1, activeSlide + 1))}
                  disabled={activeSlide === job.slides_content.length - 1}
                  className="px-4 py-2 text-sm text-slate-600 dark:text-slate-300 hover:text-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
