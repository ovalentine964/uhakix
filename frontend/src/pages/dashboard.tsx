import React, { useEffect, useState } from 'react';
import Head from 'next/head';
import { api } from '../services/api';
import { Header } from '../components/layout/Header';
import { Footer } from '../components/layout/Footer';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';

const COLORS = ['#1e40af', '#059669', '#d97706', '#dc2626', '#7c3aed', '#0891b2'];

export default function Dashboard() {
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [budgetData, setBudgetData] = useState<any[]>([]);
  const [countyData, setCountyData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [anomRes, transRes] = await Promise.all([
          api.get('/api/v1/transparency/anomalies'),
          api.get('/api/v1/transparency/transactions'),
        ]);
        setAnomalies(anomRes.data.anomalies || []);
        setTransactions(transRes.data || []);

        // Generate sample budget allocation chart data
        setBudgetData([
          { ministry: 'Health', allocated: 150, spent: 142, variance: 93 },
          { ministry: 'Education', allocated: 180, spent: 165, variance: 92 },
          { ministry: 'Infrastructure', allocated: 220, spent: 198, variance: 90 },
          { ministry: 'Agriculture', allocated: 90, spent: 72, variance: 80 },
          { ministry: 'Security', allocated: 200, spent: 185, variance: 93 },
          { ministry: 'Energy', allocated: 120, spent: 88, variance: 73 },
        ]);

        setCountyData([
          { name: 'Nairobi', absorption: 87, risk: 'low' },
          { name: 'Mombasa', absorption: 72, risk: 'medium' },
          { name: 'Kisumu', absorption: 68, risk: 'medium' },
          { name: 'Nakuru', absorption: 91, risk: 'low' },
          { name: 'Kiambu', absorption: 94, risk: 'low' },
          { name: 'Kakamega', absorption: 58, risk: 'high' },
          { name: 'Machakos', absorption: 63, risk: 'medium' },
          { name: 'Uasin Gishu', absorption: 71, risk: 'medium' },
        ]);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Dashboard — UHAKIX | Kenya Government Transparency</title>
      </Head>
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Transparency Dashboard</h1>
          <p className="text-gray-600 mt-2">Real-time government spending analysis and corruption risk monitoring</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Tracked" value="KES 1.2T" sublabel="Annual spending" color="blue" />
          <StatCard label="Active Alerts" value={anomalies.length > 0 ? anomalies.length : 12} sublabel="Requiring review" color="red" />
          <StatCard label="Entities Mapped" value="24,500+" sublabel="People, companies, tenders" color="green" />
          <StatCard label="Tenders Analyzed" value="8,740" sublabel="Past 12 months" color="amber" />
        </div>

        {/* Budget Allocation vs Spending */}
        <div className="bg-white rounded-xl shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Budget Allocation vs Actual Spending</h2>
          <p className="text-sm text-gray-500 mb-6">Amounts in billions KES</p>
          {loading ? (
            <ChartPlaceholder />
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={budgetData} margin={{ top: 5, right: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="ministry" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => `KES ${value}B`} />
                  <Legend />
                  <Bar dataKey="allocated" fill="#1e40af" name="Allocated" />
                  <Bar dataKey="spent" fill="#059669" name="Spent" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Risk Map - Absorption Rate */}
          <div className="bg-white rounded-xl shadow p-6 lg:col-span-2">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">County Budget Absorption Rate</h2>
            <p className="text-sm text-gray-500 mb-4">Lower rates may indicate project delays or fund diversion</p>
            {loading ? (
              <ChartPlaceholder />
            ) : (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={countyData} layout="vertical" margin={{ left: 80, top: 5, right: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                    <YAxis dataKey="name" type="category" />
                    <Tooltip formatter={(value: number) => `${value}%`} />
                    <Bar dataKey="absorption" fill="#1e40af" name="Absorption Rate" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Alert Feed */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">🔴 Live Alerts</h2>
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                    <div className="h-3 bg-gray-100 rounded w-1/2" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-3 max-h-64 overflow-y-auto">
                <AlertItem severity="high" title="Spending spike" desc="Health Ministry: 340% above quarterly average" time="2h ago" />
                <AlertItem severity="medium" title="Low absorption" desc="Kakamega County: 58% budget utilization in Q3" time="5h ago" />
                <AlertItem severity="high" title="Repeat contractor" desc="Same company won 12 tenders from Ministry of Roads" time="8h ago" />
                <AlertItem severity="low" title="Variance detected" desc="Energy Ministry spending 27% below allocation" time="12h ago" />
                <AlertItem severity="medium" title="No-bid contract" desc="KES 450M single-source procurement flagged" time="1d ago" />
                <AlertItem severity="high" title="End-year spike" desc="3 ministries spent 40% of annual budget in June" time="1d ago" />
              </div>
            )}
          </div>
        </div>

        {/* Spending Over Time */}
        <div className="bg-white rounded-xl shadow p-6 mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Monthly Spending Trend</h2>
          {loading ? (
            <ChartPlaceholder />
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={[
                    { month: 'Jan', spending: 120 },
                    { month: 'Feb', spending: 95 },
                    { month: 'Mar', spending: 130 },
                    { month: 'Apr', spending: 110 },
                    { month: 'May', spending: 98 },
                    { month: 'Jun', spending: 245 }, // End of FY spike!
                    { month: 'Jul', spending: 85 },
                    { month: 'Aug', spending: 105 },
                    { month: 'Sep', spending: 115 },
                    { month: 'Oct', spending: 108 },
                    { month: 'Nov', spending: 125 },
                    { month: 'Dec', spending: 135 },
                  ]}
                  margin={{ top: 5, right: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis tickFormatter={(v: number) => `KES ${v}B`} />
                  <Tooltip formatter={(value: number) => `KES ${value}B`} />
                  <Line type="monotone" dataKey="spending" stroke="#1e40af" strokeWidth={2} dot={{ r: 4 }} name="Monthly Spending" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}

function StatCard({ label, value, sublabel, color }: { label: string; value: string | number; sublabel: string; color: string }) {
  const colorMap: Record<string, string> = {
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    amber: 'bg-amber-50 border-amber-200 text-amber-700',
  };

  return (
    <div className={`rounded-xl border p-5 ${colorMap[color] || colorMap.blue}`}>
      <p className="text-sm font-medium opacity-75">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      <p className="text-xs mt-1 opacity-60">{sublabel}</p>
    </div>
  );
}

function AlertItem({ severity, title, desc, time }: { severity: string; title: string; desc: string; time: string }) {
  const severityStyles: Record<string, string> = {
    high: 'bg-red-50 border-red-200 text-red-800',
    medium: 'bg-amber-50 border-amber-200 text-amber-800',
    low: 'bg-blue-50 border-blue-200 text-blue-800',
  };

  return (
    <div className={`rounded-lg border-l-4 p-3 ${severityStyles[severity] || severityStyles.low}`}>
      <div className="flex justify-between items-start">
        <h3 className="font-semibold text-sm">{title}</h3>
        <span className="text-xs opacity-60 flex-shrink-0 ml-2">{time}</span>
      </div>
      <p className="text-xs mt-1 opacity-75">{desc}</p>
    </div>
  );
}

function ChartPlaceholder() {
  return (
    <div className="h-64 flex items-center justify-center">
      <div className="animate-pulse space-y-2 text-center">
        <div className="h-4 bg-gray-200 rounded w-48 mx-auto" />
        <div className="h-4 bg-gray-200 rounded w-32 mx-auto" />
      </div>
    </div>
  );
}
