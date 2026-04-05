import React, { useEffect, useState } from 'react';
import Head from 'next/head';
import { Header } from '../components/layout/Header';
import { Footer } from '../components/layout/Footer';
import { api } from '../services/api';
import { kenyanCounties } from '../constants';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#1e40af', '#059669', '#d97706', '#dc2626'];

interface ElectionData {
  constituency: string;
  county: string;
  totalStations: number;
  stationsReported: number;
  reportingPct: number;
  results: Record<string, number>;
}

interface ElectionAlert {
  id: string;
  alertType: string;
  severity: string;
  location: string;
  description: string;
  createdAt: string;
}

export default function ElectionPage() {
  const [activeTab, setActiveTab] = useState<'national' | 'county' | 'alerts'>('national');
  const [electionData, setElectionData] = useState<ElectionData[]>([]);
  const [alerts, setAlerts] = useState<ElectionAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCounty, setSelectedCounty] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        // In production: await api.get('/api/v1/election/results/national')
        setElectionData(generateSampleElectionData());
        setAlerts(generateSampleAlerts());
      } catch (err) {
        console.error('Election data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const totalStations = 46229;
  const totalReported = Math.floor(totalStations * 0.73);
  const candidates = ['Candidate A', 'Candidate B', 'Candidate C', 'Candidate D'];

  return (
    <div className="min-h-screen bg-gray-50">
      <Head><title>Election Monitoring — UHAKIX</title></Head>
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Live Election Monitoring</h1>
          <p className="text-gray-600 mt-1">
            Real-time results from citizen-verified Form 34A submissions, cross-referenced and stored on blockchain
          </p>
        </div>

        {/* National Stats Bar */}
        <div className="bg-gradient-to-r from-blue-900 to-blue-700 rounded-xl p-6 mb-8 text-white">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-sm opacity-75">Reporting Stations</p>
              <p className="text-3xl font-bold">{totalReported.toLocaleString()}</p>
              <p className="text-xs opacity-75">of {totalStations.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm opacity-75">Reporting %</p>
              <p className="text-3xl font-bold">73.2%</p>
            </div>
            <div>
              <p className="text-sm opacity-75">Forms Verified</p>
              <p className="text-3xl font-bold">41,025</p>
            </div>
            <div>
              <p className="text-sm opacity-75">Blockchain Records</p>
              <p className="text-3xl font-bold">41,025</p>
            </div>
          </div>
          <div className="mt-4 bg-white/20 rounded-full h-3">
            <div className="bg-green-400 h-3 rounded-full transition-all" style={{ width: '73.2%' }} />
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6">
          {(['national', 'county', 'alerts'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {tab === 'national' ? '📊 National' : tab === 'county' ? '🗺️ By County' : '🚨 Anomaly Alerts'}
            </button>
          ))}
        </div>

        {activeTab === 'national' && (
          <div className="space-y-8">
            {/* National Results */}
            <div className="bg-white rounded-xl shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Presidential Results</h2>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={[
                    { candidate: 'Candidate A', votes: 6850429 },
                    { candidate: 'Candidate B', votes: 6432801 },
                    { candidate: 'Candidate C', votes: 1042560 },
                    { candidate: 'Candidate D', votes: 359821 },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="candidate" />
                    <YAxis tickFormatter={(v: number) => `${(v/1e6).toFixed(1)}M`} />
                    <Tooltip formatter={(v: number) => v.toLocaleString()} />
                    <Bar dataKey="votes" fill="#1e40af" radius={[4, 4, 0, 0]}>
                      {candidates.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Reporting by County */}
            <div className="bg-white rounded-xl shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">County Reporting Progress</h2>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={kenyanCounties.slice(0, 20).map(c => ({
                    name: c.substring(0, 12),
                    reporting: Math.floor(Math.random() * 30) + 50,
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis tickFormatter={(v: number) => `${v}%`} />
                    <Tooltip formatter={(v: number) => `${v}%`} />
                    <Bar dataKey="reporting" fill="#059669" name="Reporting %" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'county' && (
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">County Results Explorer</h2>
            <select
              className="w-full md:w-64 rounded-lg border border-gray-300 px-3 py-2 mb-6"
              value={selectedCounty}
              onChange={(e) => setSelectedCounty(e.target.value)}
            >
              <option value="">— Select a County —</option>
              {kenyanCounties.map(c => <option key={c} value={c}>{c}</option>)}
            </select>

            {selectedCounty ? (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">{selectedCounty} County</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <StatBadge label="Total Stations" value="1,247" />
                  <StatBadge label="Reported" value="1,089" />
                  <StatBadge label="Reporting" value="87.3%" />
                  <StatBadge label="Verified" value="98.1%" />
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Select a county to view detailed results</p>
            )}
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Anomaly Alerts</h2>
            {loading ? (
              <AlertSkeleton />
            ) : alerts.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No anomalies detected</p>
            ) : (
              alerts.map(alert => (
                <div
                  key={alert.id}
                  className={`bg-white rounded-xl shadow p-4 border-l-4 ${
                    alert.severity === 'critical' ? 'border-red-600' :
                    alert.severity === 'high' ? 'border-orange-500' :
                    'border-amber-400'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900">{alert.alertType}</h3>
                      <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
                      <p className="text-xs text-gray-400 mt-1">📍 {alert.location} · {alert.createdAt}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                      'bg-amber-100 text-amber-800'
                    }`}>
                      {alert.severity}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}

function StatBadge({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3 text-center">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

function AlertSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3, 4].map(i => (
        <div key={i} className="bg-white rounded-xl shadow p-4 animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
          <div className="h-3 bg-gray-100 rounded w-3/4 mb-1" />
          <div className="h-3 bg-gray-100 rounded w-1/4" />
        </div>
      ))}
    </div>
  );
}

function generateSampleElectionData(): ElectionData[] {
  return kenyanCounties.map(county => ({
    constituency: `${county} Central`,
    county,
    totalStations: Math.floor(Math.random() * 500) + 200,
    stationsReported: Math.floor(Math.random() * 200) + 100,
    reportingPct: Math.floor(Math.random() * 40) + 40,
    results: {
      'Candidate A': Math.floor(Math.random() * 500000),
      'Candidate B': Math.floor(Math.random() * 500000),
      'Candidate C': Math.floor(Math.random() * 100000),
    },
  }));
}

function generateSampleAlerts(): ElectionAlert[] {
  return [
    { id: '1', alertType: 'Turnout Anomaly', severity: 'high', location: 'Turkana County, Station 042', description: 'Reported turnout of 98.7% exceeds statistical expectation (expected: 65-75%)', createdAt: '2h ago' },
    { id: '2', alertType: 'Duplicate Submission', severity: 'medium', location: 'Nairobi, Kibera Station 112', description: '3 identical Form 34A images submitted from the same polling station', createdAt: '4h ago' },
    { id: '3', alertType: 'Math Inconsistency', severity: 'critical', location: 'Kisumu, Rusinga Station 007', description: 'Sum of candidate votes (45,230) does not match total votes cast (42,100)', createdAt: '5h ago' },
    { id: '4', alertType: 'Timing Anomaly', severity: 'high', location: 'Nakuru, Subukia Station 023', description: '623 votes recorded in 4 minutes — exceeds physically possible rate', createdAt: '8h ago' },
    { id: '5', alertType: 'Missing Watermark', severity: 'medium', location: 'Mombasa, Changamwe Station 088', description: 'Form 34A watermark not detected, image may be a copy', createdAt: '12h ago' },
  ];
}
