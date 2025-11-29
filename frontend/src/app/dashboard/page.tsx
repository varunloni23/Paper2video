'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  Video,
  ArrowRight,
  RefreshCw,
  Trash2,
  FileText
} from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

const statusConfig: Record<string, { icon: any; color: string; bg: string }> = {
  pending: { icon: Clock, color: 'text-amber-600', bg: 'bg-amber-100' },
  parsing: { icon: Loader2, color: 'text-blue-600', bg: 'bg-blue-100' },
  generating_script: { icon: Loader2, color: 'text-blue-600', bg: 'bg-blue-100' },
  generating_slides: { icon: Loader2, color: 'text-blue-600', bg: 'bg-blue-100' },
  generating_audio: { icon: Loader2, color: 'text-blue-600', bg: 'bg-blue-100' },
  composing_video: { icon: Loader2, color: 'text-blue-600', bg: 'bg-blue-100' },
  completed: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100' },
  failed: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-100' },
};

export default function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/jobs`);
      if (!response.ok) throw new Error('Failed to fetch jobs');
      const data = await response.json();
      setJobs(data.jobs);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleDelete = async (jobId: string) => {
    if (!confirm('Are you sure you want to delete this job?')) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/jobs/${jobId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setJobs(jobs.filter(j => j.id !== jobId));
      }
    } catch (err) {
      console.error('Failed to delete job:', err);
    }
  };

  const handleRetry = async (jobId: string) => {
    try {
      await fetch(`${API_BASE}/api/jobs/${jobId}/retry`, { method: 'POST' });
      fetchJobs();
    } catch (err) {
      console.error('Failed to retry job:', err);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Job Dashboard</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Manage your video generation jobs
          </p>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={fetchJobs}
            className="inline-flex items-center gap-2 text-slate-600 hover:text-primary-600 dark:text-slate-300"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <Link
            href="/"
            className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            New Upload
          </Link>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Jobs List */}
      {jobs.length === 0 ? (
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-12 text-center">
          <FileText className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">No jobs yet</h3>
          <p className="text-slate-600 dark:text-slate-400 mb-6">
            Upload your first research paper to get started
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg transition-colors"
          >
            Upload Paper
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => {
            const status = statusConfig[job.status] || statusConfig.pending;
            const StatusIcon = status.icon;
            const isProcessing = ['parsing', 'generating_script', 'generating_slides', 'generating_audio', 'composing_video'].includes(job.status);

            return (
              <div
                key={job.id}
                className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden card-hover"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      {/* Status Icon */}
                      <div className={`w-10 h-10 rounded-full ${status.bg} flex items-center justify-center flex-shrink-0`}>
                        <StatusIcon className={`w-5 h-5 ${status.color} ${isProcessing ? 'animate-spin' : ''}`} />
                      </div>

                      {/* Job Info */}
                      <div>
                        <h3 className="font-semibold text-slate-900 dark:text-white mb-1">
                          {job.original_filename}
                        </h3>
                        <div className="flex items-center gap-3 text-sm text-slate-500 dark:text-slate-400">
                          <span className="uppercase">{job.file_type}</span>
                          <span>•</span>
                          <span>{job.style_preset}</span>
                          <span>•</span>
                          <span>Avatar: {job.avatar_option}</span>
                        </div>
                        <p className="text-sm text-slate-600 dark:text-slate-300 mt-2">
                          {job.status_message || job.status.replace(/_/g, ' ')}
                        </p>
                        {job.error_message && (
                          <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                            Error: {job.error_message}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      {job.status === 'completed' && (
                        <>
                          <Link
                            href={`/job/${job.id}`}
                            className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                          >
                            <Video className="w-4 h-4" />
                            View
                          </Link>
                          <a
                            href={`${API_BASE}/api/jobs/${job.id}/video`}
                            className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                          >
                            Download
                          </a>
                        </>
                      )}
                      {job.status === 'failed' && (
                        <button
                          onClick={() => handleRetry(job.id)}
                          className="inline-flex items-center gap-2 bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                        >
                          <RefreshCw className="w-4 h-4" />
                          Retry
                        </button>
                      )}
                      {isProcessing && (
                        <Link
                          href={`/job/${job.id}`}
                          className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                        >
                          View Progress
                        </Link>
                      )}
                      <button
                        onClick={() => handleDelete(job.id)}
                        className="p-2 text-slate-400 hover:text-red-600 transition-colors"
                        title="Delete job"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {isProcessing && (
                    <div className="mt-4">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-slate-600 dark:text-slate-400">Progress</span>
                        <span className="text-slate-900 dark:text-white font-medium">{job.progress}%</span>
                      </div>
                      <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full progress-animated rounded-full transition-all duration-500"
                          style={{ width: `${job.progress}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Footer Info */}
                  <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700 flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
                    <span>Created: {formatDate(job.created_at)}</span>
                    {job.video_duration && (
                      <span>Duration: {formatDuration(job.video_duration)}</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
