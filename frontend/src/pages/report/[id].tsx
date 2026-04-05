import { useRouter } from 'next/router';
import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { Header } from '../../components/layout/Header';
import { Footer } from '../../components/layout/Footer';

const PIPELINE_STEPS = [
  { name: 'Submitted', icon: '📤', desc: 'Report received and encrypted' },
  { name: 'Transcribed', icon: '📝', desc: 'AI transcription completed' },
  { name: 'Analysed', icon: '🔍', desc: 'SPHINX anomaly detection' },
  { name: 'Verified', icon: '✅', desc: 'SHIELD compliance review' },
  { name: 'Published', icon: '📢', desc: 'Report is live on the dashboard' },
];

export default function ReportPage() {
  const router = useRouter();
  const { id } = router.query;
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    // In production: fetch from API
    setTimeout(() => {
      setReport({
        id,
        type: 'Form 34A Submission',
        status: 3, // 0-4 pipeline step index
        submittedAt: '2025-07-14T08:30:00Z',
        stationCode: '071/042',
        stationName: 'Uhuru Primary School',
        constituency: 'Westlands',
        county: 'Nairobi',
        pipeline: [
          { step: 'Submitted', status: 'complete', time: '08:30 AM', details: 'Photo received, encrypted with AES-256' },
          { step: 'Transcribed', status: 'complete', time: '08:30 AM', details: 'OCR extracted station code, votes, totals' },
          { step: 'Analysed', status: 'complete', time: '08:32 AM', details: 'No anomalies detected, math checks out' },
          { step: 'Verified', status: 'processing', time: '08:33 AM', details: 'Running SHIELD compliance check' },
          { step: 'Published', status: 'pending', time: null, details: null },
        ],
        blockchainHash: null,
      });
      setLoading(false);
    }, 500);
  }, [id]);

  if (loading) return <LoadingSkeleton />;

  return (
    <div className="min-h-screen bg-gray-50">
      <Head><title>Report #{id} — UHAKIX</title></Head>
      <Header />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <button onClick={() => router.back()} className="text-blue-600 hover:underline mb-4 text-sm">← Back</button>
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Report Tracker</h1>
        
        {report && (
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-start justify-between mb-6">
              <div>
                <p className="text-sm text-gray-500">Report ID: <span className="font-mono">{report.id}</span></p>
                <h2 className="text-xl font-bold mt-1">{report.type}</h2>
              </div>
              <StatusBadge status={PIPELINE_STEPS[report.status]?.name || 'Processing'} />
            </div>

            {/* Station Info */}
            {report.stationCode && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 bg-gray-50 rounded-lg p-4">
                <div><p className="text-xs text-gray-500">Station Code</p><p className="font-mono font-bold">{report.stationCode}</p></div>
                <div><p className="text-xs text-gray-500">Station</p><p className="font-medium">{report.stationName}</p></div>
                <div><p className="text-xs text-gray-500">Constituency</p><p className="font-medium">{report.constituency}</p></div>
                <div><p className="text-xs text-gray-500">County</p><p className="font-medium">{report.county}</p></div>
              </div>
            )}

            {/* Pipeline */}
            <h3 className="font-semibold text-gray-900 mb-4">Processing Pipeline</h3>
            <div className="space-y-4">
              {report.pipeline.map((step: any, i: number) => (
                <div key={step.step} className="flex items-start gap-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    step.status === 'complete' ? 'bg-green-500 text-white' :
                    step.status === 'processing' ? 'bg-blue-500 text-white animate-pulse' :
                    'bg-gray-200 text-gray-500'
                  }`}>
                    {step.status === 'complete' ? '✓' : i + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">{step.step}</h4>
                      {step.time && <span className="text-xs text-gray-400">{step.time}</span>}
                    </div>
                    {step.details && <p className="text-sm text-gray-500 mt-1">{step.details}</p>}
                  </div>
                </div>
              ))}
            </div>

            {/* Blockchain */}
            {report.blockchainHash && (
              <div className="mt-6 p-4 bg-purple-50 rounded-lg">
                <p className="text-xs text-purple-700 font-medium">Blockchain Record</p>
                <p className="text-xs font-mono text-purple-600 mt-1">{report.blockchainHash}</p>
              </div>
            )}
          </div>
        )}

        {!report && (
          <p className="text-gray-500 text-center py-8">Report not found. Please check the ID.</p>
        )}
      </main>
      <Footer />
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    Submitted: 'bg-blue-100 text-blue-800',
    Published: 'bg-green-100 text-green-800',
  };
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
      {status}
    </span>
  );
}

function LoadingSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="animate-pulse text-gray-500">Loading report...</div>
    </div>
  );
}
