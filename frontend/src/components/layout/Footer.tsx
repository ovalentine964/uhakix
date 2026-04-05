'use client';

import React from 'react';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-400 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-white text-lg font-bold mb-3">
              <span className="text-yellow-400">U</span>JUZIO
            </h3>
            <p className="text-sm">
              Kenya&apos;s AI-powered government transparency platform.
              Built by citizens, for citizens.
            </p>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-3">Explore</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="/transparency" className="hover:text-white">Transactions</a></li>
              <li><a href="/election" className="hover:text-white">Election Results</a></li>
              <li><a href="/directory" className="hover:text-white">Entity Directory</a></li>
              <li><a href="/submit" className="hover:text-white">Report Form 34A</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-3">AI Agents</h4>
            <ul className="space-y-2 text-sm">
              <li>JASIRI — Budget Intel</li>
              <li>RIFT — Procurement</li>
              <li>SPHINX — Anomaly Detection</li>
              <li>SCOUT — Network Mapping</li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-3">Access UJUZIO</h4>
            <ul className="space-y-2 text-sm">
              <li>🌐 Web Dashboard</li>
              <li>📱 WhatsApp Bot</li>
              <li>📞 USSD *789#</li>
              <li>🔌 Open API</li>
            </ul>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-gray-800 text-center text-xs">
          <p>Data from public government sources. Connection reports only — never accusations.</p>
          <p className="mt-1">Compliant with Kenya Data Protection Act, 2019. No ID required.</p>
          <p className="mt-1">© 2024 UJUZIO. AGPL-3.0 License. Built by CoHusdex.</p>
        </div>
      </div>
    </footer>
  );
}
