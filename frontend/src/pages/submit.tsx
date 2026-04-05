'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useElectionStore } from '@/store';
import { electionApi } from '@/services/api';
import toast from 'react-hot-toast';

export default function SubmitForm34A() {
  const { submissionStatus, setSubmissionStatus, setSubmissionResult, resetSubmission } = useElectionStore();
  const [submitterName, setSubmitterName] = useState('');
  const [submissionId, setSubmissionId] = useState('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      toast.error('Image too large (max 10MB)');
      return;
    }

    setSubmissionStatus('uploading');
    const toastId = toast.loading('Submitting Form 34A...');

    try {
      const result = await electionApi.submitForm34A(file, submitterName || undefined);
      setSubmissionResult(result.data);
      setSubmissionId(result.data.submission_id);
      setSubmissionStatus('processing');
      toast.success('Form 34A submitted! AI agents are verifying...', { id: toastId });
    } catch (error) {
      toast.error('Failed to submit. Please try again.', { id: toastId });
      setSubmissionStatus('idle');
    }
  }, [submitterName]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png'] },
    maxFiles: 1,
    disabled: submissionStatus === 'uploading' || submissionStatus === 'processing',
  });

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Report Form 34A</h1>
        <p className="text-gray-600 mb-8">
          Upload a photo of your polling station&apos;s Form 34A. No ID required.
          Your submission is verified by AI and recorded on the blockchain.
        </p>

        {/* Upload Zone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition ${
            isDragActive ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-green-400'
          } ${submissionStatus === 'uploading' ? 'opacity-50 pointer-events-none' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="text-5xl mb-4">📷</div>
          <p className="text-lg font-medium text-gray-700">
            {isDragActive ? 'Drop the photo here' : 'Drag & drop Form 34A photo'}
          </p>
          <p className="text-sm text-gray-500 mt-2">or click to browse • JPG, PNG (max 10MB)</p>
        </div>

        {/* Name (Optional) */}
        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Your Name (optional — helps track your submissions)
          </label>
          <input
            type="text"
            value={submitterName}
            onChange={(e) => setSubmitterName(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-4 py-2"
            placeholder="e.g., Jane Wanjiku"
          />
        </div>

        {/* Status */}
        {submissionStatus !== 'idle' && (
          <div className="mt-8 p-4 bg-white rounded-lg border">
            <h3 className="font-bold mb-2">Submission Status</h3>
            {submissionStatus === 'uploading' && (
              <p className="text-blue-600">⏳ Uploading photo...</p>
            )}
            {submissionStatus === 'processing' && (
              <div>
                <p className="text-yellow-600">🔄 AI agents are processing your Form 34A:</p>
                <ul className="mt-2 text-sm text-gray-600 space-y-1">
                  <li>1. POLL WITNESS Agent — Extracting data ✓</li>
                  <li>2. VERIFY Agent — Checking authenticity</li>
                  <li>3. COUNT Agent — Aggregating votes</li>
                  <li>4. ALERT Agent — Checking for anomalies</li>
                  <li>5. LEDGER Agent — Recording on blockchain</li>
                </ul>
              </div>
            )}
            {submissionId && (
              <p className="mt-2 text-xs text-gray-500">ID: {submissionId}</p>
            )}
          </div>
        )}

        {/* Info */}
        <div className="mt-8 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
          <h3 className="font-bold text-yellow-800 mb-2">ℹ️ What is Form 34A?</h3>
          <p className="text-sm text-yellow-700">
            Form 34A is the Polling Station Results Form issued by IEBC after counting votes.
            It shows votes cast for each candidate at your specific polling station.
            By aggregating citizen-uploaded Form 34As, we can independently verify election results.
          </p>
        </div>
      </div>
    </main>
  );
}
