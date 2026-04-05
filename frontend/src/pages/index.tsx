'use client';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gray-50">
      {/* Hero */}
      <section className="bg-gradient-to-br from-green-900 to-green-700 text-white py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            <span className="text-yellow-400">U</span>JUZIO
          </h1>
          <p className="text-xl md:text-2xl mb-4 text-green-100">
            Kenya&apos;s AI-Powered Government Transparency Platform
          </p>
          <p className="text-lg mb-8 text-green-200 max-w-2xl mx-auto">
            Track every shilling. Verify every vote. Know your government.
            No ID required. Built for every Kenyan.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <a href="/transparency" className="bg-yellow-400 text-green-900 px-8 py-3 rounded-lg font-bold hover:bg-yellow-300 transition">
              Track Spending
            </a>
            <a href="/election" className="bg-white text-green-900 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition">
              Election Results
            </a>
            <a href="/submit" className="border-2 border-white text-white px-8 py-3 rounded-lg font-bold hover:bg-white hover:text-green-900 transition">
              Report Form 34A
            </a>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12">
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <StatCard number="KES 1T+" label="Tracked Annually" />
            <StatCard number="47" label="Counties Covered" />
            <StatCard number="10" label="AI Agents Active" />
            <StatCard number="0" label="ID Required" />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            How UHAKIX Works
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon="🤖"
              title="AI Agents Analyze"
              description="10 specialized AI agents (using NVIDIA models) scan government data, detect anomalies, and map connections"
            />
            <FeatureCard
              icon="📊"
              title="Data You Can Trust"
              description="All verified data is hashed to Polygon blockchain — immutable, publicly verifiable, cannot be tampered"
            />
            <FeatureCard
              icon="📱"
              title="Access Anywhere"
              description="Web dashboard, WhatsApp bot, USSD *789#, or open API. No ID required. Swahili and English."
            />
          </div>
        </div>
      </section>

      {/* Access Channels */}
      <section className="py-16 bg-gray-100">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-8 text-gray-900">Access UHAKIX Your Way</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <AccessCard emoji="🌐" title="Web Dashboard" desc="Full data exploration" />
            <AccessCard emoji="📱" title="WhatsApp Bot" desc="Chat + photo uploads" />
            <AccessCard emoji="📞" title="USSD *789#" desc="Feature phone access" />
            <AccessCard emoji="🔌" title="Open API" desc="Build on our data" />
          </div>
        </div>
      </section>

      {/* AI Agent Showcase */}
      <section className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            Meet the Agent Team
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {agents.map((agent) => (
              <div key={agent.name} className="text-center p-4 border rounded-lg hover:shadow-md transition">
                <div className="text-3xl mb-2">{agent.icon}</div>
                <h3 className="font-bold text-sm">{agent.name}</h3>
                <p className="text-xs text-gray-500 mt-1">{agent.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

function StatCard({ number, label }: { number: string; label: string }) {
  return (
    <div className="bg-green-50 p-6 rounded-xl text-center">
      <div className="text-3xl font-bold text-green-900">{number}</div>
      <div className="text-sm text-green-700 mt-1">{label}</div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="text-5xl mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-2 text-gray-900">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}

function AccessCard({ emoji, title, desc }: { emoji: string; title: string; desc: string }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm">
      <div className="text-3xl mb-2">{emoji}</div>
      <h3 className="font-bold">{title}</h3>
      <p className="text-sm text-gray-500">{desc}</p>
    </div>
  );
}

const agents = [
  { name: 'JASIRI', role: 'Budget Intel', icon: '💰' },
  { name: 'RIFT', role: 'Procurement', icon: '🔍' },
  { name: 'SPHINX', role: 'Anomaly', icon: '🧩' },
  { name: 'SCOUT', role: 'Network', icon: '🕸️' },
  { name: 'HERALD', role: 'Citizen Voice', icon: '📢' },
  { name: 'SHIELD', role: 'Legal Guard', icon: '🛡️' },
  { name: 'KAZI', role: 'Orchestrator', icon: '⚡' },
  { name: 'VIGIL', role: 'Audit Trail', icon: '👁️' },
  { name: 'ATLAS', role: 'Geographic', icon: '🗺️' },
  { name: 'LEDGER', role: 'Blockchain', icon: '⛓️' },
];
