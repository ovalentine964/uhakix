import React, { useState, useCallback } from 'react';
import Head from 'next/head';
import { Header } from '../components/layout/Header';
import { Footer } from '../components/layout/Footer';
import { VoiceRecorder } from '../components/VoiceRecorder';

export default function SubmitPage() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [submitted, setSubmitted] = useState(false);
  const [reportType, setReportType] = useState<'form34a' | 'corruption' | 'anonymous'>('form34a');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    entities: '',
    evidence: '',
    email: '',
  });

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else setDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      setUploadedFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setUploadedFile(e.target.files[0]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate upload
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(r => setTimeout(r, 200));
      setUploadProgress(i);
    }
    setSubmitted(true);
  };

  const caseNumber = `UHX-${Date.now().toString(36).toUpperCase()}`;

  return (
    <div className="min-h-screen bg-gray-50">
      <Head><title>Submit Evidence — UHAKIX</title></Head>
      <Header />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Submit Evidence</h1>
        <p className="text-gray-600 mb-8">
          Report government irregularities, submit Form 34A election photos, or share anonymous tips.
          <strong className="text-blue-700"> No registration required.</strong>
        </p>

        {/* Report Type Tabs */}
        <div className="flex gap-2 mb-6">
          {[
            { key: 'form34a', label: '🗳️ Form 34A', desc: 'Election results photo' },
            { key: 'corruption', label: '🔍 Irregularity', desc: 'Report spending anomaly' },
            { key: 'anonymous', label: '🛡️ Anonymous', desc: 'Tip without identity' },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setReportType(tab.key as any)}
              className={`flex-1 p-4 rounded-xl border-2 text-center transition-all ${
                reportType === tab.key
                  ? 'border-blue-600 bg-blue-50 shadow'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="text-2xl">{tab.label.split(' ')[0]}</div>
              <div className="font-medium text-sm">{tab.label.split(' ')[1]}</div>
              <div className="text-xs text-gray-500">{tab.desc}</div>
            </button>
          ))}
        </div>

        {submitted ? (
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Submission Received</h2>
            <p className="text-gray-600 mb-4">
              Your evidence has been encrypted and queued for AI analysis.
            </p>
            <div className="bg-blue-50 rounded-lg p-4 mb-4 max-w-md mx-auto">
              <p className="text-sm text-blue-700 font-medium">Your Case Number:</p>
              <p className="text-2xl font-mono font-bold text-blue-900">{caseNumber}</p>
            </div>
            <p className="text-sm text-gray-500">Save this number to track your submission status.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow p-6 space-y-6">
            {reportType === 'form34a' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Upload Form 34A Photo</h3>
                <div
                  className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                    dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  {uploadedFile ? (
                    <div>
                      <p className="text-green-700 font-medium">✅ {uploadedFile.name}</p>
                      <p className="text-sm text-gray-500">{Math.round(uploadedFile.size / 1024)} KB</p>
                      <button
                        type="button"
                        onClick={() => setUploadedFile(null)}
                        className="text-sm text-red-600 hover:underline mt-2"
                      >
                        Remove
                      </button>
                    </div>
                  ) : (
                    <div>
                      <p className="text-4xl mb-3">📷</p>
                      <p className="text-gray-600 font-medium">Drag & drop Form 34A photo</p>
                      <p className="text-sm text-gray-500 mt-1">or</p>
                      <label className="mt-2 inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer">
                        Browse files
                        <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
                      </label>
                      <p className="text-xs text-gray-400 mt-2">PNG, JPG up to 10MB</p>
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-500 mt-3">
                  Our AI will extract: station code, candidate votes, totals, and signatures.
                </p>
              </div>
            )}

            {reportType !== 'form34a' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                  <input
                    type="text"
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Brief description of what you're reporting"
                    value={formData.title}
                    onChange={e => setFormData({...formData, title: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Details</label>
                  <textarea
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    rows={4}
                    placeholder="Describe what you observed. Include any names, amounts, dates, or locations you can share."
                    value={formData.description}
                    onChange={e => setFormData({...formData, description: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location (optional)</label>
                  <input
                    type="text"
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="County, constituency, or specific place"
                    value={formData.location}
                    onChange={e => setFormData({...formData, location: e.target.value})}
                  />
                </div>
              </>
            )}

            {reportType === 'anonymous' && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <p className="text-sm text-amber-800 font-medium">🛡️ Anonymous Mode Active</p>
                <ul className="text-xs text-amber-700 mt-1 space-y-1">
                  <li>• We do NOT log your IP address</li>
                  <li>• No email or phone required</li>
                  <li>• Your evidence is encrypted before storage</li>
                  <li>• A hash is stored on blockchain for tamper-proof verification</li>
                </ul>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Supporting Evidence (optional)</label>
              <input
                type="file"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                multiple
              />
            </div>

            {reportType !== 'anonymous' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email (optional, for case tracking)</label>
                <input
                  type="email"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={e => setFormData({...formData, email: e.target.value})}
                />
                <p className="text-xs text-gray-400 mt-1">We never share your email. Only used for status updates.</p>
              </div>
            )}

            {uploadProgress > 0 && uploadProgress < 100 && (
              <div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-600 transition-all" style={{ width: `${uploadProgress}%` }} />
                </div>
                <p className="text-sm text-gray-500 mt-1 text-center">{uploadProgress}% uploaded</p>
              </div>
            )}

            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold text-lg hover:bg-blue-700 transition-colors"
            >
              Submit Report
            </button>
          </form>
        )}

        {/* Voice Submission */}
        <div className="mt-8 bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">🎤 Submit via Voice</h3>
          <p className="text-sm text-gray-500 mb-4">Speak your report in Swahili, English, or Sheng</p>
          <VoiceRecorder
            onTranscriptionComplete={(text) => setFormData(prev => ({ ...prev, description: text }))}
            language="sw"
          />
        </div>

        {/* AI Pipeline Status */}
        <div className="mt-8 bg-white rounded-xl shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Processing Pipeline</h3>
          <div className="space-y-3">
            {[
              { agent: 'POLL WITNESS', task: 'Extract data from photo', status: reportType === 'form34a' ? 'ready' : 'skipped', model: 'Llama 3.2 Vision' },
              { agent: 'VERIFY', task: 'Check authenticity & watermarks', status: 'ready', model: 'Nemotron-4' },
              { agent: 'COUNT', task: 'Cross-verify with other submissions', status: 'ready', model: 'Llama 3.1 8B' },
              { agent: 'ALERT', task: 'Check for anomalies', status: 'ready', model: 'Nemotron-4' },
              { agent: 'LEDGER', task: 'Store hash on blockchain', status: 'ready', model: 'Polygon' },
            ].map(step => (
              <div key={step.agent} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div className="flex items-center gap-3">
                  <span className={`w-2.5 h-2.5 rounded-full ${step.status === 'ready' ? 'bg-green-500' : 'bg-gray-300'}`} />
                  <div>
                    <span className="font-medium text-sm">{step.agent}</span>
                    <span className="text-xs text-gray-500 ml-2">— {step.task}</span>
                  </div>
                </div>
                <span className="text-xs text-gray-400">{step.model}</span>
              </div>
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
