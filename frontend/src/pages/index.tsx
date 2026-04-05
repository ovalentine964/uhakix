import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Header } from '../components/layout/Header';
import { Footer } from '../components/layout/Footer';

const SECTORS = [
  { name: 'Health', icon: '🏥', desc: 'Hospital budgets, NHIF payments, medical procurement', risk: 'Medium', spending: 'KES 243B' },
  { name: 'Education', icon: '🎓', desc: 'School capitation, university funds, teacher payrolls', risk: 'Medium', spending: 'KES 654B' },
  { name: 'Infrastructure', icon: '🛣️', desc: 'Roads, bridges, public works contracts', risk: 'High', spending: 'KES 387B' },
  { name: 'Security', icon: '🛡️', desc: 'Police, military spending, classified procurement', risk: 'High', spending: 'KES 235B' },
  { name: 'Agriculture', icon: '🌾', desc: 'Subsidies, fertilizer procurement, extension services', risk: 'Medium', spending: 'KES 94B' },
  { name: 'Energy', icon: '⚡', desc: 'Electrification projects, geothermal, IPP payments', risk: 'Low', spending: 'KES 156B' },
  { name: 'Water', icon: '💧', desc: 'Boreholes, water treatment, county water projects', risk: 'Medium', spending: 'KES 45B' },
  { name: 'CDF', icon: '💰', desc: 'Constituency Development Fund usage and projects', risk: 'High', spending: 'KES 33B' },
];

const AGENTS = [
  { name: 'JASIRI', role: 'Budget Intel', icon: '📊', model: 'Nemotron-4', desc: 'Analyzes budget vs spending' },
  { name: 'RIFT', role: 'Procurement', icon: '📋', model: 'Nemotron-4', desc: 'Tender analysis & bid rigging detection' },
  { name: 'SPHINX', role: 'Anomaly Detection', icon: '🔍', model: 'Nemotron-4', desc: 'Statistical outlier detection' },
  { name: 'SCOUT', role: 'Network Mapping', icon: '🕸️', model: 'Llama-3 70B', desc: 'Entity relationship discovery' },
  { name: 'POLL WITNESS', role: 'Election OCR', icon: '🗳️', model: 'Llama Vision', desc: 'Form 34A extraction' },
  { name: 'SHIELD', role: 'Compliance', icon: '🛡️', model: 'Nemotron-4', desc: 'Legal review & redaction' },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>UHAKIX — Kenya's Government Transparency Platform</title>
        <meta name="description" content="AI-powered government transparency and electoral accountability platform" />
      </Head>
      <Header />

      {/* Hero */}
      <section className="bg-gradient-to-br from-blue-900 via-blue-800 to-green-800 text-white py-20">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <div className="inline-block px-4 py-1 bg-white/10 rounded-full text-sm mb-6 backdrop-blur-sm">
            <span className="mr-2">🇰🇪</span> Built in Kenya, for Kenya
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
            Every Shilling<br />Every Vote<br /><span className="text-green-400">Every Voice</span>
          </h1>
          <p className="text-xl text-blue-100 max-w-2xl mx-auto mb-10">
            AI-powered transparency. No ID required. Speak in Swahili, English, or Sheng.
            Track where your taxes go and verify election results yourself.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/dashboard" className="px-8 py-4 bg-white text-blue-900 rounded-xl font-bold text-lg hover:bg-blue-50 transition-colors shadow-lg">
              Open Dashboard
            </Link>
            <Link href="/submit" className="px-8 py-4 bg-transparent border-2 border-white text-white rounded-xl font-bold text-lg hover:bg-white/10 transition-colors">
              Submit Evidence
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="max-w-6xl mx-auto px-4 -mt-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'KES Tracked', value: '1.2T' },
            { label: 'Government Entities', value: '24,500+' },
            { label: 'Counties Monitored', value: '47/47' },
            { label: 'AI Agents Active', value: '14' },
          ].map(s => (
            <div key={s.label} className="bg-white rounded-xl shadow-lg p-6 text-center">
              <p className="text-2xl md:text-3xl font-bold text-blue-900">{s.value}</p>
              <p className="text-sm text-gray-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">How UHAKIX Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <StepCard number="1" icon="📥" title="Citizens Report" desc="Upload Form 34A photos, tip about irregularities, or just ask questions. No identity required. By voice, USSD, WhatsApp, or web." />
          <StepCard number="2" icon="🤖" title="AI Agents Verify" desc="14 specialized agents cross-reference, analyze, and validate. Every claim checked against 3+ sources before publication." />
          <StepCard number="3" icon="⛓️" title="Blockchain Records" desc="Verified data is hashed to Polygon blockchain — tamper-proof. Anyone can verify the integrity of reports months or years later." />
        </div>
      </section>

      {/* AI Agent Team */}
      <section className="bg-white py-16">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">The Agent Team</h2>
          <p className="text-center text-gray-600 mb-12">14 specialized AI agents working together for transparency</p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {AGENTS.map(agent => (
              <div key={agent.name} className="bg-gray-50 rounded-xl p-4 text-center hover:shadow-md transition-shadow">
                <p className="text-3xl mb-2">{agent.icon}</p>
                <p className="font-bold text-sm text-gray-900">{agent.name}</p>
                <p className="text-xs text-gray-500">{agent.role}</p>
                <p className="text-xs text-blue-600 mt-1">{agent.model}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Sector Cards */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">Sector Transparency</h2>
        <p className="text-center text-gray-600 mb-12">Real-time monitoring of government spending across sectors</p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {SECTORS.map(sector => (
            <Link href="/dashboard" key={sector.name} className="bg-white rounded-xl shadow p-5 hover:shadow-md transition-shadow block group">
              <div className="flex items-center justify-between mb-3">
                <span className="text-3xl">{sector.icon}</span>
                <RiskBadge level={sector.risk} />
              </div>
              <h3 className="font-bold text-gray-900 group-hover:text-blue-700 transition-colors">{sector.name}</h3>
              <p className="text-xs text-gray-500 mt-1">{sector.desc}</p>
              <div className="mt-3 flex justify-between items-center">
                <span className="text-sm font-semibold text-blue-900">{sector.spending}</span>
                <span className="text-xs text-gray-400">Tracked</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Election Verification CTA */}
      <section className="bg-gradient-to-r from-green-700 to-green-900 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Verify Election Results Yourself</h2>
          <p className="text-lg text-green-100 mb-8">
            Don't rely on official announcements. Upload Form 34A photos from your polling station.
            Our AI cross-verifies with other submissions and stores results on blockchain.
          </p>
          <Link href="/submit" className="inline-block px-8 py-4 bg-white text-green-900 rounded-xl font-bold text-lg hover:bg-green-50 transition-colors">
            Submit Form 34A
          </Link>
        </div>
      </section>

      {/* Citizen Voice CTA */}
      <section className="bg-gradient-to-r from-amber-500 to-orange-600 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">🎤 Speak in Your Language</h2>
          <p className="text-lg text-amber-100 mb-8">
            Ask UHAKIX about government spending in Swahili, English, or Sheng. Use voice, USSD, or WhatsApp.
            Our AI understands Kenyan context.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/citizen" className="px-6 py-3 bg-white text-orange-700 rounded-xl font-semibold hover:bg-orange-50 transition-colors">
              Ask a Question
            </Link>
            <p className="text-white text-sm flex items-center">Works via: Web · WhatsApp · USSD *247# · Telegram</p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

function StepCard({ number, icon, title, desc }: { number: string; icon: string; title: string; desc: string }) {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-3xl">{icon}</span>
      </div>
      <div className="inline-block px-2 py-0.5 bg-blue-600 text-white rounded-full text-xs font-bold mb-3">STEP {number}</div>
      <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{desc}</p>
      {parseInt(number) < 3 && <div className="text-blue-300 text-2xl mt-4 hidden md:block">→</div>}
    </div>
  );
}

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    High: 'bg-red-100 text-red-800',
    Medium: 'bg-amber-100 text-amber-800',
    Low: 'bg-green-100 text-green-800',
  };
  return <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[level] || ''}`} >{level} Risk</span>;
}
